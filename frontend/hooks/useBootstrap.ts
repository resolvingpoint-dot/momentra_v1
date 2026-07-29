"use client";

import { useSyncExternalStore } from "react";
import {
  getBootstrapSnapshot,
  loadBootstrap,
  subscribeBootstrap,
} from "@/stores/bootstrapStore";

export function useBootstrapStore() {
  const snapshot = useSyncExternalStore(
    subscribeBootstrap,
    getBootstrapSnapshot,
    getBootstrapSnapshot,
  );

  return {
    ...snapshot,
    loadBootstrap,
  };
}
