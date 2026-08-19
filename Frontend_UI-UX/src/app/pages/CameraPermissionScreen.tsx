import { useState, useEffect } from "react";
import {
  Home, BookOpen, Camera, CheckSquare, MessageCircle, TrendingUp,
  Award, Users, Settings, Bell, ChevronRight, Play, RotateCcw,
  ArrowRight, Eye, EyeOff, Clock, Zap, Target, Activity,
  Shield, Server, UserCheck, LogOut, Plus, Search, Filter,
  Download, Share2, AlertTriangle, CheckCircle, XCircle, Info,
  SkipForward, Calendar, Lock, Mail, Check, ChevronLeft,
} from "lucide-react";
import type { Screen } from "../lib/types";

export default function CameraPermissionScreen({ go }: { go: (s: Screen) => void }) {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center max-w-sm px-4">
        <div className="w-24 h-24 rounded-full bg-muted border-2 border-dashed border-border flex items-center justify-center mx-auto mb-6">
          <Camera size={34} className="text-muted-foreground" />
        </div>
        <h3 className="text-xl font-bold text-foreground mb-2">Allow Camera Access</h3>
        <p className="text-muted-foreground text-sm mb-6 leading-relaxed">
          SignPath AI uses your camera to analyze hand gestures in real-time. Your video is processed locally and never stored on our servers.
        </p>
        <div className="bg-card border border-border rounded-[14px] p-5 mb-6 space-y-3 text-left" style={{ boxShadow: 'var(--card-shadow)' }}>
          {["Video stays on your device", "No recordings saved to servers", "Revoke access anytime in Settings"].map(t => (
            <div key={t} className="flex items-center gap-2.5 text-xs text-muted-foreground">
              <Check size={12} className="text-success flex-shrink-0" />
              {t}
            </div>
          ))}
        </div>
        <button
          onClick={() => go("practice")}
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-bold py-3.5 rounded-xl transition-colors mb-3 shadow-sm"
        >
          Allow Camera Access
        </button>
        <button className="text-xs text-muted-foreground hover:text-foreground transition-colors">
          Maybe later
        </button>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════
// MAIN APP
// ══════════════════════════════════════════════════════════════════════════
