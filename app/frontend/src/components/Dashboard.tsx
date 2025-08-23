import { useEffect, useState } from "react";
import "../App.css";
import FileEditor from "./FileEditor";

interface DashboardProps {
  user: string;
  token: string;
  onLogout: () => void;
}

interface ScanFinding {
  file_path: string;
  line_number: number;
  key_type: string;
  line_content: string;
}

interface ScanResult {
  status: string;
  message: string;
  repository: string;
  total_files_scanned: number;
  findings?: ScanFinding[];
}

export default function Dashboard({ user, token, onLogout }: DashboardProps) {
  const [repos, setRepos] = useState<string[]>([]);
  const [selectedRepo, setSelectedRepo] = useState("");
  const [filteredRepos, setFilteredRepos] = useState<string[]>([]);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [editingFile, setEditingFile] = useState<string | null>(null);

  useEffect(() => {
    const fetchRepos = async () => {
      try {
        const res = await fetch(
          "https://secureakey-backend.onrender.com/repos",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        const data = await res.json();
        setRepos(data.repositories || []);
        setFilteredRepos(data.repositories || []);
      } catch (error) {
        console.error("Failed to fetch repositories:", error);
      }
    };
    fetchRepos();
  }, [token]);

  useEffect(() => {
    if (!selectedRepo) {
      setFilteredRepos(repos);
      return;
    }

    const filtered = repos.filter((repo) =>
      repo.toLowerCase().includes(selectedRepo.toLowerCase())
    );
    setFilteredRepos(filtered);
  }, [selectedRepo, repos]);

  const handleScan = async () => {
    if (!selectedRepo) return;
    setLoading(true);
    setScanResult(null);

    try {
      const res = await fetch(
        "https://secureakey-backend.onrender.com/scan/repo",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ repo_name: selectedRepo }),
        }
      );

      const data = await res.json();
      setScanResult(data);
    } catch (err) {
      console.error("Scan failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-wrapper">
      <div className="button-wrapper">
        <button className="logout-button" onClick={onLogout}>
          Logout
        </button>
      </div>

      <div className="header-wrapper">
        <h1 className="dashboard-greeting">Welcome, {user}!</h1>
      </div>

      <div className="repo-search-wrapper">
        <label className="search-bar-label">Select Repository:</label>
        <input
          type="text"
          value={selectedRepo}
          onChange={(e) => setSelectedRepo(e.target.value)}
          placeholder="Start typing repo name..."
          list="filtered-repos"
          autoComplete="off"
        />
        <datalist id="filtered-repos">
          {filteredRepos.map((repo) => (
            <option key={repo} value={repo} />
          ))}
        </datalist>

        <button
          className="scan-button"
          onClick={handleScan}
          disabled={loading || !selectedRepo}
        >
          {loading ? "Scanning..." : "Scan Repo"}
        </button>
      </div>

      {scanResult && (
        <div className="scan-results">
          <h3>{scanResult.message}</h3>
          <p>
            <strong>Repository:</strong> {scanResult.repository}
          </p>
          <p>
            <strong>Total Files Scanned:</strong>{" "}
            {scanResult.total_files_scanned}
          </p>

          {scanResult.findings && scanResult.findings.length > 0 && (
            <div className="key-detection-wrapper">
              <h4>Detected Keys:</h4>
              <ul>
                {scanResult.findings.map((finding, index) => (
                  <li key={index}>
                    <strong>{finding.key_type}</strong> key in{" "}
                    <code>{finding.file_path}</code> at line{" "}
                    {finding.line_number}:<br />
                    <code>{finding.line_content}</code>
                    <button
                      onClick={() => setEditingFile(finding.file_path)}
                      style={{
                        marginLeft: "1rem",
                        background: "#ff1493",
                        color: "white",
                        padding: "0.5rem",
                        border: "none",
                        borderRadius: "4px",
                      }}
                    >
                      Fix
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {editingFile && scanResult && (
        <FileEditor
          repoName={scanResult.repository}
          filePath={editingFile}
          authToken={token}
          onClose={() => setEditingFile(null)}
        />
      )}
    </div>
  );
}
