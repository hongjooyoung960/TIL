import { type FormEvent, useEffect, useMemo, useState } from "react";
import { fetchJson } from "../api/client";
import type { Goal } from "../types";

export function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [goalType, setGoalType] = useState("daily");
  const [parentId, setParentId] = useState("");
  const [progress, setProgress] = useState(10);

  const load = async () => {
    setError(null);
    try {
      const data = await fetchJson<Goal[]>("/goals");
      setGoals(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "목표 목록 로드 실패");
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const grouped = useMemo(() => {
    const buckets: Record<string, Goal[]> = {};
    goals.forEach((g) => {
      buckets[g.goal_type] = buckets[g.goal_type] ?? [];
      buckets[g.goal_type].push(g);
    });
    return buckets;
  }, [goals]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await fetchJson("/goals", {
        method: "POST",
        body: JSON.stringify({
          title,
          description: description || null,
          goal_type: goalType,
          parent_goal_id: parentId || null,
          target_date: null,
          status: "active",
          progress,
        }),
      });
      setTitle("");
      setDescription("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "목표 생성 실패");
    }
  };

  const remove = async (id: string) => {
    setError(null);
    try {
      await fetchJson(`/goals/${id}`, { method: "DELETE" });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "삭제 실패");
    }
  };

  const goalTitleMap = useMemo(() => Object.fromEntries(goals.map((g) => [g.id, g.title])), [goals]);

  const renderGoal = (g: Goal) => (
    <div key={g.id} className="card" style={{ padding: "0.85rem 1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: "0.75rem" }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700 }}>{g.title}</div>
          <div style={{ color: "#64748b", fontSize: "0.9rem" }}>{g.description}</div>
          {g.parent_goal_id && (
            <div style={{ fontSize: "0.85rem", marginTop: "0.35rem" }}>
              상위 목표: {goalTitleMap[g.parent_goal_id] ?? g.parent_goal_id}
            </div>
          )}
        </div>
        <div style={{ textAlign: "right" }}>
          <div>진행률 {Number(g.progress).toFixed(0)}%</div>
          <button type="button" className="danger" style={{ marginTop: "0.35rem" }} onClick={() => void remove(g.id)}>
            삭제
          </button>
        </div>
      </div>
      <div style={{ marginTop: "0.5rem" }}>
        <div className="progress-bar">
          <span style={{ width: `${Math.min(100, Number(g.progress))}%` }} />
        </div>
      </div>
    </div>
  );

  const order = ["long_term", "monthly", "weekly", "daily"];

  return (
    <div>
      <div className="card">
        <h1 style={{ marginTop: 0 }}>목표 관리</h1>
        <form className="grid two" onSubmit={submit}>
          <label>
            제목
            <input value={title} onChange={(e) => setTitle(e.target.value)} required />
          </label>
          <label>
            유형
            <select value={goalType} onChange={(e) => setGoalType(e.target.value)}>
              <option value="long_term">long_term</option>
              <option value="monthly">monthly</option>
              <option value="weekly">weekly</option>
              <option value="daily">daily</option>
            </select>
          </label>
          <label style={{ gridColumn: "span 2" }}>
            설명
            <textarea rows={2} value={description} onChange={(e) => setDescription(e.target.value)} />
          </label>
          <label>
            상위 목표
            <select value={parentId} onChange={(e) => setParentId(e.target.value)}>
              <option value="">없음</option>
              {goals.map((g) => (
                <option key={g.id} value={g.id}>
                  [{g.goal_type}] {g.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            초기 진행률 (%)
            <input type="number" min={0} max={100} value={progress} onChange={(e) => setProgress(Number(e.target.value))} />
          </label>
          <button type="submit" style={{ gridColumn: "span 2", justifySelf: "start" }}>
            목표 추가
          </button>
        </form>
        {error && <p style={{ color: "#b45309" }}>{error}</p>}
      </div>

      {order.map((bucket) =>
        grouped[bucket]?.length ? (
          <section key={bucket} style={{ marginTop: "1rem" }}>
            <h2 style={{ textTransform: "capitalize" }}>{bucket.replace("_", " ")}</h2>
            <div className="grid">{grouped[bucket].map(renderGoal)}</div>
          </section>
        ) : null,
      )}
      {Object.keys(grouped)
        .filter((k) => !order.includes(k))
        .map((bucket) => (
          <section key={bucket} style={{ marginTop: "1rem" }}>
            <h2>{bucket}</h2>
            <div className="grid">{grouped[bucket].map(renderGoal)}</div>
          </section>
        ))}
    </div>
  );
}
