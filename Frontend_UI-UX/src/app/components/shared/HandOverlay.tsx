import { useState, useEffect } from "react";
import { LANDMARKS, CONNECTIONS } from "../../utils/mockData";

export function HandOverlay({
  w = 300, h = 380, animated = true,
}: {
  w?: number; h?: number; animated?: boolean;
}) {
  const [tick, setTick] = useState(0);
  useEffect(() => {
    if (!animated) return;
    const id = setInterval(() => setTick(t => t + 1), 60);
    return () => clearInterval(id);
  }, [animated]);
  const j = (v: number, i: number) =>
    animated ? v + Math.sin((tick * 0.07 + i * 0.8)) * 0.007 : v;
  return (
    <svg width={w} height={h} className="pointer-events-none">
      {CONNECTIONS.map(([a, b], i) => (
        <line
          key={i}
          x1={j(LANDMARKS[a][0], a) * w} y1={j(LANDMARKS[a][1], a) * h}
          x2={j(LANDMARKS[b][0], b) * w} y2={j(LANDMARKS[b][1], b) * h}
          className="stroke-hand-stroke" strokeWidth={1.5}
        />
      ))}
      {LANDMARKS.map(([x, y], i) => (
        <circle
          key={i}
          cx={j(x, i) * w} cy={j(y, i) * h}
          r={i === 0 ? 5 : i % 4 === 0 ? 4.5 : 3}
          className={i % 4 === 0 ? "fill-hand-joint" : "fill-hand-bone"}
        />
      ))}
    </svg>
  );
}
