# ECHOFORGE — Cognitive Memory Engine for Student Mistakes

Built for the USAII Global AI Hackathon 2026.

Every mainstream tutoring tool makes the same mistake with students: they help them solve their mistake and tell them to just study this material until it clicks. The student might get the hang of it but most of the time it doesnt work like "study material X to solve every question about this material". Tutoring tools need to know how and why the student gets questions wrong.

ECHOFORGE remembers every mistake a student has ever made, searches across that history for mistakes that share a root cause even across subjects and asks an LLM to explain that root cause in plain language all while showing everything live, on a dashboard.

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


NOTE: Every mistake is tagged with a concept_key that maps to an actual,
handverified Common Core State Standard pulled from thecorestandards.org
not an AI guess, not a free-text label someone typed in. This is what lets
two different mistakes about the same idea reliably connect, and it's what
lets us say every diagnosis is grounded in something citable.
