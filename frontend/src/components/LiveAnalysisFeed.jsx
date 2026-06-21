import { useEffect, useState } from "react";
import { reviewCluster } from "../api.js";

export default function LiveAnalysisFeed({
  isAnalyzing,
  liveText,
  error,
  studentId,
  cluster,
  onReviewed,
}) {
  const [approving, setApproving] = useState(false);
  const [justApproved, setJustApproved] = useState(false);

  // Reset the local "just approved" flag whenever a genuinely new
  // cluster comes in, so it doesn't carry over from the previous one.
  useEffect(() => {
    setJustApproved(false);
  }, [cluster?.trigger_answer_id]);

  if (!isAnalyzing && !liveText && !error) return null;

  if (error) {
    return (
      <div className="analysis-feed analysis-feed-error">
        <div className="analysis-feed-label">Analysis failed</div>
        <p className="analysis-feed-text">{error}</p>
      </div>
    );
  }

  const [summary, explanation] = liveText.split("---");

  async function handleApprove() {
    if (!cluster) return;
    setApproving(true);
    try {
      await reviewCluster(studentId, cluster.trigger_answer_id);
      setJustApproved(true);
      onReviewed?.();
    } finally {
      setApproving(false);
    }
  }

  // The actual human-in-the-loop moment: the AI's diagnosis sits here
  // unconfirmed until a teacher clicks Approve. Until then it's
  // genuinely just a suggestion, not a final answer.
  const isReviewed = Boolean(cluster?.reviewed) || justApproved;
  const showApproveButton = !isAnalyzing && cluster && !isReviewed;
  const showReviewedBadge = !isAnalyzing && cluster && isReviewed;

  return (
    <div className="analysis-feed">
      <div className="analysis-feed-label">
        {isAnalyzing ? "ECHOFORGE is analyzing..." : "Root cause found"}
      </div>
      {summary && <p className="analysis-feed-summary">{summary.trim()}</p>}
      {explanation && <p className="analysis-feed-text">{explanation.trim()}</p>}

      {showApproveButton && (
        <button className="approve-button" onClick={handleApprove} disabled={approving}>
          {approving ? "Approving..." : "Approve this diagnosis"}
        </button>
      )}
      {showReviewedBadge && <div className="reviewed-badge">✓ Reviewed and approved</div>}
    </div>
  );
}
