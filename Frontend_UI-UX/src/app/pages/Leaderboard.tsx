import { useEffect, useState } from "react";
import { Trophy, Flame, ArrowUpRight, Medal, Crown, Sparkles } from "lucide-react";
import type { Screen } from "../utils/types";
import { MCard } from "../components/shared/MCard";
import { Bdg } from "../components/shared/Indicators";
import { useAuth } from "../context/AuthContext";
import { getLeaderboard, getGamification } from "../services/businessApi";

type LeaderRow = {
  rank: number;
  name: string;
  role: string;
  accuracy: number;
  streak: number;
  badges: number;
  isMe?: boolean;
};

function MedalIcon({ rank }: { rank: number }) {
  if (rank === 1) return <Crown size={16} className="text-warning" />;
  if (rank === 2) return <Medal size={16} className="text-slate-300" />;
  if (rank === 3) return <Medal size={16} className="text-amber-600" />;
  return <span className="text-xs font-semibold text-muted-foreground">#{rank}</span>;
}

function LeaderCard({
  title,
  subtitle,
  rows,
  metricLabel,
  metricValue,
}: {
  title: string;
  subtitle: string;
  rows: LeaderRow[];
  metricLabel: string;
  metricValue: (row: LeaderRow) => string;
}) {
  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-foreground">{title}</h3>
          <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
        </div>
        <Bdg label="Live data" v="info" />
      </div>

      <div className="space-y-2">
        {rows.map((row) => (
          <div
            key={`${title}-${row.rank}-${row.name}`}
            className={`flex items-center gap-3 rounded-lg border px-3 py-3 transition-all ${
              row.isMe
                ? "border-primary/40 bg-primary/5 ring-1 ring-primary/20"
                : "border-border bg-[#0e1a30]"
            }`}
          >
            <div className="w-8 flex items-center justify-center">
              <MedalIcon rank={row.rank} />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <div className="text-sm font-semibold text-foreground truncate">{row.name}</div>
                {row.isMe && <Bdg label="You" v="success" />}
              </div>
              <div className="text-xs text-muted-foreground truncate">{row.role}</div>
            </div>

            <div className="text-right">
              <div className="text-sm font-semibold text-foreground">{metricValue(row)}</div>
              <div className="text-[11px] text-muted-foreground">{metricLabel}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Leaderboard({ go }: { go: (s: Screen) => void }) {
  const { userId } = useAuth();
  const [accuracyLeaders, setAccuracyLeaders] = useState<LeaderRow[]>([]);
  const [streakLeaders, setStreakLeaders] = useState<LeaderRow[]>([]);
  const [me, setMe] = useState<LeaderRow | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userId) return;
    setLoading(true);
    Promise.all([getLeaderboard("accuracy"), getLeaderboard("streak"), getGamification(userId)])
      .then(([acc, streak, gamification]) => {
        const mapRows = (entries: any[]) =>
          entries.map((entry) => ({
            rank: entry.rank,
            name: entry.user_id === userId ? "You" : `Learner ${String(entry.user_id).slice(0, 4)}`,
            role: "Learner",
            accuracy: Math.round(entry.average_accuracy),
            streak: entry.current_streak,
            badges: gamification.total_badges_earned,
            isMe: entry.user_id === userId,
          }));

        const accuracyRows = mapRows(acc.entries ?? []);
        const streakRows = mapRows(streak.entries ?? []);
        setAccuracyLeaders(accuracyRows);
        setStreakLeaders(streakRows);
        setMe(accuracyRows.find((row) => row.isMe) ?? accuracyRows[0] ?? null);
      })
      .finally(() => setLoading(false));
  }, [userId]);

  return (
    <div className="p-6 space-y-5 max-w-6xl mx-auto">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Leaderboard</h2>
          <p className="text-muted-foreground text-sm mt-1">
            Compare progress by accuracy and streak, with your rank highlighted.
          </p>
        </div>
        <button
          onClick={() => go("practice")}
          className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90 transition"
        >
          <Sparkles size={16} />
          Keep Practicing
        </button>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <MCard icon={Trophy} label="Your Accuracy Rank" value={me ? `#${me.rank}` : "—"} delta={me ? `${me.accuracy}% accuracy` : "Loading"} col="cyan" />
        <MCard icon={Flame} label="Current Streak" value={me ? `${me.streak}` : "—"} delta="days in a row" col="amber" />
        <MCard icon={ArrowUpRight} label="Badges Earned" value={me ? `${me.badges}` : "—"} delta="live from gamification" col="emerald" />
        <MCard icon={Medal} label="Top Rank" value="#1" delta="by accuracy & streak" col="violet" />
      </div>

      {loading ? (
        <div className="bg-card border border-border rounded-xl p-8 text-center text-sm text-muted-foreground">
          Loading leaderboard…
        </div>
      ) : accuracyLeaders.length === 0 ? (
        <div className="bg-card border border-border rounded-xl p-8 text-center space-y-2">
          <div className="text-sm font-semibold text-foreground">No leaderboard data yet</div>
          <div className="text-xs text-muted-foreground">
            Start practicing to appear on the leaderboard once the backend has session data.
          </div>
          <button
            onClick={() => go("practice")}
            className="mt-2 inline-flex items-center gap-2 rounded-xl border border-border bg-muted px-4 py-2 text-sm font-semibold text-foreground hover:bg-hover transition"
          >
            <Sparkles size={14} />
            Practice now
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          <LeaderCard
            title="Ranked by Accuracy"
            subtitle="Highest average accuracy across recent practice"
            rows={accuracyLeaders}
            metricLabel="accuracy"
            metricValue={(row) => `${row.accuracy}%`}
          />

          <LeaderCard
            title="Ranked by Streak"
            subtitle="Longest active practice streak this week"
            rows={streakLeaders}
            metricLabel="streak"
            metricValue={(row) => `${row.streak} days`}
          />
        </div>
      )}
    </div>
  );
}
