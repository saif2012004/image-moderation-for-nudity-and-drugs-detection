import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:7000";

function App() {
  const [token, setToken] = useState(localStorage.getItem("auth_token") || "");
  const [isAdmin, setIsAdmin] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [moderationResult, setModerationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [tokens, setTokens] = useState([]);

  // Save token to localStorage when it changes
  React.useEffect(() => {
    if (token) {
      localStorage.setItem("auth_token", token);
    }
  }, [token]);

  const handleLogin = () => {
    if (token.trim()) {
      setError("");
      // Token is saved automatically via useEffect
    } else {
      setError("Please enter a valid token");
    }
  };

  const handleLogout = () => {
    setToken("");
    setTokens([]);
    setModerationResult(null);
    localStorage.removeItem("auth_token");
  };

  const createToken = async () => {
    if (!token) {
      setError("Please login first");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/auth/tokens`,
        { isAdmin },
        {
          headers: { Authorization: `Bearer ${token}` },
          params: { isAdmin },
        }
      );
      setError("");
      alert(`New token created: ${response.data.token}`);
      await fetchTokens(); // Refresh tokens list
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create token");
    }
    setLoading(false);
  };

  const fetchTokens = async () => {
    if (!token) return;

    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/auth/tokens`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setTokens(response.data);
      setError("");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to fetch tokens");
    }
    setLoading(false);
  };

  const deleteToken = async (tokenToDelete) => {
    if (!token) return;

    setLoading(true);
    try {
      await axios.delete(`${API_BASE_URL}/auth/tokens/${tokenToDelete}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setError("");
      await fetchTokens(); // Refresh tokens list
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete token");
    }
    setLoading(false);
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type.startsWith("image/")) {
        setSelectedFile(file);
        setError("");
      } else {
        setError("Please select an image file");
        setSelectedFile(null);
      }
    }
  };

  const moderateImage = async () => {
    if (!selectedFile || !token) {
      setError("Please select an image and provide a token");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await axios.post(`${API_BASE_URL}/moderate`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
      });
      setModerationResult(response.data);
      setError("");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to moderate image");
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🛡️ Image Moderation API</h1>
          <p>Upload images for content safety analysis</p>
        </header>

        {/* Token Authentication Section */}
        <div className="auth-section">
          <h2>Authentication</h2>
          {!token ? (
            <div className="auth-form">
              <input
                type="text"
                placeholder="Enter your bearer token"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                className="token-input"
              />
              <button onClick={handleLogin} className="btn primary">
                Login
              </button>
            </div>
          ) : (
            <div className="auth-info">
              <p>✅ Authenticated with token: {token.substring(0, 8)}...</p>
              <button onClick={handleLogout} className="btn secondary">
                Logout
              </button>
            </div>
          )}
        </div>

        {token && (
          <>
            {/* Admin Token Management */}
            <div className="admin-section">
              <h2>Token Management (Admin Only)</h2>
              <div className="admin-controls">
                <label>
                  <input
                    type="checkbox"
                    checked={isAdmin}
                    onChange={(e) => setIsAdmin(e.target.checked)}
                  />
                  Create admin token
                </label>
                <button
                  onClick={createToken}
                  disabled={loading}
                  className="btn primary"
                >
                  Create Token
                </button>
                <button
                  onClick={fetchTokens}
                  disabled={loading}
                  className="btn secondary"
                >
                  View All Tokens
                </button>
              </div>

              {tokens.length > 0 && (
                <div className="tokens-list">
                  <h3>All Tokens:</h3>
                  {tokens.map((t) => (
                    <div key={t.token} className="token-item">
                      <span>
                        {t.token.substring(0, 16)}...{" "}
                        {t.isAdmin ? "(Admin)" : "(User)"}
                      </span>
                      <button
                        onClick={() => deleteToken(t.token)}
                        className="btn danger small"
                        disabled={loading}
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Image Moderation Section */}
            <div className="moderation-section">
              <h2>Image Moderation</h2>
              <div className="upload-area">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="file-input"
                  id="file-input"
                />
                <label htmlFor="file-input" className="file-label">
                  {selectedFile ? selectedFile.name : "Choose an image..."}
                </label>
                <button
                  onClick={moderateImage}
                  disabled={!selectedFile || loading}
                  className="btn primary"
                >
                  {loading ? "Analyzing..." : "Moderate Image"}
                </button>
              </div>

              {selectedFile && (
                <div className="image-preview">
                  <img
                    src={URL.createObjectURL(selectedFile)}
                    alt="Preview"
                    className="preview-image"
                  />
                </div>
              )}
            </div>

            {/* Results Section */}
            {moderationResult && (
              <div className="results-section">
                <h2>Moderation Results</h2>
                <div
                  className={`result-summary ${
                    moderationResult.safe ? "safe" : "unsafe"
                  }`}
                >
                  <h3>
                    {moderationResult.safe
                      ? "✅ Image is Safe"
                      : "⚠️ Image Flagged"}
                  </h3>
                  <p>
                    Overall Confidence:{" "}
                    {(moderationResult.overall_confidence * 100).toFixed(1)}%
                  </p>
                  <p>Analyzed: {moderationResult.filename}</p>
                  <p>
                    Time:{" "}
                    {new Date(moderationResult.timestamp).toLocaleString()}
                  </p>
                </div>

                <div className="categories">
                  <h3>Category Analysis:</h3>
                  {moderationResult.categories.map((category) => (
                    <div
                      key={category.category}
                      className={`category-item ${
                        category.flagged ? "flagged" : "clean"
                      }`}
                    >
                      <span className="category-name">
                        {category.category.replace(/_/g, " ")}
                      </span>
                      <span className="confidence">
                        {(category.confidence * 100).toFixed(1)}%
                      </span>
                      <span className="status">
                        {category.flagged ? "🚫 Flagged" : "✅ Clean"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {error && <div className="error-message">❌ {error}</div>}
      </div>
    </div>
  );
}

export default App;
