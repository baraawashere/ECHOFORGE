import { useEffect, useRef, useState } from "react";
import "./CognitiveGapMap.css";

const SUBJECT_COLORS = {
  math: "var(--math)",
  physics: "var(--physics)",
  chemistry: "var(--chemistry)",
  biology: "var(--biology)",
};

function colorFor(subject) {
  return SUBJECT_COLORS[subject?.toLowerCase()] || "var(--default-subject)";
}

function edgeKey(edge) {
  return `${edge.source_id}::${edge.target_id}`;
}

/**
 * Renders mistakes on a horizontal timeline, one lane per subject —
 * because the entire point of ECHOFORGE is that the gap PERSISTS
 * ACROSS TIME, the x-axis being literal time is the most honest way
 * to show that, not a generic force-directed blob.
 *
 * Day 3 additions:
 * - New edges draw themselves in with a stroke animation instead of
 *   just popping into existence (see "justAppeared" below)
 * - The two nodes an edge connects pulse briefly when it's new
 * - Clicking any node opens a detail panel with the real question
 */
export default function CognitiveGapMap({ nodes, edges }) {
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [justAppearedKeys, setJustAppearedKeys] = useState(new Set());
  const seenEdgeKeysRef = useRef(new Set());

  useEffect(() => {
    const currentKeys = new Set((edges || []).map(edgeKey));
    const newlyAppeared = new Set();

    for (const key of currentKeys) {
      if (!seenEdgeKeysRef.current.has(key)) {
        newlyAppeared.add(key);
      }
    }

    if (newlyAppeared.size > 0) {
      setJustAppearedKeys(newlyAppeared);
      // After the draw-in + pulse animations finish, drop back to the
      // plain static render so refreshing the page later doesn't
      // replay the animation for edges that aren't actually new.
      const timer = setTimeout(() => setJustAppearedKeys(new Set()), 1400);
      seenEdgeKeysRef.current = currentKeys;
      return () => clearTimeout(timer);
    }

    seenEdgeKeysRef.current = currentKeys;
  }, [edges]);

  if (!nodes || nodes.length === 0) {
    return (
      <div className="gap-map-empty">
        No mistakes recorded yet for this student. Submit one below to begin.
      </div>
    );
  }

  const width = 900;
  const padding = 60;
  const laneHeight = 70;
  const topMargin = 140;
  const maxArcHeight = topMargin - 20;

  const subjects = [...new Set(nodes.map((n) => n.subject))];
  const height = topMargin + subjects.length * laneHeight + 40;
  const laneY = (subject) =>
    topMargin + subjects.indexOf(subject) * laneHeight + laneHeight / 2;

  const times = nodes.map((n) => new Date(n.timestamp).getTime());
  const minTime = Math.min(...times);
  const maxTime = Math.max(...times);
  const span = Math.max(maxTime - minTime, 1);

  const positionX = (timestamp) => {
    const t = new Date(timestamp).getTime();
    const ratio = (t - minTime) / span;
    return padding + ratio * (width - padding * 2);
  };

  const nodeById = Object.fromEntries(nodes.map((n) => [n.answer_id, n]));

  // Which node ids belong to an edge that just appeared — these get
  // the pulsing-ring treatment for a moment.
  const pulsingNodeIds = new Set();
  for (const edge of edges || []) {
    if (justAppearedKeys.has(edgeKey(edge))) {
      pulsingNodeIds.add(edge.source_id);
      pulsingNodeIds.add(edge.target_id);
    }
  }

  const selectedNode = selectedNodeId ? nodeById[selectedNodeId] : null;

  return (
    <div className="gap-map">
      <svg viewBox={`0 0 ${width} ${height}`} className="gap-map-svg">
        {subjects.map((subject) => (
          <g key={subject}>
            <text x={8} y={laneY(subject) + 4} className="lane-label" fill={colorFor(subject)}>
              {subject}
            </text>
            <line
              x1={padding}
              x2={width - padding}
              y1={laneY(subject)}
              y2={laneY(subject)}
              className="lane-line"
            />
          </g>
        ))}

        {edges?.map((edge, i) => {
          const a = nodeById[edge.source_id];
          const b = nodeById[edge.target_id];
          if (!a || !b) return null;

          const x1 = positionX(a.timestamp);
          const y1 = laneY(a.subject);
          const x2 = positionX(b.timestamp);
          const y2 = laneY(b.subject);
          const midX = (x1 + x2) / 2;
          const arcHeight = Math.min(Math.abs(x1 - x2) * 0.4, maxArcHeight);
          const isNew = justAppearedKeys.has(edgeKey(edge));
          const baseClass = edge.reviewed ? "gap-edge" : "gap-edge-pending";
          const className = isNew ? `${baseClass} gap-edge-drawing` : baseClass;

          return (
            <path
              key={i}
              d={`M ${x1} ${y1} Q ${midX} ${Math.min(y1, y2) - arcHeight} ${x2} ${y2}`}
              className={className}
              pathLength="1"
            >
              <title>
                {edge.root_cause_summary}
                {edge.reviewed ? " (reviewed)" : " (pending teacher review)"}
              </title>
            </path>
          );
        })}

        {nodes.map((node) => {
          const cx = positionX(node.timestamp);
          const cy = laneY(node.subject);
          const isPulsing = pulsingNodeIds.has(node.answer_id);
          const isSelected = node.answer_id === selectedNodeId;

          return (
            <g key={node.answer_id}>
              {isPulsing && (
                <circle cx={cx} cy={cy} r={9} className="node-pulse-ring" style={{ stroke: colorFor(node.subject) }} />
              )}
              <circle
                cx={cx}
                cy={cy}
                r={node.is_correct ? 6 : 9}
                className={
                  (node.is_correct ? "node-correct" : "node-wrong") +
                  (isSelected ? " node-selected" : "")
                }
                style={{ stroke: colorFor(node.subject), cursor: "pointer" }}
                onClick={() => setSelectedNodeId(isSelected ? null : node.answer_id)}
              >
                <title>{`${node.standard_code} (${node.is_correct ? "correct" : "wrong"}) — click for detail`}</title>
              </circle>
            </g>
          );
        })}
      </svg>

      {selectedNode && (
        <div className="node-detail-panel">
          <div className="node-detail-header">
            <span style={{ color: colorFor(selectedNode.subject) }}>
              {selectedNode.standard_code}
            </span>
            <button className="node-detail-close" onClick={() => setSelectedNodeId(null)}>
              ✕
            </button>
          </div>
          <p className="node-detail-question">{selectedNode.question_text}</p>
          <div className="node-detail-answers">
            <div className={selectedNode.is_correct ? "answer-correct" : "answer-wrong"}>
              Student answered: {selectedNode.student_answer}
            </div>
            {!selectedNode.is_correct && (
              <div className="answer-correct">Correct: {selectedNode.correct_answer}</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
