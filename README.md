# ECHOFORGE — Cognitive Memory Engine for Student Mistakes

Built for the USAII Global AI Hackathon 2026.

Every tutoring tool today treats mistakes as isolated events: get a question
wrong, get corrected, move on. None of them ask whether a mistake made this
week is secretly the same misunderstanding as a mistake made two weeks ago
in a completely different subject.

ECHOFORGE does. It remembers every mistake a student has ever made, searches
across that history for mistakes that share a root cause even across
subjects, and asks an LLM to explain that root cause in plain language —
live, on a dashboard.



## How it works

1. A student submits an answer 
2. The answer is embedded (Sentence-Transformers) and stored in ChromaDB,
   tagged with the real Common Core standard it falls under
3. If the answer is wrong, the backend searches that same student's other
   wrong answers for ones that are semantically close, even across subjects
4. If related mistakes are found, they're sent to Claude (`claude-sonnet-4-6`),
   which is asked to identify the one misconception connecting them
5. The explanation streams token-by-token over a WebSocket to the React
   dashboard, which draws the connection live on the Cognitive Gap Map


## Known limitations / what's next

ECHOFORGE currently stops at identifying the root cause — it doesn't yet
generate a follow-up question targeting that misconception, which is the
natural next step. Teacher review is built in (connections start unreviewed
and require approval), but a fuller workflow before a diagnosis reaches a
student is still on the roadmap.


## IMPORTANT: THIS PROJECT REQUIRES A CLAUDE OR A GROQ API KEY TO FUNCTION