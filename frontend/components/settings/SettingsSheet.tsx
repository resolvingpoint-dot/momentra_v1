"use client";

import { useEffect, useRef, useState } from "react";
import { UserAvatar } from "@/components/profile/UserAvatar";
import {
  confirmAvatarUpload,
  putToSignedUrl,
  requestAvatarUploadUrl,
  updateProfile,
} from "@/lib/api/client";
import type { UserResponse } from "@/lib/api/types";
import { prepareAvatarFile } from "@/lib/avatarUpload";
import { AvatarPhotoEditor } from "@/components/settings/AvatarPhotoEditor";
import { CurrencyPreferencesSection } from "@/components/settings/CurrencyPreferencesSection";
import { getBootstrap } from "@/stores/bootstrapStore";
import type { BootstrapPreferences } from "@/lib/api/bootstrapTypes";
import {
  changePassword,
  getFirebaseAuth,
  isEmailPasswordUser,
  updateFirebaseDisplayName,
} from "@/lib/firebase";

type SettingsSheetProps = {
  user: UserResponse;
  isLoading: boolean;
  onClose: () => void;
  onSignOut: () => void;
  onUserUpdated: (user: UserResponse) => void;
  onViewIntro?: () => void;
};

export function SettingsSheet({
  user,
  isLoading,
  onClose,
  onSignOut,
  onUserUpdated,
  onViewIntro,
}: SettingsSheetProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [displayName, setDisplayName] = useState(user.display_name ?? "");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [uploading, setUploading] = useState(false);
  const [savingName, setSavingName] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [nameError, setNameError] = useState<string | null>(null);
  const [nameSuccess, setNameSuccess] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null);
  const [canChangePassword, setCanChangePassword] = useState(false);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [currencyPrefs, setCurrencyPrefs] = useState<BootstrapPreferences | null>(
    () => getBootstrap()?.preferences ?? null,
  );

  useEffect(() => {
    setDisplayName(user.display_name ?? "");
  }, [user.display_name]);

  useEffect(() => {
    setCanChangePassword(isEmailPasswordUser(getFirebaseAuth().currentUser));
  }, []);

  useEffect(() => {
    setCurrencyPrefs(getBootstrap()?.preferences ?? null);
  }, []);

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;

    setUploadError(null);
    setPendingFile(file);
  }

  async function handleConfirmAvatar(rotationDegrees: number) {
    if (!pendingFile) return;

    setUploading(true);
    setUploadError(null);
    try {
      const prepared = await prepareAvatarFile(pendingFile, rotationDegrees);
      const upload = await requestAvatarUploadUrl("image/jpeg", prepared.size);
      await putToSignedUrl(upload.upload_url, prepared, "image/jpeg");
      const updated = await confirmAvatarUpload(upload.storage_path);
      onUserUpdated(updated);
      setPendingFile(null);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  function handleCancelAvatarEditor() {
    if (uploading) return;
    setPendingFile(null);
    setUploadError(null);
  }

  async function handleSaveDisplayName() {
    const trimmed = displayName.trim();
    if (!trimmed) {
      setNameError("Display name cannot be empty");
      return;
    }
    setSavingName(true);
    setNameError(null);
    setNameSuccess(null);
    try {
      await updateFirebaseDisplayName(trimmed);
      const updated = await updateProfile(trimmed);
      onUserUpdated(updated);
      setNameSuccess("Display name saved");
    } catch (err) {
      setNameError(err instanceof Error ? err.message : "Could not save name");
    } finally {
      setSavingName(false);
    }
  }

  async function handleChangePassword() {
    if (newPassword.length < 6) {
      setPasswordError("New password must be at least 6 characters");
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError("Passwords do not match");
      return;
    }
    setChangingPassword(true);
    setPasswordError(null);
    setPasswordSuccess(null);
    try {
      await changePassword(currentPassword, newPassword);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setPasswordSuccess("Password updated");
    } catch (err) {
      setPasswordError(err instanceof Error ? err.message : "Could not change password");
    } finally {
      setChangingPassword(false);
    }
  }

  const busy = isLoading || uploading || savingName || changingPassword;

  return (
    <>
      {pendingFile ? (
        <AvatarPhotoEditor
          file={pendingFile}
          isUploading={uploading}
          uploadError={uploadError}
          onCancel={handleCancelAvatarEditor}
          onConfirm={handleConfirmAvatar}
        />
      ) : null}

    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 sm:items-center">
      <div className="max-h-[90vh] w-full max-w-sm overflow-y-auto rounded-t-2xl bg-white p-6 text-indigo-900 sm:rounded-2xl">
        <h2 className="text-lg font-semibold">Settings</h2>
        <p className="mt-1 text-sm text-indigo-700/80">Account and app preferences</p>

        <div className="mt-6 flex flex-col items-center gap-3 text-center">
          <UserAvatar
            photoUrl={user.photo_url}
            displayName={user.display_name}
            email={user.email}
            size={72}
          />
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileChange}
          />
          <button
            type="button"
            className="rounded-lg border border-indigo-200 px-4 py-2 text-sm font-medium text-indigo-800 disabled:opacity-60"
            disabled={busy}
            onClick={() => fileInputRef.current?.click()}
          >
            {uploading ? "Uploading…" : "Change photo"}
          </button>
          {uploadError ? (
            <p className="text-sm text-red-600">{uploadError}</p>
          ) : null}
        </div>

        <div className="mt-6 space-y-4">
          <div>
            <label className="text-sm font-medium text-indigo-800">Display name</label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="mt-1 w-full rounded-lg border border-indigo-200 px-3 py-2 text-sm"
              disabled={busy}
            />
            <button
              type="button"
              className="mt-2 w-full rounded-lg bg-indigo-100 px-4 py-2 text-sm font-medium text-indigo-900 disabled:opacity-60"
              disabled={busy}
              onClick={handleSaveDisplayName}
            >
              {savingName ? "Saving…" : "Save name"}
            </button>
            {nameError ? <p className="mt-1 text-sm text-red-600">{nameError}</p> : null}
            {nameSuccess ? <p className="mt-1 text-sm text-teal-700">{nameSuccess}</p> : null}
          </div>

          {user.email ? (
            <div>
              <label className="text-sm font-medium text-indigo-800">Email</label>
              <p className="mt-1 rounded-lg border border-indigo-100 bg-indigo-50/50 px-3 py-2 text-sm text-indigo-700">
                {user.email}
              </p>
            </div>
          ) : null}

          {canChangePassword ? (
            <div className="space-y-2 border-t border-indigo-100 pt-4">
              <p className="text-sm font-medium text-indigo-800">Change password</p>
              <input
                type="password"
                placeholder="Current password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="w-full rounded-lg border border-indigo-200 px-3 py-2 text-sm"
                disabled={busy}
                autoComplete="current-password"
              />
              <input
                type="password"
                placeholder="New password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full rounded-lg border border-indigo-200 px-3 py-2 text-sm"
                disabled={busy}
                autoComplete="new-password"
              />
              <input
                type="password"
                placeholder="Confirm new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full rounded-lg border border-indigo-200 px-3 py-2 text-sm"
                disabled={busy}
                autoComplete="new-password"
              />
              <button
                type="button"
                className="w-full rounded-lg border border-indigo-200 px-4 py-2 text-sm font-medium text-indigo-800 disabled:opacity-60"
                disabled={busy}
                onClick={handleChangePassword}
              >
                {changingPassword ? "Updating…" : "Update password"}
              </button>
              {passwordError ? (
                <p className="text-sm text-red-600">{passwordError}</p>
              ) : null}
              {passwordSuccess ? (
                <p className="text-sm text-teal-700">{passwordSuccess}</p>
              ) : null}
            </div>
          ) : null}
        </div>

        {currencyPrefs ? (
          <div className="mt-6 space-y-3 border-t border-indigo-100 pt-6">
            <h3 className="text-sm font-semibold text-indigo-900">Currency & locale</h3>
            <CurrencyPreferencesSection
              preferences={currencyPrefs}
              onPreferencesUpdated={setCurrencyPrefs}
            />
          </div>
        ) : null}

        <div className="mt-6 flex flex-col gap-2">
          {onViewIntro ? (
            <button
              type="button"
              className="w-full rounded-lg border border-indigo-200 px-4 py-2 text-sm font-medium text-indigo-800"
              onClick={onViewIntro}
            >
              View intro
            </button>
          ) : null}
          <button type="button" className="btn-ghost w-full" onClick={onClose}>
            Close
          </button>
          <button
            type="button"
            className="w-full rounded-lg border border-red-200 px-4 py-2 text-sm font-medium text-red-600 disabled:opacity-60"
            disabled={busy}
            onClick={onSignOut}
          >
            Sign out
          </button>
        </div>
      </div>
    </div>
    </>
  );
}
