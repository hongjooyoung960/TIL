export type ActivityStatus = "planned" | "done" | "missed" | "partial";

export interface Activity {
  id: string;
  daily_plan_id: string;
  activity_name: string;
  category: string | null;
  start_time: string | null;
  end_time: string | null;
  duration_minutes: number | null;
  status: ActivityStatus | string;
  importance_score: number;
  focus_score: number;
  memo: string | null;
  created_at: string;
}

export interface DailyGoalLink {
  id: string;
  daily_plan_id: string;
  goal_id: string;
  contribution_score: number;
}

export interface DailyPlan {
  id: string;
  plan_date: string;
  wake_time: string | null;
  sleep_time: string | null;
  main_goal: string | null;
  daily_memo: string | null;
  total_score: number | null;
  achievement_rate: number | null;
  created_at: string;
  updated_at: string;
  activities: Activity[];
  goal_links: DailyGoalLink[];
}

export interface Goal {
  id: string;
  title: string;
  description: string | null;
  goal_type: string;
  parent_goal_id: string | null;
  target_date: string | null;
  status: string;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface WeeklyStats {
  year: number;
  week: number;
  average_achievement_rate: number | null;
  total_focused_time_minutes: number;
  total_activity_duration_minutes: number;
  category_distribution: Record<string, number>;
  average_wake_time: string | null;
  average_sleep_time: string | null;
  missed_activity_count: number;
  achievement_by_day: { date: string; achievement_rate: number | null; basic_rate: number | null }[];
}

export interface GitCommitLog {
  id: string;
  plan_date: string;
  commit_hash: string | null;
  commit_message: string | null;
  status: string;
  error_message: string | null;
  created_at: string;
}

export interface ReportSummary {
  date: string;
  json_path: string | null;
  markdown_path: string | null;
  achievement_rate_weighted: number | null;
  main_goal: string | null;
}

export interface SleepPoint {
  date: string;
  wake_minutes: number | null;
  sleep_minutes: number | null;
}
