"""
Entry point. Run with: uvicorn app.main:app --reload

Routes:
  POST /api/answers                       submit one answer
  GET  /api/students/{student_id}/history raw list of past answers
  GET  /api/students/{student_id}/gap-map nodes + edges for the dashboard
  WS   /ws/{student_id}                   live stream of root-cause analysis
"""
import asyncio

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.models import Answer, AnswerIn, GapMapEdge, GapMapNode, GapMapResponse
from app.memory_store import get_student_history, query_related_mistakes, store_answer
from app.root_cause_engine import streaming_root_cause_analysis
from app.websocket_manager import manager
from app.curriculum_standards import list_concepts
from app.cluster_store import load_clusters, save_clusters

app = FastAPI(title="ECHOFORGE")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server default
    allow_methods=["*"],
    allow_headers=["*"],
)

# Loaded from disk now instead of starting empty every restart.
_clusters_by_student: dict[str, list[dict]] = load_clusters()


@app.post("/api/answers")
async def submit_answer(payload: AnswerIn):
    answer = Answer(**payload.model_dump())
    store_answer(answer)

    related = query_related_mistakes(answer)
    pattern_found = len(related) > 0

    if pattern_found:
        # Don't make the HTTP request wait for the LLM — stream the
        # explanation over the WebSocket instead, fire-and-forget.
        asyncio.create_task(_analyze_and_broadcast(answer, related))

    return {
        "answer_id": answer.answer_id,
        "stored": True,
        "pattern_found": pattern_found,
        "related_count": len(related),
    }


async def _analyze_and_broadcast(answer: Answer, related: list) -> None:
    await manager.send_event(
        answer.student_id,
        {"type": "analysis_started", "trigger_answer_id": answer.answer_id},
    )

    try:
        full_text = ""
        async for chunk in streaming_root_cause_analysis(answer, related):
            full_text += chunk
            await manager.send_event(
                answer.student_id, {"type": "analysis_chunk", "text": chunk}
            )
    except Exception as exc:
        # Without this, a bad/missing API key fails INSIDE this background
        # task and the frontend just sits on "analyzing..." forever with
        # no error, no explanation. Surface it instead — this exact bug
        # cost real debugging time once already.
        await manager.send_event(
            answer.student_id,
            {"type": "analysis_error", "message": f"{type(exc).__name__}: {exc}"},
        )
        return

    summary, _, explanation = full_text.partition("---")

    cluster = {
        "trigger_answer_id": answer.answer_id,
        "related_answer_ids": [m.answer_id for m in related],
        "root_cause_summary": summary.strip(),
        "explanation": explanation.strip(),
        "reviewed": False,
    }
    _clusters_by_student.setdefault(answer.student_id, []).append(cluster)
    save_clusters(_clusters_by_student)

    await manager.send_event(
        answer.student_id, {"type": "analysis_complete", "cluster": cluster}
    )


@app.post("/api/students/{student_id}/clusters/{trigger_answer_id}/review")
async def review_cluster(student_id: str, trigger_answer_id: str):
    """
    The actual human-in-the-loop action: a teacher confirming an
    AI-discovered diagnosis. Without this endpoint, "a teacher should be
    able to review this" was just a sentence in a script, not something
    the running app could do.
    """
    clusters = _clusters_by_student.get(student_id, [])
    for cluster in clusters:
        if cluster["trigger_answer_id"] == trigger_answer_id:
            cluster["reviewed"] = True
            save_clusters(_clusters_by_student)
            return {"trigger_answer_id": trigger_answer_id, "reviewed": True}
    raise HTTPException(status_code=404, detail="Cluster not found")


@app.get("/api/concepts")
async def concepts():
    """
    The real curriculum taxonomy, served so the frontend dropdown always
    matches the backend exactly — there's only ever one source of truth,
    curriculum_standards.py.
    """
    return list_concepts()


@app.get("/api/students/{student_id}/history")
async def history(student_id: str):
    return get_student_history(student_id)


@app.get("/api/students/{student_id}/gap-map", response_model=GapMapResponse)
async def gap_map(student_id: str):
    raw_history = get_student_history(student_id)
    nodes = [
        GapMapNode(
            answer_id=item["answer_id"],
            subject=item["subject"],
            concept_key=item["concept_key"],
            standard_code=item["standard_code"],
            question_text=item["question_text"],
            student_answer=item.get("student_answer", "(not recorded)"),
            correct_answer=item.get("correct_answer", "(not recorded)"),
            is_correct=item["is_correct"],
            timestamp=item["timestamp"],
        )
        for item in raw_history
    ]

    edges: list[GapMapEdge] = []
    for cluster in _clusters_by_student.get(student_id, []):
        for related_id in cluster["related_answer_ids"]:
            edges.append(
                GapMapEdge(
                    source_id=cluster["trigger_answer_id"],
                    target_id=related_id,
                    root_cause_summary=cluster["root_cause_summary"],
                    trigger_answer_id=cluster["trigger_answer_id"],
                    reviewed=cluster.get("reviewed", False),
                )
            )

    return GapMapResponse(nodes=nodes, edges=edges)


@app.websocket("/ws/{student_id}")
async def websocket_endpoint(websocket: WebSocket, student_id: str):
    await manager.connect(student_id, websocket)
    try:
        while True:
            # We don't expect the client to send anything — this just
            # keeps the connection open so manager.send_event() can push to it.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(student_id)
