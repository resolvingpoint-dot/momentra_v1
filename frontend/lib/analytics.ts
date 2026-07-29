import {
  getAnalytics,
  isSupported,
  logEvent,
  setUserId,
  setUserProperties,
  type Analytics,
  type CustomParams,
} from "firebase/analytics";
import type { User } from "firebase/auth";
import type { AppContext } from "@/lib/appContext";
import type { UserResponse } from "@/lib/api/types";
import { getFirebaseApp } from "@/lib/firebase";

const APP_PLATFORM = "web";

/** Skip Analytics when Web app credentials are missing or still placeholders. */
function isFirebaseAnalyticsConfigured(): boolean {
  const appId = process.env.NEXT_PUBLIC_FIREBASE_APP_ID?.trim();
  const measurementId = process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID?.trim();
  if (!appId || !measurementId) return false;
  // Placeholder from .env.example before registering a Web app in Firebase Console
  if (/0{10,}/.test(appId)) return false;
  return true;
}

let analytics: Analytics | null = null;
let initPromise: Promise<Analytics | null> | null = null;
let configWarningLogged = false;

async function getMomentraAnalytics(): Promise<Analytics | null> {
  if (typeof window === "undefined") return null;
  if (!isFirebaseAnalyticsConfigured()) {
    if (process.env.NODE_ENV === "development" && !configWarningLogged) {
      configWarningLogged = true;
      console.info(
        "[Momentra] Firebase Analytics disabled: set NEXT_PUBLIC_FIREBASE_APP_ID and NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID from Firebase Console → Project settings → Your apps → Web.",
      );
    }
    return null;
  }
  if (analytics) return analytics;
  if (!initPromise) {
    initPromise = (async () => {
      try {
        const supported = await isSupported();
        if (!supported) return null;
        analytics = getAnalytics(getFirebaseApp());
        return analytics;
      } catch (error) {
        if (process.env.NODE_ENV === "development") {
          console.warn("[Momentra] Firebase Analytics init failed:", error);
        }
        return null;
      }
    })();
  }
  return initPromise;
}

function authProviderFrom(firebaseUser: User | null | undefined): string {
  const providers = firebaseUser?.providerData.map((p) => p.providerId) ?? [];
  if (providers.includes("google.com")) return "google";
  if (providers.includes("password")) return "email";
  if (providers.includes("apple.com")) return "apple";
  return "unknown";
}

export const MomentraAnalytics = {
  async logScreen(screenName: string, appContext?: AppContext | null) {
    const a = await getMomentraAnalytics();
    if (!a) return;
    logEvent(a, "screen_view", {
      firebase_screen: screenName,
      firebase_screen_class: screenName,
      app_platform: APP_PLATFORM,
      ...(appContext ? { app_context: appContext } : {}),
    });
  },

  async logCustomEvent(name: string, params: Record<string, string> = {}) {
    const a = await getMomentraAnalytics();
    if (!a) return;
    logEvent(a, name, { app_platform: APP_PLATFORM, ...params } as CustomParams);
  },

  async setUser(profile: UserResponse, firebaseUser: User | null) {
    const a = await getMomentraAnalytics();
    if (!a) return;
    setUserId(a, profile.id);
    setUserProperties(a, {
      firebase_uid: firebaseUser?.uid ?? "",
      auth_provider: authProviderFrom(firebaseUser),
      has_avatar: profile.photo_url ? "true" : "false",
      app_platform: APP_PLATFORM,
    });
  },

  async clearUser() {
    const a = await getMomentraAnalytics();
    if (!a) return;
    setUserId(a, null);
    setUserProperties(a, {
      firebase_uid: null,
      auth_provider: null,
      has_avatar: null,
      app_platform: APP_PLATFORM,
      active_context: null,
    });
  },

  async setActiveContext(context: AppContext) {
    const a = await getMomentraAnalytics();
    if (!a) return;
    setUserProperties(a, { active_context: context });
  },

  async logSignIn(method: string) {
    await MomentraAnalytics.logCustomEvent("sign_in", { method });
  },

  async logSignOut() {
    await MomentraAnalytics.logCustomEvent("sign_out");
  },
};
