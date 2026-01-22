import { useState, useEffect, useRef } from "react";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [uploadError, setUploadError] = useState(false);

  const chatEndRef = useRef(null);

  // ✅ Auto-scroll to latest message (UX polish)
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // =====================
  // Ask Question (Chat)
  // =====================
  const askQuestion = async () => {
    if (!question || loading) return;

    const userMessage = { role: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);

    setQuestion("");
    setLoading(true);

    try {
      const res = await fetch(
        import.meta.env.VITE_BACKEND_URL + "/ask",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: userMessage.text }),
        }
      );

      const data = await res.json();

      const botMessage = { role: "bot", text: data.answer };
      setMessages((prev) => [...prev, botMessage]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "❌ Error connecting to backend" },
      ]);
    }

    setLoading(false);
  };

  // =====================
  // Upload PDF
  // =====================
  const uploadPDF = async () => {
    if (!file) return;

    setUploadStatus("Uploading...");
    setUploadError(false);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(
        import.meta.env.VITE_BACKEND_URL + "/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await res.json();

      if (data.message?.includes("already exists")) {
        setUploadStatus("PDF already exists ⚠️");
        setUploadError(true);
      } else if (res.ok) {
        setUploadStatus("PDF uploaded successfully ✅");
        setUploadError(false);
      } else {
        setUploadStatus("Failed to upload PDF ❌");
        setUploadError(true);
      }
    } catch {
      setUploadStatus("Error uploading PDF ❌");
      setUploadError(true);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100vw",
        backgroundColor: "#f3f4f6",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "Segoe UI, sans-serif",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "520px",
          backgroundColor: "#ffffff",
          padding: "24px",
          borderRadius: "12px",
          boxShadow: "0 10px 25px rgba(0,0,0,0.1)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <h2 style={{ textAlign: "center", marginBottom: "16px" }}>
          RAG Chatbot
        </h2>

        {/* ================= PDF Upload ================= */}
        <div style={{ marginBottom: "16px" }}>
          <label style={{ fontSize: "14px", fontWeight: "500" }}>
            Upload PDF
          </label>

          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => {
              setFile(e.target.files[0]);
              setUploadStatus("");
              setUploadError(false);
            }}
          />

          {file && (
            <div
              style={{
                marginTop: "8px",
                padding: "8px",
                backgroundColor: "#f1f5f9",
                borderRadius: "6px",
                fontSize: "13px",
                border: "1px solid #e5e7eb",
              }}
            >
              📄 <strong>{file.name}</strong>
            </div>
          )}

          <button
            onClick={uploadPDF}
            disabled={!file}
            style={{
              marginTop: "10px",
              padding: "8px",
              borderRadius: "6px",
              border: "none",
              backgroundColor: file ? "#16a34a" : "#9ca3af",
              color: "#ffffff",
              cursor: file ? "pointer" : "not-allowed",
              width: "100%",
            }}
          >
            Upload PDF
          </button>

          {uploadStatus && (
            <div
              style={{
                marginTop: "8px",
                padding: "8px",
                borderRadius: "6px",
                fontSize: "13px",
                backgroundColor: uploadError ? "#fee2e2" : "#dcfce7",
                color: uploadError ? "#991b1b" : "#166534",
                border: uploadError
                  ? "1px solid #fca5a5"
                  : "1px solid #86efac",
              }}
            >
              {uploadStatus}
            </div>
          )}
        </div>

        {/* ================= Chat Messages ================= */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            marginBottom: "12px",
            display: "flex",
            flexDirection: "column",
            gap: "10px",
          }}
        >
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                backgroundColor:
                  msg.role === "user" ? "#2563eb" : "#e5e7eb",
                color: msg.role === "user" ? "#ffffff" : "#111827",
                padding: "10px 14px",
                borderRadius: "12px",
                maxWidth: "80%",
                fontSize: "14px",
              }}
            >
              {msg.text}
            </div>
          ))}

          {loading && (
            <div
              style={{
                fontSize: "13px",
                color: "#6b7280",
                alignSelf: "flex-start",
              }}
            >
              Bot is typing...
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* ================= Input ================= */}
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
          onKeyDown={(e) => e.key === "Enter" && askQuestion()}
          disabled={loading}
          style={{
            width: "100%",
            padding: "12px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            marginBottom: "8px",
          }}
        />

        <button
          onClick={askQuestion}
          disabled={loading}
          style={{
            width: "100%",
            padding: "10px",
            borderRadius: "8px",
            border: "none",
            backgroundColor: "#2563eb",
            color: "#ffffff",
            fontSize: "15px",
          }}
        >
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default App;
