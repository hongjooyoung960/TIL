import { useCallback, useEffect, useMemo, useState } from "react";
import { apiUrl, fetchJson } from "../api/client";
import { ProgressBar } from "../components/ProgressBar";
import type { Activity, ActivityStatus, DailyPlan, Goal } from "../types";
import { getIsoWeekAndYear } from "../utils/date";

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function toApiTime(s: string): string | null {
  if (!s) return null;
  return s.length === 5 ? `${s}:00` : s;
}

async function loadDailyPlan(date: string): Promise<DailyPlan | null> {
  const res = await fetch(apiUrl(`/daily/${date}`));
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as DailyPlan;
}

export function DailyPage() {
  const [date, setDate] = useState(todayIso());
  const [plan, setPlan] = useState<DailyPlan | null>(null);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [wake, setWake] = useState("");
  const [sleep, setSleep] = useState("");
  const [mainGoal, setMainGoal] = useState("");
  const [memo, setMemo] = useState("");
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    setMessage(null);
    try {
      const [p, gs] = await Promise.all([loadDailyPlan(date), fetchJson<Goal[]>("/goals")]);
      setPlan(p);
      setGoals(gs);
      if (p) {
        setWake(p.wake_time?.slice(0, 5) ?? "");
        setSleep(p.sleep_time?.slice(0, 5) ?? "");
        setMainGoal(p.main_goal ?? "");
        setMemo(p.daily_memo ?? "");
        setSelectedGoals(p.goal_links.map((l) => l.goal_id));
      } else {
        setWake("");
        setSleep("");
        setMainGoal("");
        setMemo("");
        setSelectedGoals([]);
      }
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "불러오기 실패");
    } finally {
      setLoading(false);
    }
  }, [date]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const { year, week } = useMemo(() => getIsoWeekAndYear(new Date(date)), [date]);

  const completed = plan?.activities.filter((a) => a.status === "done").length ?? 0;
  const missed = plan?.activities.filter((a) => a.status === "missed").length ?? 0;
  const weighted = plan?.achievement_rate ?? 0;

  const createPlan = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const body = {
        plan_date: date,
        wake_time: toApiTime(wake),
        sleep_time: toApiTime(sleep),
        main_goal: mainGoal || null,
        daily_memo: memo || null,
        goal_links: selectedGoals.map((id) => ({ goal_id: id, contribution_score: 4 })),
      };
      await fetchJson<DailyPlan>("/daily", { method: "POST", body: JSON.stringify(body) });
      await refresh();
      setMessage("일간 플랜을 생성했습니다.");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "생성 실패");
    } finally {
      setLoading(false);
    }
  };

  const savePlan = async () => {
    if (!plan) return;
    setLoading(true);
    setMessage(null);
    try {
      const body = {
        wake_time: toApiTime(wake),
        sleep_time: toApiTime(sleep),
        main_goal: mainGoal || null,
        daily_memo: memo || null,
        goal_links: selectedGoals.map((id) => ({ goal_id: id, contribution_score: 4 })),
      };
      await fetchJson<DailyPlan>(`/daily/${date}`, { method: "PUT", body: JSON.stringify(body) });
      await refresh();
      setMessage("저장되었습니다.");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "저장 실패");
    } finally {
      setLoading(false);
    }
  };

  const toggleGoal = (id: string) => {
    setSelectedGoals((prev) => (prev.includes(id) ? prev.filter((g) => g !== id) : [...prev, id]));
  };

  const addActivity = async () => {
    if (!plan) return;
    setLoading(true);
    setMessage(null);
    try {
      await fetchJson("/activities", {
        method: "POST",
        body: JSON.stringify({
          daily_plan_id: plan.id,
          activity_name: "새 활동",
          category: "general",
          status: "planned",
          importance_score: 3,
          focus_score: 3,
        }),
      });
      await refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "활동 추가 실패");
    } finally {
      setLoading(false);
    }
  };

  const updateActivity = async (act: Activity, patch: Partial<Activity>) => {
    setLoading(true);
    setMessage(null);
    try {
      const body: Record<string, unknown> = {};
      const keys = [
        "activity_name",
        "category",
        "start_time",
        "end_time",
        "duration_minutes",
        "status",
        "importance_score",
        "focus_score",
        "memo",
      ] as const;
      keys.forEach((k) => {
        if (k in patch) body[k] = patch[k];
      });
      await fetchJson(`/activities/${act.id}`, { method: "PUT", body: JSON.stringify(body) });
      await refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "활동 저장 실패");
    } finally {
      setLoading(false);
    }
  };

  const deleteActivity = async (id: string) => {
    setLoading(true);
    setMessage(null);
    try {
      await fetchJson(`/activities/${id}`, { method: "DELETE" });
      await refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "삭제 실패");
    } finally {
      setLoading(false);
    }
  };

  const commitGit = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const res = await fetchJson<{ status: string; error?: string }>(`/git/commit-daily/${date}`, {
        method: "POST",
      });
      setMessage(res.status === "success" ? "Git 커밋 및 push 요청이 완료되었습니다." : `Git 실패: ${res.error ?? ""}`);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Git 요청 실패");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="card">
        <h1 style={{ marginTop: 0 }}>일간 플래너</h1>
        <p style={{ color: "#64748b" }}>
          선택한 날짜: <strong>{date}</strong> (ISO 주차 {year}-W{week.toString().padStart(2, "0")})
        </p>
        <div className="grid two" style={{ alignItems: "end" }}>
          <label>
            날짜
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </label>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button type="button" className="secondary" onClick={() => void refresh()} disabled={loading}>
              새로고침
            </button>
            {!plan && (
              <button type="button" onClick={() => void createPlan()} disabled={loading}>
                빈 플랜 만들기
              </button>
            )}
            {plan && (
              <>
                <button type="button" onClick={() => void savePlan()} disabled={loading}>
                  일간 플랜 저장
                </button>
                <button type="button" onClick={() => void commitGit()} disabled={loading}>
                  오늘 로그 Git 커밋
                </button>
              </>
            )}
          </div>
        </div>
        {message && <p style={{ color: "#b45309" }}>{message}</p>}
      </div>

      {plan && (
        <>
          <div className="card grid two">
            <label>
              기상 시간
              <input type="time" value={wake} onChange={(e) => setWake(e.target.value)} />
            </label>
            <label>
              취침 시간
              <input type="time" value={sleep} onChange={(e) => setSleep(e.target.value)} />
            </label>
            <label style={{ gridColumn: "span 2" }}>
              하루 메인 목표
              <input value={mainGoal} onChange={(e) => setMainGoal(e.target.value)} />
            </label>
            <label style={{ gridColumn: "span 2" }}>
              메모
              <textarea rows={3} value={memo} onChange={(e) => setMemo(e.target.value)} />
            </label>
            <div style={{ gridColumn: "span 2" }}>
              <div style={{ marginBottom: "0.35rem", fontWeight: 600 }}>연결된 목표</div>
              <div className="grid two">
                {goals.map((g) => (
                  <label key={g.id} style={{ display: "flex", gap: "0.35rem", alignItems: "center" }}>
                    <input
                      type="checkbox"
                      checked={selectedGoals.includes(g.id)}
                      onChange={() => toggleGoal(g.id)}
                    />
                    <span>
                      [{g.goal_type}] {g.title}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          <div className="card">
            <h3>성취 요약</h3>
            <p>가중 성취율 (주 지표): {Number(weighted ?? 0).toFixed(2)}%</p>
            <ProgressBar value={Number(weighted ?? 0)} />
            <p style={{ marginTop: "0.75rem" }}>
              완료 {completed}건 · 놓침 {missed}건 · 총 {plan.activities.length}건
            </p>
          </div>

          <div className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3 style={{ margin: 0 }}>활동</h3>
              <button type="button" className="secondary" onClick={() => void addActivity()} disabled={loading}>
                활동 추가
              </button>
            </div>
            <div style={{ overflowX: "auto" }}>
              <table>
                <thead>
                  <tr>
                    <th>이름</th>
                    <th>카테고리</th>
                    <th>시작</th>
                    <th>종료</th>
                    <th>분</th>
                    <th>상태</th>
                    <th>중요도</th>
                    <th>집중</th>
                    <th>메모</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {plan.activities.map((a) => (
                    <ActivityRow key={a.id} activity={a} onSave={updateActivity} onDelete={deleteActivity} />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {!plan && !loading && (
        <div className="card">이 날짜에는 플랜이 없습니다. 상단에서 &quot;빈 플랜 만들기&quot;를 눌러 시작하세요.</div>
      )}
    </div>
  );
}

function ActivityRow({
  activity,
  onSave,
  onDelete,
}: {
  activity: Activity;
  onSave: (a: Activity, patch: Partial<Activity>) => void;
  onDelete: (id: string) => void;
}) {
  const [draft, setDraft] = useState({
    activity_name: activity.activity_name,
    category: activity.category ?? "",
    start_time: activity.start_time?.slice(0, 5) ?? "",
    end_time: activity.end_time?.slice(0, 5) ?? "",
    duration_minutes: activity.duration_minutes != null ? String(activity.duration_minutes) : "",
    status: activity.status as ActivityStatus,
    importance_score: activity.importance_score,
    focus_score: activity.focus_score,
    memo: activity.memo ?? "",
  });

  useEffect(() => {
    setDraft({
      activity_name: activity.activity_name,
      category: activity.category ?? "",
      start_time: activity.start_time?.slice(0, 5) ?? "",
      end_time: activity.end_time?.slice(0, 5) ?? "",
      duration_minutes: activity.duration_minutes != null ? String(activity.duration_minutes) : "",
      status: activity.status as ActivityStatus,
      importance_score: activity.importance_score,
      focus_score: activity.focus_score,
      memo: activity.memo ?? "",
    });
  }, [activity]);

  const save = () => {
    void onSave(activity, {
      activity_name: draft.activity_name,
      category: draft.category || null,
      start_time: toApiTime(String(draft.start_time)),
      end_time: toApiTime(String(draft.end_time)),
      duration_minutes:
        draft.duration_minutes === ""
          ? null
          : Number.parseInt(String(draft.duration_minutes), 10) || null,
      status: draft.status,
      importance_score: draft.importance_score,
      focus_score: draft.focus_score,
      memo: draft.memo || null,
    });
  };

  return (
    <tr>
      <td>
        <input value={draft.activity_name} onChange={(e) => setDraft({ ...draft, activity_name: e.target.value })} />
      </td>
      <td>
        <input value={draft.category} onChange={(e) => setDraft({ ...draft, category: e.target.value })} />
      </td>
      <td>
        <input type="time" value={draft.start_time} onChange={(e) => setDraft({ ...draft, start_time: e.target.value })} />
      </td>
      <td>
        <input type="time" value={draft.end_time} onChange={(e) => setDraft({ ...draft, end_time: e.target.value })} />
      </td>
      <td>
        <input
          style={{ width: "72px" }}
          type="number"
          value={draft.duration_minutes}
          onChange={(e) => setDraft({ ...draft, duration_minutes: e.target.value })}
        />
      </td>
      <td>
        <select value={draft.status} onChange={(e) => setDraft({ ...draft, status: e.target.value as ActivityStatus })}>
          <option value="planned">planned</option>
          <option value="done">done</option>
          <option value="partial">partial</option>
          <option value="missed">missed</option>
        </select>
      </td>
      <td>
        <input
          style={{ width: "64px" }}
          type="number"
          min={1}
          max={5}
          value={draft.importance_score}
          onChange={(e) => setDraft({ ...draft, importance_score: Number(e.target.value) })}
        />
      </td>
      <td>
        <input
          style={{ width: "64px" }}
          type="number"
          min={1}
          max={5}
          value={draft.focus_score}
          onChange={(e) => setDraft({ ...draft, focus_score: Number(e.target.value) })}
        />
      </td>
      <td>
        <input value={draft.memo} onChange={(e) => setDraft({ ...draft, memo: e.target.value })} />
      </td>
      <td style={{ whiteSpace: "nowrap" }}>
        <button type="button" className="secondary" onClick={save}>
          저장
        </button>{" "}
        <button type="button" className="danger" onClick={() => onDelete(activity.id)}>
          삭제
        </button>
      </td>
    </tr>
  );
}
