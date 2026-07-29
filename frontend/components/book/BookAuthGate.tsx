"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useAuth } from "@/components/auth/AuthProvider";

type AuthMode = "signIn" | "register";

interface BookAuthGateProps {
  title: string;
}

export function BookAuthGate({ title }: BookAuthGateProps) {
  const { signIn, register, signInWithGoogle, isLoading, error, clearError } =
    useAuth();
  const [mode, setMode] = useState<AuthMode>("signIn");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);

  const displayError = localError ?? error;

  function switchMode(next: AuthMode) {
    setMode(next);
    setLocalError(null);
    clearError();
    if (next === "signIn") setConfirmPassword("");
  }

  async function handleEmailSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLocalError(null);
    clearError();

    const trimmed = email.trim();
    if (!trimmed) {
      setLocalError("Enter your email.");
      return;
    }
    if (password.length < 6) {
      setLocalError("Password must be at least 6 characters.");
      return;
    }
    if (mode === "register" && password !== confirmPassword) {
      setLocalError("Passwords do not match.");
      return;
    }

    try {
      if (mode === "register") {
        await register(trimmed, password);
      } else {
        await signIn(trimmed, password);
      }
    } catch {
      // error via context
    }
  }

  async function handleGoogle() {
    setLocalError(null);
    clearError();
    try {
      await signInWithGoogle();
    } catch {
      // error via context
    }
  }

  return (
    <motion.div
      className="flex min-h-dvh flex-col items-center justify-center bg-[#0a0614] px-6 py-12"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="w-full max-w-sm text-center">
        <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
          {title}
        </h1>
        <p className="mt-3 text-sm text-white/50">Login to continue reading.</p>

        <div className="mt-8 flex rounded-full border border-white/10 bg-white/5 p-1">
          {(["signIn", "register"] as const).map((key) => (
            <button
              key={key}
              type="button"
              onClick={() => switchMode(key)}
              className={`flex-1 rounded-full px-3 py-2 text-sm transition ${
                mode === key
                  ? "bg-white/15 text-white"
                  : "text-white/50 hover:text-white/80"
              }`}
            >
              {key === "signIn" ? "Login" : "Create Account"}
            </button>
          ))}
        </div>

        <form onSubmit={handleEmailSubmit} className="mt-6 space-y-3 text-left">
          <label className="block">
            <span className="mb-1.5 block text-xs text-white/45">Email</span>
            <input
              type="email"
              autoComplete="username"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full rounded-lg border border-white/15 bg-white/5 px-3 py-2.5 text-sm text-white placeholder:text-white/30 outline-none focus:border-ember-500/60"
            />
          </label>
          <label className="block">
            <span className="mb-1.5 block text-xs text-white/45">Password</span>
            <input
              type="password"
              autoComplete={
                mode === "signIn" ? "current-password" : "new-password"
              }
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="w-full rounded-lg border border-white/15 bg-white/5 px-3 py-2.5 text-sm text-white placeholder:text-white/30 outline-none focus:border-ember-500/60"
            />
          </label>
          {mode === "register" ? (
            <label className="block">
              <span className="mb-1.5 block text-xs text-white/45">
                Confirm password
              </span>
              <input
                type="password"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm password"
                className="w-full rounded-lg border border-white/15 bg-white/5 px-3 py-2.5 text-sm text-white placeholder:text-white/30 outline-none focus:border-ember-500/60"
              />
            </label>
          ) : null}

          <button
            type="submit"
            disabled={isLoading}
            className="mt-2 w-full rounded-full bg-ember-500 py-2.5 text-sm font-semibold text-white transition hover:brightness-110 disabled:opacity-60"
          >
            {isLoading
              ? "Please wait…"
              : mode === "signIn"
                ? "Login"
                : "Create Account"}
          </button>
        </form>

        <div className="my-5 flex items-center gap-3">
          <div className="h-px flex-1 bg-white/10" />
          <span className="text-xs text-white/35">or</span>
          <div className="h-px flex-1 bg-white/10" />
        </div>

        <button
          type="button"
          onClick={handleGoogle}
          disabled={isLoading}
          className="w-full rounded-full border border-white/15 py-2.5 text-sm text-white/80 transition hover:bg-white/5 disabled:opacity-60"
        >
          Continue with Google
        </button>

        {displayError ? (
          <p className="mt-4 text-sm text-red-300" role="alert">
            {displayError}
          </p>
        ) : null}
      </div>
    </motion.div>
  );
}
