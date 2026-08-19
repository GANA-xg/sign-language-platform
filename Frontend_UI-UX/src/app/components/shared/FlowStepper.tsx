import { Check, ChevronRight } from "lucide-react";

const FLOW_STEPS = ["Select Lesson", "Practice", "AI Analysis", "Feedback", "Saved"];

export function FlowStepper({ active }: { active: number }) {
  return (
    <div className="flex items-center justify-center gap-1.5 py-2.5 border-b border-border/50 bg-muted/50">
      {FLOW_STEPS.map((s, i) => (
        <div key={s} className="flex items-center gap-1.5">
          <div
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
              i === active
                ? "bg-primary text-primary-foreground"
                : i < active
                ? "bg-success/10 text-success"
                : "text-muted-foreground"
            }`}
          >
            {i < active && <Check size={9} />}
            {s}
          </div>
          {i < FLOW_STEPS.length - 1 && <ChevronRight size={11} className="text-muted-foreground" />}
        </div>
      ))}
    </div>
  );
}
