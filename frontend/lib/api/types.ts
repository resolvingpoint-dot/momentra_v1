export interface FirebaseExchangeRequest {
  id_token: string;
  device_info?: string | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: string;
  email: string | null;
  display_name: string | null;
  photo_url: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AvatarUploadUrlRequest {
  content_type: string;
  byte_size: number;
}

export interface AvatarUploadUrlResponse {
  upload_url: string;
  storage_path: string;
  token: string | null;
}

export interface AvatarConfirmRequest {
  storage_path: string;
}

export interface UserProfileUpdateRequest {
  display_name: string;
}

export interface FirebaseExchangeResponse {
  user: UserResponse;
  tokens: TokenResponse;
}

export interface RefreshTokenRequest {
  refresh_token?: string | null;
}
