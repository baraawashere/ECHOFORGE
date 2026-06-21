export default function LiveAnalysisFeed({ isAnalyzing, liveText, error }) {
  if (!isAnalyzing && !liveText && !error) return null;

  if (error) {
    return (
      <div className="analysis-feed analysis-feed-error">
        <div className="analysis-feed-label">Analysis failed</div>
        <p className="analysis-feed-text">{error}</p>
      </div>
    );
  }

  return (
    <div className="analysis-feed">
      <div className="analysis-feed-label">
        {isAnalyzing ? "ECHOFORGE is analyzing..." : "Root cause found"}
      </div>
      <p className="analysis-feed-text">{liveText}</p>
    </div>
  );
}