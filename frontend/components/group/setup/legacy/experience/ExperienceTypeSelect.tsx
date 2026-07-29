"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { groupGlassCardStyle } from "@/components/group/empty/shared/emptyStyles";

type ProfileOption = {
  profile_code: string;
  profile_name: string;
  profile_description: string | null;
  display_order: number;
};

type ExperienceTypeSelectProps = {
  profiles: ProfileOption[];
  selectedProfile: string | null;
  onSelectProfile: (profileCode: string) => void;
  onContinue: () => void;
};

export function ExperienceTypeSelect({
  profiles,
  selectedProfile,
  onSelectProfile,
  onContinue,
}: ExperienceTypeSelectProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Choose Experience Type</h2>
        <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
          Select the type of shared experience you want to create
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {profiles.map((profile) => (
          <button
            key={profile.profile_code}
            type="button"
            onClick={() => onSelectProfile(profile.profile_code)}
            className="relative overflow-hidden rounded-2xl text-left transition-all duration-200"
            style={{
              ...(groupGlassCardStyle(tokens) as React.CSSProperties),
              boxShadow: selectedProfile === profile.profile_code ? `0 0 0 2px ${colors.primaryContainer}` : undefined,
            }}
          >
            <div className="p-5">
              <h3 className="text-lg font-semibold">{profile.profile_name}</h3>
              {profile.profile_description && (
                <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
                  {profile.profile_description}
                </p>
              )}
            </div>
            {selectedProfile === profile.profile_code && (
              <div
                className="absolute right-3 top-3 flex size-6 items-center justify-center rounded-full"
                style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
              >
                <div className="size-2 rounded-full bg-current" />
              </div>
            )}
          </button>
        ))}
      </div>

      <div className="pt-4">
        <button
          type="button"
          onClick={onContinue}
          disabled={!selectedProfile}
          className="w-full rounded-xl py-4 text-sm font-semibold transition-opacity disabled:opacity-50"
          style={{
            background: colors.primaryContainer,
            color: colors.brandOnPrimary,
          }}
        >
          Continue
        </button>
      </div>
    </div>
  );
}
