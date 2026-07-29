import { requestWithRetry } from "@/lib/api/client";
import type { ReferenceDataBootstrap, ReferenceDataOptions } from "@/lib/reference_data/types";

/** Metadata API client (Sprint A foundation). */
export const MetadataRepository = {
  getBootstrap(): Promise<ReferenceDataBootstrap & { metadata_version: number }> {
    return requestWithRetry("api/v1/metadata/bootstrap", { method: "GET" });
  },

  getOptions(keys: string[]): Promise<ReferenceDataOptions & { metadata_version: number }> {
    const query = encodeURIComponent(keys.join(","));
    return requestWithRetry<ReferenceDataOptions & { metadata_version: number }>(
      `api/v1/metadata/options?keys=${query}`,
      { method: "GET" },
    );
  },
};
