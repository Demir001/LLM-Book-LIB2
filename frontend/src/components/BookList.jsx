import React, { useEffect, useState } from "react";
import { fetchBooks } from "../api/client";

export default function BookList({ onSelectBook }) {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // PDF / kitap listesini backend'den çek
  const loadBooks = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchBooks();
      setBooks(data || []);
    } catch (err) {
      console.error("Kitaplar yüklenirken hata:", err);
      setError("Kitaplar yüklenemedi.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBooks();
  }, []);

  if (loading) return <div>📚 Kitaplar yükleniyor...</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;
  if (books.length === 0) return <div>📭 Kütüphanede henüz kitap yok.</div>;

  return (
    <div className="book-list">
      <h3>📖 Kütüphanedeki Kitaplar</h3>
      <ul>
        {books.map((book, index) => (
          <li key={index}>
            <button
              onClick={() => onSelectBook(book)}
              className="book-item-btn"
            >
              {book.title || book.name || `Kitap ${index + 1}`}
            </button>
          </li>
        ))}
      </ul>
      <button onClick={loadBooks} className="refresh-btn">
        🔄 Yenile
      </button>
    </div>
  );
}