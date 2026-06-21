const BASE_URL = "http://localhost:8000";

export async function submitAnswer(answer) {
  const res = await fetch(`${BASE_URL}/api/answers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(answer),
  });
  if (!res.ok) throw new Error(`submitAnswer failed: ${res.status}`);
  return res.json();
}

export async function fetchConcepts() {
  const res = await fetch(`${BASE_URL}/api/concepts`);
  if (!res.ok) throw new Error(`fetchConcepts failed: ${res.status}`);
  return res.json();
}

export async function fetchGapMap(studentId) {
  const res = await fetch(`${BASE_URL}/api/students/${studentId}/gap-map`);
  if (!res.ok) throw new Error(`fetchGapMap failed: ${res.status}`);
  return res.json();
}

export async function fetchHistory(studentId) {
  const res = await fetch(`${BASE_URL}/api/students/${studentId}/history`);
  if (!res.ok) throw new Error(`fetchHistory failed: ${res.status}`);
  return res.json();
}

export async function reviewCluster(studentId, triggerAnswerId) {
  const res = await fetch(
    `${BASE_URL}/api/students/${studentId}/clusters/${triggerAnswerId}/review`,
    { method: "POST" }
  );
  if (!res.ok) throw new Error(`reviewCluster failed: ${res.status}`);
  return res.json();
}

export const WS_BASE_URL = "ws://localhost:8000";
