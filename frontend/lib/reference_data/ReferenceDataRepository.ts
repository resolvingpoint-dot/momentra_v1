import { requestWithRetry } from "@/lib/api/client";
import type { ReferenceDataBootstrap, ReferenceDataOptions } from "@/lib/reference_data/types";

export const ReferenceDataRepository = {
  getBootstrap(): Promise<ReferenceDataBootstrap> {
    return requestWithRetry<ReferenceDataBootstrap>("api/v1/reference-data/bootstrap", {
      method: "GET",
    });
  },

  getOptions(keys: string[]): Promise<ReferenceDataOptions> {
    const query = encodeURIComponent(keys.join(","));
    return requestWithRetry<ReferenceDataOptions>(
      `api/v1/reference-data/options?keys=${query}`,
      { method: "GET" },
    );
  },
};
