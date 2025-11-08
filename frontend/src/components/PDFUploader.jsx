import React, { useState } from "react";
import PropTypes from "prop-types";
import { uploadPDFs } from "../api/client";

const PDFUploader = ({ onUploadComplete }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files).filter(
      (file) => file.type === "application/pdf"
    );
    setSelectedFiles(files);
    setProgress(0);
    setError(null);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError("Lütfen en az bir PDF dosyası seçin.");
      return;
    }

    setUploading(true);
    setProgress(0);
    setError(null);

    try {
      // uploadPDFs fonksiyonu paralel olarak dosyaları yükler ve % progress callback verir
      await uploadPDFs(selectedFiles, (uploaded, total) => {
        setProgress(Math.round((uploaded / total) * 100));
      });
      setUploading(false);
      setSelectedFiles([]);
      setProgress(100);
      if (onUploadComplete) onUploadComplete();
    } catch (err) {
      console.error("PDF yükleme hatası:", err);
      setError("Yükleme sırasında bir hata oluştu.");
      setUploading(false);
    }
  };

  return (
    <div className="pdf-uploader p-4 border rounded shadow-sm">
      <h2 className="text-lg font-bold mb-2">PDF Yükleyici</h2>
      <input
        type="file"
        multiple
        accept="application/pdf"
        onChange={handleFileChange}
        disabled={uploading}
        className="mb-2"
      />
      {selectedFiles.length > 0 && (
        <div className="mb-2">
          <strong>Seçilen dosyalar:</strong>
          <ul className="list-disc list-inside">
            {selectedFiles.map((file) => (
              <li key={file.name}>{file.name}</li>
            ))}
          </ul>
        </div>
      )}
      {error && <p className="text-red-500 mb-2">{error}</p>}
      {uploading && (
        <div className="mb-2">
          <p>Yükleniyor... {progress}%</p>
          <progress value={progress} max="100" className="w-full" />
        </div>
      )}
      <button
        onClick={handleUpload}
        disabled={uploading || selectedFiles.length === 0}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
      >
        {uploading ? "Yükleniyor..." : "PDF Yükle"}
      </button>
    </div>
  );
};

PDFUploader.propTypes = {
  onUploadComplete: PropTypes.func,
};

export default PDFUploader;