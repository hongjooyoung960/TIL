export function ProgressBar({ value }: { value: number | null | undefined }) {
  const pct = value == null ? 0 : Math.min(100, Math.max(0, value));
  return (
    <div className="progress-bar">
      <span style={{ width: `${pct}%` }} />
    </div>
  );
}
