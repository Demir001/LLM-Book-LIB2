const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

/**
 * PDF dosyasını backend’e yükler
 * @param {File} file - PDF dosyası
 * @returns {Promise<Object>} - Yükleme sonucu
 */
export async function uploadPDF(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
  return await res.json();
}

/**
 * Soru sorar ve RAG cevabını döndürür
 * @param {string} question - Kullanıcı sorusu
 * @returns {Promise<Object>} - Cevap ve metadata
 */
export async function askQuestion(question) {
  const res = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: question }),
  });

  if (!res.ok) throw new Error(`Query failed: ${res.statusText}`);
  return await res.json();
}

/**
 * Kütüphanedeki PDF listesini alır
 * @returns {Promise<Array>} - PDF dosya isimleri
 */
export async function fetchPDFList() {
  const res = await fetch(`${API_BASE}/pdfs`);
  if (!res.ok) throw new Error(`Fetch PDF list failed: ${res.statusText}`);
  return await res.json();
}

/**
 * Kullanıcıyı backend’e kaydeder veya oturum başlatır
 * @param {string} userId
 * @returns {Promise<Object>}
 */
export async function initUserSession(userId) {
  const res = await fetch(`${API_BASE}/session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId }),
  });
  if (!res.ok) throw new Error(`Session init failed: ${res.statusText}`);
  return await res.json();
}

/**
 * Streaming cevapları alır (WebSocket / SSE)
 * @param {string} question
 * @param {function(string)} onMessage - Her mesaj geldiğinde çağrılır
 * @param {function()} onComplete - Stream tamamlandığında çağrılır
 */
export function streamAnswer(question, onMessage, onComplete) {
  const ws = new WebSocket(`${API_BASE.replace(/^http/, "ws")}/stream`);
  ws.onopen = () => {
    ws.send(JSON.stringify({ query: question }));
  };
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.chunk) onMessage(data.chunk);
    if (data.done) {
      ws.close();
      onComplete();
    }
  };
  ws.onerror = (err) => {
    console.error("Stream error:", err);
    ws.close();
  };
}