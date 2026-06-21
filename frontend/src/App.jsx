import { useCallback, useEffect, useState } from "react";
import { fetchGapMap } from "./api.js";
import { useAnalysisSocket } from "./useAnalysisSocket.js";
import CognitiveGapMap from "./components/CognitiveGapMap.jsx";
import AnswerSubmitForm from "./components/AnswerSubmitForm.jsx";
import LiveAnalysisFeed from "./components/LiveAnalysisFeed.jsx";
import "./styles/app.css";

const DEFAULT_STUDENT_ID = "demo_student_01";

export default function App() {
  const [studentId] = useState(DEFAULT_STUDENT_ID);
  const [gapMap, setGapMap] = useState({ nodes: [], edges: [] });

  const refreshGapMap = useCallback(async () => {
    const data = await fetchGapMap(studentId);
    setGapMap(data);
  }, [studentId]);

  useEffect(() => {
    refreshGapMap();
  }, [refreshGapMap]);

  const { isAnalyzing, liveText, error } = useAnalysisSocket(studentId, () => {
    refreshGapMap();
  });

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>ECHOFORGE</h1>
        <p className="app-subtitle">NEXUS Cognitive Memory Engine — student: {studentId}</p>
      </header>

      <main className="app-main">
        <CognitiveGapMap nodes={gapMap.nodes} edges={gapMap.edges} />

        <LiveAnalysisFeed isAnalyzing={isAnalyzing} liveText={liveText} error={error} />

        <section className="answer-section">
          <h2>Submit a new answer</h2>
          <AnswerSubmitForm studentId={studentId} onSubmitted={refreshGapMap} />
        </section>
      </main>
    </div>
  );
}