import { useState, useEffect, useRef } from "react";
import {
  Camera, ArrowRight, AlertTriangle, Loader2,
} from "lucide-react";
import type { Screen } from "../lib/types";
import { HandOverlay } from "../components/shared/HandOverlay";
import { Bdg } from "../components/shared/Indicators";
import { useAuth } from "../context/AuthContext";
import {
  startPracticeSession, submitPracticeAttempt,
  endPracticeSession, generateFeedback,
} from "../services/businessApi";

const PLACEHOLDER_LESSON_ID = 1;
const SIGNS = ["HELLO", "THANK YOU", "PLEASE", "FEAR", "SURPRISE", "DISGUST", "YES", "NO"];
const TOTAL = SIGNS.length;

type ScoreEntry = { sign: string; score: number; predicted: string | null };

export default function AssessmentScreen({ go }: { go: (s: Screen) => void }) {
  const { userId } = useAuth();
  const [qIdx, setQIdx] = useState(1);
  const [scores, setScores] = useState<ScoreEntry[]>([]);
  const [capturing, setCapturing] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionError, setSessionError] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const holdStartedAt = useRef<string | null>(null);
  const sessionEndedRef = useRef(false);

  useEffect(() => {
    let stream: MediaStream | null = null;
    navigator.mediaDevices
      ?.getUserMedia({ video: { facingMode: "user" } })
      .then(s => {
        stream = s;
        if (videoRef.current) {
          videoRef.current.srcObject = s;
          setCameraReady(true);
        }
      })
      .catch(() => setCameraError("Couldn't access your camera. Check permissions and try again."));

    const uid = userId ?? "00000000-0000-0000-0000-000000000000";
    // Reuse the session started on the Practice screen if one exists, so
    // this assessment's attempts count toward the same session.
    const existingSessionId = localStorage.getItem("current_session_id");
    if (existingSessionId) {
      setSessionId(existingSessionId);
    } else {
      startPracticeSession(uid, PLACEHOLDER_LESSON_ID)
        .then(session => {
          setSessionId(session.session_id);
          localStorage.setItem("current_session_id", session.session_id);
        })
        .catch(() => setSessionError("Couldn't start a session. Is the Business Logic service running on port 8002?"));
    }
    holdStartedAt.current = new Date().toISOString();

    return () => {
      stream?.getTracks().forEach(t => t.stop());
    };
  }, []);

  const currentSign = SIGNS[qIdx - 1];

  const capture = async () => {
    if (!videoRef.current || !canvasRef.current || !sessionId) return;
    setCapturing(true);

    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx?.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
      if (!blob) { setCapturing(false); return; }
      try {
        const data = await submitPracticeAttempt(
          sessionId, currentSign, blob, holdStartedAt.current ?? undefined
        );
        const score = data.assessment?.score ?? 0;
        setScores(prev => [...prev, { sign: currentSign, score, predicted: data.predicted_sign ?? null }]);
      } catch (e) {
        setScores(prev => [...prev, { sign: currentSign, score: 0, predicted: null }]);
      } finally {
        setCapturing(false);
        holdStartedAt.current = new Date().toISOString();

        if (qIdx < TOTAL) {
          setQIdx(q => q + 1);
        } else {
          if (sessionId && !sessionEndedRef.current) {
            sessionEndedRef.current = true;
            try {
              await generateFeedback(sessionId, currentSign);
              await endPracticeSession(sessionId, "completed");
            } catch (e) {
              // non-fatal — still proceed to feedback screen
            }
          }
          go("feedback");
        }
      }
    }, "image/jpeg", 0.9);
  };

  const avg = scores.length
    ? Math.round(scores.reduce((a, b) => a + b.score, 0) / scores.length)
    : 0;

  return (
    <div className="h-full bg-background flex flex-col overflow-hidden">
      <div className="bg-card border-b border-border px-6 py-3 flex-shrink-0">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h3 className="font-semibold text-foreground text-sm">Module 4 Assessment</h3>
            <p className="text-xs text-muted-foreground">Sign {qIdx} of {TOTAL} · Emotions &amp; Mental States</p>
          </div>
          {avg > 0 && <Bdg label={`${avg}% avg`} v="info" />}
        </div>
        <div className="flex gap-1">
          {Array.from({ length: TOTAL }, (_, i) => (
            <div
              key={i}
              className={`h-2 flex-1 rounded-full transition-all ${
                i < scores.length
                  ? scores[i].score >= 80 ? "bg-success" : scores[i].score >= 60 ? "bg-warning" : "bg-danger"
                  : i === qIdx - 1 ? "bg-primary animate-pulse" : "bg-muted"
              }`}
            />
          ))}
        </div>
        {sessionError && (
          <p className="text-xs text-rose-400 mt-2">{sessionError}</p>
        )}
      </div>

      <div className="flex-1 flex flex-col md:flex-row gap-5 p-5 overflow-hidden">
        <div className="flex-1 min-h-48 md:min-h-0 bg-muted rounded-[14px] border border-border relative overflow-hidden">
          <video
            ref={videoRef}
            autoPlay playsInline muted
            className="absolute inset-0 w-full h-full object-cover scale-x-[-1]"
          />
          <canvas ref={canvasRef} className="hidden" />

          {!cameraReady && !cameraError && (
            <div className="absolute inset-0 flex items-center justify-center">
              <HandOverlay w={240} h={300} animated />
            </div>
          )}

          {cameraError && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-center px-8">
              <AlertTriangle size={28} className="text-rose-400" />
              <p className="text-sm text-muted-foreground max-w-sm">{cameraError}</p>
            </div>
          )}

          {capturing && (
            <div className="absolute inset-0 flex items-center justify-center bg-background/60 backdrop-blur-sm">
              <div className="text-center">
                <Loader2 size={40} className="text-primary mb-2 animate-spin mx-auto" />
                <div className="text-sm text-muted-foreground">Analyzing…</div>
              </div>
            </div>
          )}
          <div className="absolute top-3 left-3 flex items-center gap-2 bg-card/80 backdrop-blur-sm px-2.5 py-1 rounded-full border border-border">
            <div className={`w-1.5 h-1.5 rounded-full animate-pulse ${cameraReady ? "bg-success" : "bg-muted-foreground"}`} />
            <span className="text-xs text-muted-foreground">{cameraReady ? "Camera active" : "Connecting..."}</span>
          </div>
        </div>

        <div className="w-full md:w-56 flex flex-col gap-3 flex-shrink-0">
          <div className="bg-card border border-border rounded-[14px] p-4" style={{ boxShadow: 'var(--card-shadow)' }}>
            <div className="text-xs text-muted-foreground mb-1">Sign this word:</div>
            <div className="text-4xl font-bold text-foreground mb-2">{currentSign}</div>
            <div className="flex items-center justify-center">
              <HandOverlay w={100} h={80} animated={false} />
            </div>
          </div>

          <button
            onClick={capture}
            disabled={capturing || !cameraReady || !sessionId}
            className={`py-3 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 ${
              capturing || !cameraReady || !sessionId
                ? "bg-muted text-muted-foreground cursor-not-allowed"
                : "bg-primary hover:bg-primary/90 text-primary-foreground"
            }`}
          >
            <Camera size={15} />
            {capturing ? "Capturing…" : "Capture Sign"}
          </button>

          {scores.length > 0 && (
            <div className="bg-card border border-border rounded-[14px] p-3 max-h-40 overflow-y-auto" style={{ boxShadow: 'var(--card-shadow)' }}>
              <div className="text-xs text-muted-foreground mb-2">Previous Scores</div>
              <div className="space-y-2">
                {scores.map((entry, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="text-xs text-muted-foreground w-14 truncate">{entry.sign}</div>
                    <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${entry.score >= 80 ? "bg-success" : entry.score >= 60 ? "bg-warning" : "bg-danger"}`}
                        style={{ width: `${entry.score}%` }}
                      />
                    </div>
                    <div className="text-xs font-semibold text-foreground">{Math.round(entry.score)}%</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={() => go("feedback")}
            className="flex items-center justify-center gap-2 text-xs text-muted-foreground hover:text-foreground border border-border rounded-xl py-2.5 transition-all hover:border-primary/30"
          >
            <ArrowRight size={13} />
            View Results
          </button>
        </div>
      </div>
    </div>
  );
}