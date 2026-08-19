/**
 * CertificationExam.tsx — M4 Day 3 (Intern 1 + Intern 4)
 *
 * Implements the Certification Exam workflow (SRS Section 9 / FR-4):
 *   4 levels: Beginner / Intermediate / Advanced / Professional
 *   Flow: pick level → webcam attempt per sign → pass/fail result → PDF certificate
 *
 * Wired to real Business Logic service (port 8002) via:
 *   getCertificationLevels, startCertificationExam, recordCertificationAttempt,
 *   completeCertificationExam, downloadCertificationCertificate
 *   (all confirmed from certification.py + schemas/certification.py)
 *
 * AI prediction comes from submitPracticeAttempt (Business Logic forwards to
 * Intern 3's AI service internally — same pattern as PracticeScreen).
 * We re-use that endpoint here so we get scoring + prediction in one call,
 * then feed predicted_sign + confidence into recordCertificationAttempt.
 */

import { useState, useEffect, useRef } from "react";
import {
  Camera, CheckCircle, XCircle, Award, ChevronRight,
  Loader2, AlertTriangle, RotateCcw, Download,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import {
  getCertificationLevels,
  startCertificationExam,
  recordCertificationAttempt,
  completeCertificationExam,
  downloadCertificationCertificate,
} from "../services/businessApi";
import { startPracticeSession, submitPracticeAttempt } from "../services/businessApi";
import type { Screen } from "../lib/types";

// ── Types ────────────────────────────────────────────────────────────────────

interface LevelInfo {
  level: string;
  num_signs: number;
  pass_threshold: number;
  description: string;
}

interface ExamState {
  exam_id: string;
  required_signs: string[];
  level: string;
}

interface AttemptResult {
  predicted_sign: string;
  is_correct: boolean;
  attempt_score: number;
  signs_completed: number;
  signs_remaining: number;
  exam_status: string;
}

interface ExamResult {
  passed: boolean;
  score: number;
  accuracy_percentage: number;
  correct_predictions: number;
  total_predictions: number;
  pass_threshold: number;
  level: string;
  exam_id: string;
}

type Phase =
  | "level-select"
  | "ready"         // level chosen, about to start
  | "capturing"     // webcam active, waiting for capture
  | "processing"    // frame sent, waiting for result
  | "attempt-done"  // showing per-sign result before next
  | "exam-complete" // showing final pass/fail
  | "error";

const LEVEL_COLORS: Record<string, string> = {
  beginner:     "text-emerald-400 border-emerald-400/30 bg-emerald-400/5",
  intermediate: "text-amber-400 border-amber-400/30 bg-amber-400/5",
  advanced:     "text-violet-400 border-violet-400/30 bg-violet-400/5",
  professional: "text-primary border-primary/30 bg-primary/5",
};

// ── Component ────────────────────────────────────────────────────────────────

export default function CertificationExam({ go }: { go: (s: Screen) => void }) {
  const { userId, fullName } = useAuth();
  const uid = userId ?? "00000000-0000-0000-0000-000000000001";
  const learnerName = fullName ?? "Learner";

  const [phase, setPhase] = useState<Phase>("level-select");
  const [levels, setLevels] = useState<LevelInfo[]>([]);
  const [selectedLevel, setSelectedLevel] = useState<LevelInfo | null>(null);
  const [exam, setExam] = useState<ExamState | null>(null);
  const [currentSignIndex, setCurrentSignIndex] = useState(0);
  const [lastAttempt, setLastAttempt] = useState<AttemptResult | null>(null);
  const [result, setResult] = useState<ExamResult | null>(null);
  const [practiceSessionId, setPracticeSessionId] = useState<string | null>(null);
  const [certDownloading, setCertDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Load levels on mount
  useEffect(() => {
    getCertificationLevels()
      .then(setLevels)
      .catch(() => setError("Couldn't load certification levels. Is the Business Logic service running on port 8002?"));
  }, []);

  // Start webcam when entering capturing phase
  useEffect(() => {
    if (phase === "capturing") {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
          streamRef.current = stream;
          if (videoRef.current) videoRef.current.srcObject = stream;
        })
        .catch(() => setError("Camera access denied. Please allow camera access and try again."));
    } else {
      // Stop stream when not capturing
      streamRef.current?.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
    return () => {
      streamRef.current?.getTracks().forEach(t => t.stop());
    };
  }, [phase]);

  // ── Handlers ────────────────────────────────────────────────────────────────

  async function handleStartExam() {
    if (!selectedLevel) return;
    setError(null);
    try {
      const [examData, session] = await Promise.all([
        startCertificationExam(uid, selectedLevel.level),
        startPracticeSession(uid, 1), // lesson_id=1 as placeholder; exam doesn't use it
      ]);
      setExam({
        exam_id: examData.exam_id,
        required_signs: examData.required_signs,
        level: examData.level,
      });
      setPracticeSessionId(session.session_id);
      setCurrentSignIndex(0);
      setPhase("capturing");
    } catch (e: any) {
      setError(`Failed to start exam: ${e.message}`);
      setPhase("error");
    }
  }

  async function handleCapture() {
    if (!exam || !videoRef.current || !practiceSessionId) return;
    setPhase("processing");

    try {
      const canvas = document.createElement("canvas");
      canvas.width = videoRef.current.videoWidth || 640;
      canvas.height = videoRef.current.videoHeight || 480;
      canvas.getContext("2d")!.drawImage(videoRef.current, 0, 0);
      const blob = await new Promise<Blob>(res => canvas.toBlob(b => res(b!), "image/jpeg", 0.85));

      const expectedSign = exam.required_signs[currentSignIndex];

      // Submit through Business Logic (forwards to AI service, returns prediction + score)
      const attemptData = await submitPracticeAttempt(practiceSessionId, expectedSign, blob, new Date().toISOString());

      const predictedSign: string = attemptData.predicted_sign ?? "";
      const confidence: number = attemptData.confidence ?? 0;
      const holdSeconds: number | null = attemptData.hold_seconds ?? null;

      // Record the attempt in the certification exam
      const certAttempt = await recordCertificationAttempt(
        exam.exam_id,
        expectedSign,
        predictedSign,
        confidence,
        holdSeconds
      );

      setLastAttempt(certAttempt);
      setPhase("attempt-done");
    } catch (e: any) {
      setError(`Prediction failed: ${e.message}`);
      setPhase("error");
    }
  }

  async function handleNextSign() {
    if (!exam || !lastAttempt) return;
    const nextIndex = currentSignIndex + 1;

    if (lastAttempt.signs_remaining === 0 || nextIndex >= exam.required_signs.length) {
      // All signs done — complete the exam
      try {
        const finalResult = await completeCertificationExam(exam.exam_id);
        setResult({
          passed: finalResult.passed,
          score: finalResult.score,
          accuracy_percentage: finalResult.accuracy_percentage,
          correct_predictions: finalResult.correct_predictions,
          total_predictions: finalResult.total_predictions,
          pass_threshold: finalResult.pass_threshold,
          level: finalResult.level,
          exam_id: finalResult.exam_id,
        });
        setPhase("exam-complete");
      } catch (e: any) {
        setError(`Failed to complete exam: ${e.message}`);
        setPhase("error");
      }
    } else {
      setCurrentSignIndex(nextIndex);
      setPhase("capturing");
    }
  }

  async function handleDownloadCertificate() {
    if (!result?.exam_id || !result.passed) return;
    setCertDownloading(true);
    try {
      const blob = await downloadCertificationCertificate(result.exam_id, learnerName);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `certification_${result.level}_${result.exam_id.slice(0, 8)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(`Certificate download failed: ${e.message}`);
    } finally {
      setCertDownloading(false);
    }
  }

  function handleRetry() {
    setPhase("level-select");
    setExam(null);
    setLastAttempt(null);
    setResult(null);
    setPracticeSessionId(null);
    setCurrentSignIndex(0);
    setError(null);
  }

  // ── Render ───────────────────────────────────────────────────────────────────

  if (error && phase === "error") {
    return (
      <div className="p-8 max-w-lg mx-auto text-center space-y-4">
        <AlertTriangle size={32} className="mx-auto text-warning" />
        <p className="text-sm text-foreground">{error}</p>
        <button onClick={handleRetry} className="inline-flex items-center gap-2 text-sm text-primary underline">
          <RotateCcw size={13} /> Try again
        </button>
      </div>
    );
  }

  // ── Level Select ─────────────────────────────────────────────────────────────
  if (phase === "level-select") {
    return (
      <div className="p-8 max-w-2xl mx-auto space-y-6">
        <div>
          <h2 className="text-lg font-bold text-foreground">Certification Exam</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Choose a level and prove your sign language proficiency. Each exam tests a fixed set of signs;
            pass the threshold to earn a certificate.
          </p>
        </div>

        {levels.length === 0 ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 size={13} className="animate-spin" /> Loading levels…
          </div>
        ) : (
          <div className="grid gap-3">
            {levels.map(lvl => {
              const isSelected = selectedLevel?.level === lvl.level;
              const colCls = LEVEL_COLORS[lvl.level] ?? "text-foreground border-border bg-muted/30";
              return (
                <button
                  key={lvl.level}
                  onClick={() => setSelectedLevel(lvl)}
                  className={`w-full text-left border rounded-xl p-4 transition-all ${colCls} ${
                    isSelected ? "ring-2 ring-primary/40" : "hover:opacity-80"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold capitalize">{lvl.level}</div>
                      <div className="text-xs text-muted-foreground mt-0.5">{lvl.description}</div>
                    </div>
                    <div className="text-right text-xs ml-4 flex-shrink-0">
                      <div className="font-semibold">{lvl.num_signs} signs</div>
                      <div className="text-muted-foreground">{Math.round(lvl.pass_threshold)}% to pass</div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        <button
          onClick={() => setPhase("ready")}
          disabled={!selectedLevel}
          className="w-full py-3 rounded-xl bg-primary text-white font-semibold text-sm disabled:opacity-40 hover:bg-primary/90 transition-colors flex items-center justify-center gap-2"
        >
          Continue <ChevronRight size={15} />
        </button>
      </div>
    );
  }

  // ── Ready ────────────────────────────────────────────────────────────────────
  if (phase === "ready") {
    return (
      <div className="p-8 max-w-lg mx-auto space-y-6 text-center">
        <Award size={40} className="mx-auto text-primary" />
        <div>
          <h2 className="text-lg font-bold text-foreground capitalize">{selectedLevel?.level} Certification</h2>
          <p className="text-sm text-muted-foreground mt-1">
            You'll be asked to sign {selectedLevel?.num_signs} signs one at a time using your webcam.
            Score at least {Math.round(selectedLevel?.pass_threshold ?? 0)}% to pass.
          </p>
        </div>
        <ul className="text-sm text-muted-foreground space-y-1 text-left bg-muted/40 rounded-xl p-4">
          <li>• Make sure your hand is clearly visible and well-lit</li>
          <li>• Hold the sign steady, then click Capture</li>
          <li>• Each sign gets one attempt — take your time</li>
          <li>• The exam is timed per your practice — pace yourself</li>
        </ul>
        <div className="flex gap-3">
          <button onClick={() => setPhase("level-select")} className="flex-1 py-3 rounded-xl border border-border text-sm text-muted-foreground hover:text-foreground transition-colors">
            Back
          </button>
          <button onClick={handleStartExam} className="flex-1 py-3 rounded-xl bg-primary text-white font-semibold text-sm hover:bg-primary/90 transition-colors flex items-center justify-center gap-2">
            <Camera size={14} /> Start Exam
          </button>
        </div>
      </div>
    );
  }

  // ── Capturing / Processing ───────────────────────────────────────────────────
  if (phase === "capturing" || phase === "processing") {
    const currentSign = exam?.required_signs[currentSignIndex] ?? "?";
    const total = exam?.required_signs.length ?? 0;
    const isProcessing = phase === "processing";

    return (
      <div className="p-8 max-w-xl mx-auto space-y-5">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground capitalize">{exam?.level} Certification</span>
          <span className="text-muted-foreground">Sign {currentSignIndex + 1} of {total}</span>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-muted rounded-full h-1.5">
          <div
            className="bg-primary h-1.5 rounded-full transition-all"
            style={{ width: `${((currentSignIndex) / total) * 100}%` }}
          />
        </div>

        {/* Target sign */}
        <div className="text-center">
          <div className="text-xs text-muted-foreground mb-1">Sign this letter:</div>
          <div className="text-7xl font-black text-primary">{currentSign}</div>
        </div>

        {/* Webcam */}
        <div className="relative bg-black rounded-2xl overflow-hidden aspect-video">
          <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
          {isProcessing && (
            <div className="absolute inset-0 bg-black/50 flex flex-col items-center justify-center gap-2">
              <Loader2 size={24} className="animate-spin text-white" />
              <span className="text-white text-sm">Analyzing sign…</span>
            </div>
          )}
        </div>

        <button
          onClick={handleCapture}
          disabled={isProcessing}
          className="w-full py-3.5 rounded-xl bg-primary text-white font-semibold text-sm disabled:opacity-50 hover:bg-primary/90 transition-colors flex items-center justify-center gap-2"
        >
          {isProcessing ? <Loader2 size={14} className="animate-spin" /> : <Camera size={14} />}
          {isProcessing ? "Processing…" : "Capture Sign"}
        </button>
      </div>
    );
  }

  // ── Attempt Done ──────────────────────────────────────────────────────────────
  if (phase === "attempt-done" && lastAttempt) {
    const total = exam?.required_signs.length ?? 0;
    const isLast = lastAttempt.signs_remaining === 0;

    return (
      <div className="p-8 max-w-xl mx-auto space-y-5">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground capitalize">{exam?.level} Certification</span>
          <span className="text-muted-foreground">
            {lastAttempt.signs_completed} / {total} done
          </span>
        </div>

        <div className={`rounded-2xl p-6 text-center border ${
          lastAttempt.is_correct
            ? "border-emerald-400/30 bg-emerald-400/5"
            : "border-rose-400/30 bg-rose-400/5"
        }`}>
          {lastAttempt.is_correct
            ? <CheckCircle size={32} className="mx-auto text-emerald-400 mb-2" />
            : <XCircle size={32} className="mx-auto text-rose-400 mb-2" />
          }
          <div className="font-bold text-lg text-foreground">
            {lastAttempt.is_correct ? "Correct!" : "Missed"}
          </div>
          <div className="text-sm text-muted-foreground mt-1">
            Expected <span className="font-semibold text-foreground">{lastAttempt.expected_sign}</span>
            {" "}— you signed{" "}
            <span className="font-semibold text-foreground">{lastAttempt.predicted_sign || "?"}</span>
          </div>
          <div className="text-xs text-muted-foreground mt-2">
            Attempt score: <span className="font-semibold">{Math.round(lastAttempt.attempt_score)}</span>
          </div>
        </div>

        <button
          onClick={handleNextSign}
          className="w-full py-3.5 rounded-xl bg-primary text-white font-semibold text-sm hover:bg-primary/90 transition-colors flex items-center justify-center gap-2"
        >
          {isLast ? "See Results" : "Next Sign"}
          <ChevronRight size={14} />
        </button>
      </div>
    );
  }

  // ── Exam Complete ─────────────────────────────────────────────────────────────
  if (phase === "exam-complete" && result) {
    const pct = Math.round(result.accuracy_percentage);
    const threshold = Math.round(result.pass_threshold);

    return (
      <div className="p-8 max-w-xl mx-auto space-y-6 text-center">
        <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full mx-auto ${
          result.passed ? "bg-emerald-400/10 text-emerald-400" : "bg-rose-400/10 text-rose-400"
        }`}>
          {result.passed ? <Award size={32} /> : <XCircle size={32} />}
        </div>

        <div>
          <h2 className={`text-xl font-black ${result.passed ? "text-emerald-400" : "text-rose-400"}`}>
            {result.passed ? "Congratulations!" : "Not Quite"}
          </h2>
          <p className="text-sm text-muted-foreground mt-1 capitalize">
            {result.level} Certification — {result.passed ? "Passed ✓" : "Not passed"}
          </p>
        </div>

        <div className="bg-card border border-border rounded-xl p-5 text-left space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Score</span>
            <span className="font-semibold text-foreground">{Math.round(result.score)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Accuracy</span>
            <span className="font-semibold text-foreground">{pct}%</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Correct Signs</span>
            <span className="font-semibold text-foreground">{result.correct_predictions} / {result.total_predictions}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Pass Threshold</span>
            <span className={`font-semibold ${result.passed ? "text-emerald-400" : "text-rose-400"}`}>
              {threshold}% {result.passed ? "✓" : `(needed ${threshold}%)`}
            </span>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleRetry}
            className="flex-1 py-3 rounded-xl border border-border text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center justify-center gap-2"
          >
            <RotateCcw size={13} /> Try Again
          </button>

          {result.passed && (
            <button
              onClick={handleDownloadCertificate}
              disabled={certDownloading}
              className="flex-1 py-3 rounded-xl bg-primary text-white font-semibold text-sm hover:bg-primary/90 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
            >
              {certDownloading
                ? <Loader2 size={13} className="animate-spin" />
                : <Download size={13} />
              }
              {certDownloading ? "Generating…" : "Download Certificate"}
            </button>
          )}
        </div>

        <button
          onClick={() => go("certificates")}
          className="text-sm text-primary underline"
        >
          View all certificates →
        </button>
      </div>
    );
  }

  return null;
}