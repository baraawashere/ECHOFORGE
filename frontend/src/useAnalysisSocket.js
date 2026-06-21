import { useEffect, useRef, useState } from "react";
import { WS_BASE_URL } from "./api.js";

export function useAnalysisSocket(studentId, onClusterComplete) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [liveText, setLiveText] = useState("");
  const [error, setError] = useState(null);
  const socketRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const isMountedRef = useRef(true);

  useEffect(() => {
    if (!studentId) return;
    isMountedRef.current = true;

    function connect() {
      const socket = new WebSocket(`${WS_BASE_URL}/ws/${studentId}`);
      socketRef.current = socket;

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "analysis_started") {
          setIsAnalyzing(true);
          setLiveText("");
          setError(null);
        } else if (data.type === "analysis_chunk") {
          setLiveText((prev) => prev + data.text);
        } else if (data.type === "analysis_complete") {
          setIsAnalyzing(false);
          onClusterComplete?.(data.cluster);
        } else if (data.type === "analysis_error") {
          setIsAnalyzing(false);
          setError(data.message);
        }
      };

      socket.onerror = (err) => {
        console.error("ECHOFORGE socket error", err);
      };

      socket.onclose = () => {
        if (isMountedRef.current) {
          reconnectTimerRef.current = setTimeout(connect, 2000);
        }
      };
    }

    connect();

    return () => {
      isMountedRef.current = false;
      clearTimeout(reconnectTimerRef.current);
      socketRef.current?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [studentId]);

  return { isAnalyzing, liveText, error };
}