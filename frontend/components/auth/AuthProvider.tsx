"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  exchangeFirebaseToken,
  fetchMe,
  logout as apiLogout,
  refreshAccessToken,
  ApiError,
} from "@/lib/api/client";
import type { UserResponse } from "@/lib/api/types";
import {
  clearProactiveTokenRefresh,
  scheduleProactiveTokenRefresh,
} from "@/lib/auth/tokenRefresh";
import { clearSessionOnLogout } from "@/stores/sessionStore";
import {
  clearTokens,
  getAccessToken,
  hasStoredSession,
  loadCachedUser,
  saveCachedUser,
} from "@/lib/auth/tokens";
import {
  getFirebaseIdToken,
  registerWithEmail,
  signInWithEmail,
  signInWithGoogle,
  signOutFirebase,
  getFirebaseAuth,
} from "@/lib/firebase";
import { MomentraAnalytics } from "@/lib/analytics";
import { startLoginToPulseSpan, markAuthValidated } from "@/lib/telemetry/performanceTelemetry";

interface AuthContextValue {
  user: UserResponse | null;
  isLoading: boolean;
  isRestoring: boolean;
  error: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  setUser: (user: UserResponse) => void;
  clearError: () => void;
  clearSessionAndShowLogin: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const RESTORE_TIMEOUT_MS = 15_000;

function formatAuthError(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 408 || err.status === 0) {
      return err.message;
    }
    return err.userMessage;
  }
  return err instanceof Error ? err.message : "Authentication failed";
}

async function exchangeAndLoadProfile(): Promise<UserResponse> {
  const { getFirebaseAuth } = await import("@/lib/firebase");
  const firebaseUser = getFirebaseAuth().currentUser;
  if (!firebaseUser) throw new Error("Firebase sign-in did not complete.");
  const idToken = await getFirebaseIdToken(firebaseUser);
  const response = await exchangeFirebaseToken(idToken);
  scheduleProactiveTokenRefresh();
  return response.user;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRestoring, setIsRestoring] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const restoreAttemptRef = useRef(0);

  const clearSessionAndShowLogin = useCallback(() => {
    clearTokens();
    clearProactiveTokenRefresh();
    void signOutFirebase().catch(() => undefined);
    setUser(null);
    setIsRestoring(false);
    setError(null);
  }, []);

  useEffect(() => {
    const attempt = ++restoreAttemptRef.current;

    async function restore() {
      if (!hasStoredSession()) {
        return;
      }
      const cached = loadCachedUser();
      if (cached) {
        setUser(cached);
      }
      setIsRestoring(true);
      setError(null);
      try {
        // Memory access tokens die on reload; restore via HttpOnly cookie
        // (or one-time legacy localStorage refresh migration).
        if (!getAccessToken()) {
          await refreshAccessToken();
        }
        const profile = await Promise.race([
          fetchMe(),
          new Promise<never>((_, reject) => {
            window.setTimeout(
              () =>
                reject(
                  new Error(
                    "Session restore timed out. Check that the backend and ngrok tunnel are running.",
                  ),
                ),
              RESTORE_TIMEOUT_MS,
            );
          }),
        ]);
        if (attempt !== restoreAttemptRef.current) return;
        setUser(profile);
        saveCachedUser(profile);
        startLoginToPulseSpan();
        scheduleProactiveTokenRefresh();
        const firebaseUser = getFirebaseAuth().currentUser;
        void MomentraAnalytics.setUser(profile, firebaseUser);
        markAuthValidated();
      } catch (err) {
        if (attempt !== restoreAttemptRef.current) return;
        clearTokens();
        clearProactiveTokenRefresh();
        void signOutFirebase().catch(() => undefined);
        setUser(null);
        setError(formatAuthError(err));
      } finally {
        if (attempt === restoreAttemptRef.current) {
          setIsRestoring(false);
        }
      }
    }

    void restore();
  }, []);

  const runAuth = useCallback(
    async (action: () => Promise<UserResponse>, method: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const profile = await action();
        setUser(profile);
        saveCachedUser(profile);
        startLoginToPulseSpan();
        const firebaseUser = getFirebaseAuth().currentUser;
        void MomentraAnalytics.setUser(profile, firebaseUser);
        void MomentraAnalytics.logSignIn(method);
      } catch (err) {
        const message = formatAuthError(err);
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const signIn = useCallback(
    async (email: string, password: string) => {
      await runAuth(async () => {
        await signInWithEmail(email, password);
        return exchangeAndLoadProfile();
      }, "email");
    },
    [runAuth],
  );

  const register = useCallback(
    async (email: string, password: string) => {
      await runAuth(async () => {
        await registerWithEmail(email, password);
        return exchangeAndLoadProfile();
      }, "email");
    },
    [runAuth],
  );

  const signInWithGoogleHandler = useCallback(async () => {
    await runAuth(async () => {
      await signInWithGoogle();
      return exchangeAndLoadProfile();
    }, "google");
  }, [runAuth]);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await apiLogout();
    } catch {
      clearSessionOnLogout();
    } finally {
      clearSessionOnLogout();
      void signOutFirebase().catch(() => undefined);
      void MomentraAnalytics.logSignOut();
      void MomentraAnalytics.clearUser();
      setUser(null);
      setIsLoading(false);
    }
  }, []);

  const clearError = useCallback(() => setError(null), []);

  const refreshUser = useCallback(async () => {
    const profile = await fetchMe();
    setUser(profile);
    saveCachedUser(profile);
    const firebaseUser = getFirebaseAuth().currentUser;
    void MomentraAnalytics.setUser(profile, firebaseUser);
    scheduleProactiveTokenRefresh();
  }, []);

  const setUserDirect = useCallback((profile: UserResponse) => {
    setUser(profile);
    saveCachedUser(profile);
    const firebaseUser = getFirebaseAuth().currentUser;
    void MomentraAnalytics.setUser(profile, firebaseUser);
  }, []);

  const value = useMemo(
    () => ({
      user,
      isLoading,
      isRestoring,
      error,
      signIn,
      register,
      signInWithGoogle: signInWithGoogleHandler,
      logout,
      refreshUser,
      setUser: setUserDirect,
      clearError,
      clearSessionAndShowLogin,
    }),
    [
      user,
      isLoading,
      isRestoring,
      error,
      signIn,
      register,
      signInWithGoogleHandler,
      logout,
      refreshUser,
      setUserDirect,
      clearError,
      clearSessionAndShowLogin,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
