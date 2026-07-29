"use client";

import { useState } from "react";
import { useAuth } from "@/components/auth/AuthProvider";

type AuthMode = "signIn" | "register";

export function LoginScreen() {
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
      // error surfaced via context
    }
  }

  async function handleGoogle() {
    setLocalError(null);
    clearError();
    try {
      await signInWithGoogle();
    } catch {
      // error surfaced via context
    }
  }

  return (
    <div className="auth-screen flex min-h-screen flex-col items-center justify-center px-6 py-12">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex justify-center">
          <img
            src="/momentra_logo_dark.svg"
            alt="Momentra"
            className="mx-auto h-auto w-full max-w-[280px]"
          />
        </div>

        <div className="auth-segment-track mb-6">
          {(["signIn", "register"] as const).map((key) => (
            <button
              key={key}
              type="button"
              onClick={() => switchMode(key)}
              className={`auth-segment-btn${mode === key ? " auth-segment-btn--active" : ""}`}
            >
              {key === "signIn" ? "Sign in" : "Register"}
            </button>
          ))}
        </div>

        <form onSubmit={handleEmailSubmit} className="space-y-4">
          <label className="block">
            <span className="auth-field-label">Email</span>
            <input
              type="email"
              autoComplete="username"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="auth-input"
            />
          </label>

          <label className="block">
            <span className="auth-field-label">Password</span>
            <input
              type="password"
              autoComplete={mode === "signIn" ? "current-password" : "new-password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="auth-input"
            />
          </label>

          {mode === "register" && (
            <label className="block">
              <span className="auth-field-label">Confirm password</span>
              <input
                type="password"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm password"
                className="auth-input"
              />
            </label>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="btn-celebrate btn-celebrate--block disabled:opacity-60"
          >
            {isLoading
              ? "Please wait…"
              : mode === "signIn"
                ? "Sign in"
                : "Create account"}
          </button>
        </form>

        <div className="my-6 flex items-center gap-3">
          <div className="auth-divider-line" />
          <span className="auth-divider">or</span>
          <div className="auth-divider-line" />
        </div>

        <button
          type="button"
          onClick={handleGoogle}
          disabled={isLoading}
          className="btn-ghost-on-dark disabled:opacity-60"
        >
          Continue with Google
        </button>

        {displayError && (
          <p className="auth-error mt-4" role="alert">
            {displayError}
          </p>
        )}
      </div>
    </div>
  );
}
