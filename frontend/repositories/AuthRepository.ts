import {
  exchangeFirebaseToken,
  fetchMe,
  logout as apiLogout,
  refreshAccessToken,
} from "@/lib/api/client";
import type {
  FirebaseExchangeResponse,
  UserResponse,
} from "@/lib/api/types";

export const AuthRepository = {
  exchangeFirebaseToken(idToken: string): Promise<FirebaseExchangeResponse> {
    return exchangeFirebaseToken(idToken);
  },

  refreshAccessToken() {
    return refreshAccessToken();
  },

  fetchMe(): Promise<UserResponse> {
    return fetchMe();
  },

  logout(): Promise<void> {
    return apiLogout();
  },
};
