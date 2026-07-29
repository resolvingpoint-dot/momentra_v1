"use client";

import { useSyncExternalStore } from "react";
import {
  getSelectedGroupMomentTypeCode,
  hydrateGroupMomentSession,
  subscribeGroupMomentSession,
  type GroupMomentTypeCode,
} from "@/lib/group/groupMomentSession";

if (typeof window !== "undefined") {
  hydrateGroupMomentSession();
}

export function useGroupMomentSession(): GroupMomentTypeCode {
  return useSyncExternalStore(
    subscribeGroupMomentSession,
    getSelectedGroupMomentTypeCode,
    () => "SHARED_EXPERIENCE" as GroupMomentTypeCode,
  );
}
