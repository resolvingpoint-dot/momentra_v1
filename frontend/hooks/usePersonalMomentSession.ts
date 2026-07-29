"use client";

import { useSyncExternalStore } from "react";
import {
  getSelectedMomentTypeCode,
  hydratePersonalMomentSession,
  subscribePersonalMomentSession,
  type PersonalMomentTypeCode,
} from "@/lib/personal/personalMomentSession";

if (typeof window !== "undefined") {
  hydratePersonalMomentSession();
}

export function usePersonalMomentSession(): PersonalMomentTypeCode {
  return useSyncExternalStore(
    subscribePersonalMomentSession,
    getSelectedMomentTypeCode,
    () => "LIFE_OPERATIONS" as PersonalMomentTypeCode,
  );
}
