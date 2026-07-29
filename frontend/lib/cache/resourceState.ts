/**
 * Loading-state contract for data hooks.
 * Skeleton only when loading && !data — never blank usable cached content.
 */
export type ResourceState<T> = {
  data: T | null;
  /** No usable data exists yet. */
  loading: boolean;
  /** Usable data is visible; a background update is in progress. */
  refreshing: boolean;
  error: Error | string | null;
};

export function shouldShowSkeleton(
  loading: boolean,
  data: unknown,
): boolean {
  return loading && data == null;
}
