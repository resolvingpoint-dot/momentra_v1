"use client";

import { createContext, useContext, type ReactNode } from "react";
import { useReducedMotion } from "./useReducedMotion";

const ReducedMotionContext = createContext(false);

export function MotionProvider({ children }: { children: ReactNode }) {
  const reducedMotion = useReducedMotion();
  return (
    <ReducedMotionContext.Provider value={reducedMotion}>{children}</ReducedMotionContext.Provider>
  );
}

export function useMotionReduced(): boolean {
  return useContext(ReducedMotionContext);
}
