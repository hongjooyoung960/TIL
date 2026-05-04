/** ISO week number and ISO week-year (approximation suitable for UI). */
export function getIsoWeekAndYear(source: Date): { year: number; week: number } {
  const d = new Date(Date.UTC(source.getFullYear(), source.getMonth(), source.getDate()));
  const day = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - day);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  const week = Math.ceil(((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7);
  return { year: d.getUTCFullYear(), week };
}

export function minutesToHourLabel(min: number | null | undefined): number | null {
  if (min == null || Number.isNaN(min)) return null;
  return Math.round((min / 60) * 100) / 100;
}
