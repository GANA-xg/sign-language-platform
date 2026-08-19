import type { BadgeVariant } from "../../lib/types";

export function Bdg({ label, v = "default" }: { label: string; v?: BadgeVariant }) {
  const cls: Record<BadgeVariant, string> = {
    default: "bg-muted text-muted-foreground",
    success: "bg-success/10 text-success",
    warning: "bg-warning/10 text-warning",
    error: "bg-danger/10 text-danger",
    info: "bg-info/10 text-info",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${cls[v]}`}>
      {label}
    </span>
  );
}

export function PBar({ pct, cls = "" }: { pct: number; cls?: string }) {
  return (
    <div className={`h-2 bg-muted rounded-full overflow-hidden ${cls}`}>
      <div
        className="h-full bg-primary rounded-full transition-all duration-700"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

export function Ring({ pct, size = 80 }: { pct: number; size?: number }) {
  const r = (size - 10) / 2;
  const c = 2 * Math.PI * r;
  const off = c - (pct / 100) * c;
  const col = pct >= 80 ? "var(--success)" : pct >= 60 ? "var(--warning)" : "var(--danger)";
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--border)" strokeWidth={6} />
        <circle
          cx={size / 2} cy={size / 2} r={r} fill="none"
          stroke={col} strokeWidth={6}
          strokeDasharray={c} strokeDashoffset={off}
          strokeLinecap="round" className="transition-all duration-700"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-sm font-bold" style={{ color: col }}>{pct}%</span>
      </div>
    </div>
  );
}
