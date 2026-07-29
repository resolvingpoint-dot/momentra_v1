"use client";

import { useState } from "react";
import { CheckCircle, MapPin, Loader2 } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type ReviewData = {
  moment_name: string;
  address?: string;
  move_in_date?: string;
  description?: string;
  residents: Array<{ display_name: string; role_code: string; resident_type?: string }>;
};

type LivingReviewProps = {
  data: ReviewData;
  onActivate: () => void;
  onBack: () => void;
};

export function LivingReview({ data, onActivate, onBack }: LivingReviewProps) {
  const [isActivating, setIsActivating] = useState(false);
  const tokens = useThemeTokens();
  const { colors } = tokens;

  const handleActivate = async () => {
    setIsActivating(true);
    try {
      await onActivate();
    } catch (error) {
      console.error("Error activating living arrangement:", error);
      setIsActivating(false);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Review & Activate</h2>
        <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
          Review your living arrangement details before activating
        </p>
      </div>

      <div className="space-y-5 rounded-2xl p-5" style={{ background: colors.surfaceContainer }}>
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider opacity-70" style={{ color: colors.textSecondary }}>
            Living Details
          </h3>
          <div className="mt-3 space-y-3">
            <div className="flex justify-between">
              <span className="font-medium">Name</span>
              <span>{data.moment_name}</span>
            </div>
            {data.address && (
              <div className="flex justify-between">
                <span className="font-medium">Address</span>
                <span className="truncate max-w-[200px]" title={data.address}>
                  <MapPin className="inline size-3 mr-1" />{data.address}
                </span>
              </div>
            )}
            {data.move_in_date && (
              <div className="flex justify-between">
                <span className="font-medium">Move-in Date</span>
                <span>{formatDate(data.move_in_date)}</span>
              </div>
            )}
          </div>
        </div>

        {data.description && (
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider opacity-70" style={{ color: colors.textSecondary }}>
              Description
            </h3>
            <p className="mt-2 text-sm">{data.description}</p>
          </div>
        )}

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider opacity-70" style={{ color: colors.textSecondary }}>
            Residents ({data.residents.length})
          </h3>
          <div className="mt-3 space-y-2">
            {data.residents.map((resident, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="font-medium">{resident.display_name}</span>
                <div className="flex items-center gap-2">
                  {resident.resident_type && (
                    <span className="text-xs" style={{ color: colors.textSecondary }}>
                      {resident.resident_type.replace("_", " ").toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                  )}
                  <span className="text-xs opacity-70" style={{ color: colors.textSecondary }}>
                    {resident.role_code.replace("_", " ").toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-2xl p-5" style={{ background: `color-mix(in srgb, ${colors.primaryContainer} 15%, transparent)` }}>
        <div className="flex items-start gap-3">
          <CheckCircle className="mt-0.5 size-5 shrink-0" style={{ color: colors.primaryContainer }} />
          <div>
            <h3 className="font-semibold">Ready to Activate</h3>
            <p className="mt-1 text-sm opacity-80" style={{ color: colors.textSecondary }}>
              Once activated, your living arrangement will be live and visible to all residents.
            </p>
          </div>
        </div>
      </div>

      <div className="flex gap-3 pt-4">
        <button
          type="button"
          onClick={onBack}
          className="flex-1 rounded-xl border py-3 text-sm font-semibold"
          style={{
            borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)`,
            color: colors.textPrimary,
          }}
        >
          Back
        </button>
        <button
          type="button"
          onClick={handleActivate}
          disabled={isActivating}
          className="flex flex-1 items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold transition-opacity disabled:opacity-50"
          style={{
            background: colors.primaryContainer,
            color: colors.brandOnPrimary,
          }}
        >
          {isActivating ? (
            <>
              <Loader2 className="size-4 animate-spin" />
              Activating...
            </>
          ) : (
            "Activate Living"
          )}
        </button>
      </div>
    </div>
  );
}