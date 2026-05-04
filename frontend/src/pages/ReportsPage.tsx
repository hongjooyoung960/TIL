import { useEffect, useState } from "react";
import { fetchJson } from "../api/client";
import type { GitCommitLog, ReportSummary } from "../types";

export function ReportsPage() {
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [logs, setLogs] = useState<GitCommitLog[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setError(null);
      try {
        const [r, l] = await Promise.all([
          fetchJson<ReportSummary[]>("/reports/list"),
          fetchJson<GitCommitLog[]>("/git/logs"),
        ]);
        if (!cancelled) {
          setReports(r);
          setLogs(l);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "리포트 로드 실패");
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div>
      <div className="card">
        <h1 style={{ marginTop: 0 }}>리포트 및 Git 상태</h1>
        <p style={{ color: "#64748b" }}>
          백엔드가 생성한 JSON/Markdown 산출물과 Git 커밋 로그를 확인합니다.
        </p>
        {error && <p style={{ color: "#b45309" }}>{error}</p>}
      </div>

      <div className="card">
        <h3>생성된 일간 리포트</h3>
        <div style={{ overflowX: "auto" }}>
          <table>
            <thead>
              <tr>
                <th>날짜</th>
                <th>메인 목표</th>
                <th>가중 성취율</th>
                <th>JSON</th>
                <th>Markdown</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((r) => (
                <tr key={r.date}>
                  <td>{r.date}</td>
                  <td>{r.main_goal ?? "—"}</td>
                  <td>{r.achievement_rate_weighted ?? "—"}</td>
                  <td>{r.json_path ?? "—"}</td>
                  <td>{r.markdown_path ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {reports.length === 0 && <p>아직 생성된 리포트가 없습니다.</p>}
        </div>
      </div>

      <div className="card">
        <h3>Git 커밋 로그</h3>
        <div style={{ overflowX: "auto" }}>
          <table>
            <thead>
              <tr>
                <th>시각</th>
                <th>날짜</th>
                <th>상태</th>
                <th>커밋</th>
                <th>메시지</th>
                <th>오류</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>{new Date(log.created_at).toLocaleString()}</td>
                  <td>{log.plan_date}</td>
                  <td>
                    <span style={{ color: log.status === "success" ? "#15803d" : "#b91c1c" }}>{log.status}</span>
                  </td>
                  <td style={{ fontFamily: "monospace", fontSize: "0.85rem" }}>
                    {log.commit_hash?.slice(0, 7) ?? "—"}
                  </td>
                  <td>{log.commit_message ?? "—"}</td>
                  <td style={{ color: "#b45309", maxWidth: 360 }}>{log.error_message ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {logs.length === 0 && <p>Git 커밋 기록이 없습니다.</p>}
        </div>
      </div>
    </div>
  );
}
