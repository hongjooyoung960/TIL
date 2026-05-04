import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchJson } from "../api/client";
import type { SleepPoint, WeeklyStats } from "../types";
import { getIsoWeekAndYear, minutesToHourLabel } from "../utils/date";

const PIE_COLORS = ["#2563eb", "#22c55e", "#f97316", "#a855f7", "#eab308", "#14b8a6"];

export function WeeklyPage() {
  const initial = useMemo(() => getIsoWeekAndYear(new Date()), []);
  const [year, setYear] = useState(initial.year);
  const [week, setWeek] = useState(initial.week);
  const [stats, setStats] = useState<WeeklyStats | null>(null);
  const [sleep, setSleep] = useState<SleepPoint[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setError(null);
      try {
        const [w, s] = await Promise.all([
          fetchJson<WeeklyStats>(`/weekly/${year}/${week}`),
          fetchJson<SleepPoint[]>("/weekly/sleep-pattern/recent"),
        ]);
        if (!cancelled) {
          setStats(w);
          setSleep(s);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "주간 데이터 로드 실패");
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, [year, week]);

  const categoryData = Object.entries(stats?.category_distribution ?? {}).map(([name, value]) => ({
    name,
    value,
  }));

  const achievementData =
    stats?.achievement_by_day.map((d) => ({
      ...d,
      label: d.date.slice(5),
      rate: d.achievement_rate ?? 0,
    })) ?? [];

  const sleepSeries =
    sleep?.map((row) => ({
      date: row.date.slice(5),
      wake_h: minutesToHourLabel(row.wake_minutes),
      sleep_h: minutesToHourLabel(row.sleep_minutes),
    })) ?? [];

  return (
    <div>
      <div className="card">
        <h1 style={{ marginTop: 0 }}>주간 플래너</h1>
        <div className="grid two" style={{ alignItems: "end" }}>
          <label>
            연도
            <input type="number" value={year} onChange={(e) => setYear(Number(e.target.value))} />
          </label>
          <label>
            주차 (ISO)
            <input type="number" value={week} min={1} max={53} onChange={(e) => setWeek(Number(e.target.value))} />
          </label>
        </div>
        {error && <p style={{ color: "#b45309" }}>{error}</p>}
      </div>

      {stats && (
        <>
          <div className="card grid two">
            <div>
              <h3>요약</h3>
              <p>평균 가중 성취율: {stats.average_achievement_rate ?? "—"}%</p>
              <p>총 집중 시간(가중 분): {stats.total_focused_time_minutes}</p>
              <p>총 활동 지속 시간(분): {stats.total_activity_duration_minutes}</p>
              <p>평균 기상: {stats.average_wake_time ?? "—"}</p>
              <p>평균 취침: {stats.average_sleep_time ?? "—"}</p>
              <p>missed 활동 수: {stats.missed_activity_count}</p>
            </div>
            <div style={{ height: 260 }}>
              <h3>요일별 성취율 막대</h3>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={achievementData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="rate" name="성취율(%)" fill="#2563eb" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card grid two">
            <div style={{ height: 280 }}>
              <h3>카테고리 분포 (분)</h3>
              {categoryData.length === 0 ? (
                <p>이번 주 기록된 카테고리 시간이 없습니다.</p>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie dataKey="value" data={categoryData} outerRadius={90} label>
                      {categoryData.map((_, idx) => (
                        <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
            <div style={{ height: 280 }}>
              <h3>수면 패턴 (시간, 근 2주)</h3>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={sleepSeries}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="wake_h" name="기상(h)" stroke="#2563eb" dot />
                  <Line type="monotone" dataKey="sleep_h" name="취침(h)" stroke="#f97316" dot />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
