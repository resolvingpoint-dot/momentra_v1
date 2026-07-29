import { dedupeFetch } from "@/lib/cache/cacheStore";
import { getPersonalCreateOptions } from "@/lib/api/client";
import type { PersonalCreateOptionsResponse } from "@/lib/api/personal";

const CREATE_OPTIONS_KEY = "personal:create_options";

export function fetchPersonalCreateOptions(
  force = false,
): Promise<PersonalCreateOptionsResponse> {
  if (force) {
    return getPersonalCreateOptions();
  }
  return dedupeFetch(CREATE_OPTIONS_KEY, () => getPersonalCreateOptions());
}

export function invalidatePersonalCreateOptionsCache(): void {
  // dedupeFetch only tracks inflight; next fetch will hit network.
  // Force callers use fetchPersonalCreateOptions(true) after mutations.
}
