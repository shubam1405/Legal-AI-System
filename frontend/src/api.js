const API_BASE = "http://localhost:8001";

export async function sendMessage(query, threadId) {
  const params = new URLSearchParams({ query, thread_id: threadId });
  const res = await fetch(`${API_BASE}/chat?${params}`, { method: "POST" });
  if (!res.ok) throw new Error(`Server error: ${res.status}`);
  return res.json();
}

export async function uploadCase(file, threadId) {
  const form = new FormData();
  form.append("file", file);
  const params = new URLSearchParams({ thread_id: threadId });
  const res = await fetch(`${API_BASE}/upload-case?${params}`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
  return res.json();
}
