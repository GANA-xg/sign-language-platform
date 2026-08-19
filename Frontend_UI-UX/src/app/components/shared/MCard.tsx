import type { MColor } from "../../lib/types";

const MCLS: Record<MColor, string> = {
  cyan:    "text-info bg-info/10",
  emerald: "text-success bg-success/10",
  violet:  "text-foreground bg-muted",
  amber:   "text-warning bg-warning/10",
};

export function MCard({
  icon: Icon, label, value, delta, col = "cyan",
}: { icon: React.ElementType; label: string; value: string; delta?: string; col?: MColor }) {
  return (
    <div className="bg-card border border-border rounded-[14px] p-6" style={{ boxShadow: 'var(--card-shadow)' }}>
      <div className="flex items-start justify-between mb-4">
        <div className={`p-2.5 rounded-xl ${MCLS[col]}`}>
          <Icon size={18} className={MCLS[col].split(" ")[0]} />
        </div>
        {delta && (
          <span className="text-xs text-success bg-success/10 px-2.5 py-1 rounded-full font-medium">
            {delta}
          </span>
        )}
      </div>
      <div className="text-2xl font-bold text-foreground mb-1">{value}</div>
      <div className="text-xs text-muted-foreground">{label}</div>
    </div>
  );
}
