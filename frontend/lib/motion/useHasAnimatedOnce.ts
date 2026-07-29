"use client";

const sessionAnimated = new Set<string>();

export function hasAnimatedOnce(key: string): boolean {
  return sessionAnimated.has(key);
}

export function markAnimatedOnce(key: string) {
  sessionAnimated.add(key);
}
