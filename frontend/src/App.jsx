import React, { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import PDFUploader from "./components/PDFUploader";
import BookList from "./components/BookList";
import { ApiClient } from "./api/client";

const api = new ApiClient();

function App() {
  const [books, setBooks] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  // PDF yükleme callback
  const handleUpload = async (files) => {
    setLoading(true);
    try {
      await api.uploadPDFs(files);
      const updatedBooks = await api.getBooks();
      setBooks(updatedBooks);
    } catch (err) {
      console.error("PDF yükleme hatası:", err);
    } finally {
      setLoading(false);
    }
  };

  // Soru gönderme callback
  const handleSendMessage = async (question) => {
    if (!question.trim()) return;
    setMessages((prev) => [...prev, { user: "You", text: question }]);
    try {
      const answer = await api.askQuestion(question);
      setMessages((prev) => [...prev, { user: "RAG", text: answer }]);
    } catch (err) {
      setMessages((prev) => [...prev, { user: "System", text: "Hata: " + err.message }]);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <header className="bg-blue-600 text-white p-4 text-center font-bold text-xl">
        Advanced RAG System
      </header>

      <main className="flex flex-1 p-4 gap-4">
        <div className="w-2/3 flex flex-col gap-4">
          <PDFUploader onUpload={handleUpload} />
          <ChatWindow messages={messages} onSend={handleSendMessage} loading={loading} />
        </div>
        <div className="w-1/3">
          <BookList books={books} />
        </div>
      </main>

      <footer className="bg-gray-200 p-2 text-center text-sm">
        &copy; 2025 Advanced RAG System
      </footer>
    </div>
  );
}

export default App;