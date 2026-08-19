import { useState } from "react";
import {
  Eye,
  EyeOff,
  Lock,
  Mail,
} from "lucide-react";
import type { Role } from "@/app/utils/types";
import { loginUser, USE_MOCKS } from "../services/api";
import LoginDoodles from "../components/shared/LoginDoodles";

export default function LoginScreen({
  onLogin,
  goSignup,
}: {
  onLogin: (
    r: Role,
    token?: string,
    userId?: string,
    fullName?: string
  ) => void;
  goSignup: () => void;
}) {
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [show, setShow] = useState(false);
  const [selectedRole, setSelectedRole] = useState<Role>("learner");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    setLoading(true);
    setError(null);

    try {
      if (USE_MOCKS) {
        localStorage.setItem("role", selectedRole);
      }

      const data = await loginUser({
        email,
        password: pw,
        role: selectedRole,
      });

      onLogin(
        data.role as Role,
        data.access_token,
        data.user?.user_id,
        data.user?.full_name
      );
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Invalid email or password. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0d0d0d] flex">

      {/* =====================================================
          LEFT VISUAL AREA
      ===================================================== */}
      <div className="hidden lg:flex w-[45%] bg-[#0d0d0d] relative overflow-hidden">

        {/* =================================================
            CHARACTER IMAGES
            z-20 = ABOVE BACKGROUND
        ================================================= */}

        {/* Character 1 */}
        <img
          src="/characters/character-1.png"
          alt=""
          aria-hidden="true"
          className="
            absolute
            z-20
            w-20
            top-12
            left-8
            object-contain
          "
        />

        {/* Character 2 */}
        <img
          src="/characters/character-2.png"
          alt=""
          aria-hidden="true"
          className="
            absolute
            z-20
            w-20
            top-16
            right-8
            object-contain
          "
        />

        {/* Character 3 */}
        <img
          src="/characters/character-3.png"
          alt=""
          aria-hidden="true"
          className="
            absolute
            z-20
            w-20
            top-1/2
            left-6
            -translate-y-1/2
            object-contain
          "
        />

        {/* Character 4 */}
        <img
          src="/characters/character-4.png"
          alt=""
          aria-hidden="true"
          className="
            absolute
            z-20
            w-20
            top-1/2
            right-6
            -translate-y-1/2
            object-contain
          "
        />

        {/* Character 5 */}
        <img
          src="/characters/character-5.png"
          alt=""
          aria-hidden="true"
          className="
            absolute
            z-20
            w-20
            bottom-10
            left-10
            object-contain
          "
        />

        {/* Character 6 */}
        <img
          src="/characters/character-6.png"
          alt=""
          aria-hidden="true"
          className="
            absolute
            z-20
            w-20
            bottom-10
            right-10
            object-contain
          "
        />


        {/* =================================================
            WHITE DOODLES
            z-30 = ABOVE CHARACTER CARDS
        ================================================= */}
        <LoginDoodles />


        {/* =================================================
            MAIN VIDEO
            z-40 = ABOVE DOODLES
        ================================================= */}
        <div
          className="
            absolute
            z-40
            left-1/2
            top-[54%]
            -translate-x-1/2
            -translate-y-1/2
          "
        >
          <div
            className="
              w-[330px]
              h-[520px]
              overflow-hidden
              rounded-2xl
              bg-black
              shadow-2xl
              border
              border-white/10
            "
          >
            <video
              autoPlay
              muted
              loop
              playsInline
              src="/sign-language-video.mp4"
              className="
                w-full
                h-full
                object-cover
                object-center
              "
            />
          </div>
        </div>

      </div>


      {/* =====================================================
          RIGHT LOGIN AREA
      ===================================================== */}
      <div
        className="
          flex-1
          flex
          flex-col
          items-center
          justify-center
          p-8
          bg-[#0d0d0d]
        "
      >

        <div className="w-full max-w-sm">

          {/* Header */}
          <div className="mb-7">
            <h2 className="text-2xl font-bold text-foreground mb-1">
              Welcome back
            </h2>

            <p className="text-muted-foreground text-sm">
              Sign in to continue your learning journey
            </p>
          </div>


          {/* Role selector */}
          <div className="flex gap-1 mb-5 p-1 bg-[#0e1a30] rounded-xl">
            {(
              ["learner", "instructor", "trainer", "admin"] as Role[]
            ).map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => setSelectedRole(r)}
                className={`
                  flex-1
                  py-1.5
                  text-[11px]
                  font-semibold
                  rounded-lg
                  capitalize
                  transition-all
                  ${
                    selectedRole === r
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:text-foreground"
                  }
                `}
              >
                {r}
              </button>
            ))}
          </div>


          {/* Email + Password */}
          <div className="space-y-4 mb-5">

            {/* Email */}
            <div>
              <label className="text-xs font-semibold text-foreground mb-1.5 block">
                Email
              </label>

              <div className="relative">
                <Mail
                  size={15}
                  className="
                    absolute
                    left-3
                    top-1/2
                    -translate-y-1/2
                    text-muted-foreground
                  "
                />

                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="
                    w-full
                    bg-[#0e1a30]
                    border
                    border-border
                    rounded-lg
                    pl-9
                    pr-4
                    py-2.5
                    text-foreground
                    text-sm
                    focus:outline-none
                    focus:border-primary/50
                    focus:ring-1
                    focus:ring-primary/20
                  "
                  placeholder="you@example.com"
                />
              </div>
            </div>


            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold text-foreground">
                  Password
                </label>

                <button
                  type="button"
                  className="
                    text-xs
                    text-primary
                    hover:text-primary-active
                  "
                >
                  Forgot password?
                </button>
              </div>

              <div className="relative">

                <Lock
                  size={15}
                  className="
                    absolute
                    left-3
                    top-1/2
                    -translate-y-1/2
                    text-muted-foreground
                  "
                />

                <input
                  type={show ? "text" : "password"}
                  value={pw}
                  onChange={(e) => setPw(e.target.value)}
                  className="
                    w-full
                    bg-[#0e1a30]
                    border
                    border-border
                    rounded-lg
                    pl-9
                    pr-10
                    py-2.5
                    text-foreground
                    text-sm
                    focus:outline-none
                    focus:border-primary/50
                  "
                  placeholder="Enter your password"
                />

                <button
                  type="button"
                  onClick={() => setShow(!show)}
                  className="
                    absolute
                    right-3
                    top-1/2
                    -translate-y-1/2
                    text-muted-foreground
                    hover:text-foreground
                  "
                  aria-label={
                    show
                      ? "Hide password"
                      : "Show password"
                  }
                >
                  {show ? (
                    <EyeOff size={15} />
                  ) : (
                    <Eye size={15} />
                  )}
                </button>

              </div>
            </div>

          </div>


          {/* Error */}
          {error && (
            <div
              className="
                mb-4
                px-3
                py-2.5
                rounded-lg
                bg-rose-950/40
                border
                border-rose-900/40
                text-rose-400
                text-xs
              "
            >
              {error}
            </div>
          )}


          {/* Sign in */}
          <button
            type="button"
            onClick={handleLogin}
            disabled={loading}
            className="
              w-full
              bg-primary
              hover:bg-primary-active
              disabled:opacity-60
              disabled:cursor-not-allowed
              text-black
              font-bold
              py-3
              rounded-xl
              transition-colors
              mb-4
              text-sm
            "
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>


          {/* OR */}
          <div className="relative flex items-center gap-3 mb-4">
            <div className="flex-1 h-px bg-border" />

            <span className="text-xs text-muted-foreground">
              or
            </span>

            <div className="flex-1 h-px bg-border" />
          </div>


          {/* Google */}
          <button
            type="button"
            className="
              w-full
              bg-[#0e1a30]
              border
              border-border
              hover:border-primary/30
              text-foreground
              font-medium
              py-2.5
              rounded-xl
              transition-all
              flex
              items-center
              justify-center
              gap-3
              mb-6
              text-sm
            "
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 18 18"
              aria-hidden="true"
            >
              <path
                fill="#4285F4"
                d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 0 1-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"
              />

              <path
                fill="#34A853"
                d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z"
              />

              <path
                fill="#FBBC05"
                d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z"
              />

              <path
                fill="#EA4335"
                d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"
              />
            </svg>

            Continue with Google
          </button>


          {/* Signup */}
          <p className="text-center text-xs text-muted-foreground">
            New to SignPath?{" "}

            <button
              type="button"
              onClick={goSignup}
              className="
                text-primary
                hover:text-primary-active
                font-semibold
              "
            >
              Create an account
            </button>
          </p>

        </div>
      </div>

    </div>
  );
}