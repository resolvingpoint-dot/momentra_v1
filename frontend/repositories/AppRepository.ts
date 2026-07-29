import { getAppBootstrap, patchAppPreferences } from "@/lib/api/client";
import type {
  BootstrapResponse,
  PreferenceUpdateRequest,
  PreferenceUpdateResponse,
} from "@/lib/api/bootstrapTypes";
import { patchBootstrapPreferences } from "@/stores/bootstrapStore";

export const AppRepository = {
  getBootstrap(): Promise<BootstrapResponse> {
    return getAppBootstrap();
  },

  async updatePreferences(
    body: PreferenceUpdateRequest,
  ): Promise<PreferenceUpdateResponse> {
    const result = await patchAppPreferences(body);
    // Write-through immediately so BootstrapGate sync cannot snap context
    // back to a stale MY_MONEY while a Group switch is in flight.
    patchBootstrapPreferences(result);
    return result;
  },
};
