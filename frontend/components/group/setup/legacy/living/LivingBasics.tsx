"use client";

import { useState } from "react";
import { MapPin, Calendar } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { GroupSkeletonForm } from "@/components/group/shared/skeleton/GroupSkeletonBlocks";

type LivingBasicsProps = {
  initialData?: {
    moment_name?: string;
    address?: string;
    move_in_date?: string;
    description?: string;
  };
  onContinue: (data: any) => void;
  onBack: () => void;
};

export function LivingBasics({ initialData, onContinue, onBack }: LivingBasicsProps) {
  const [formData, setFormData] = useState({
    moment_name: initialData?.moment_name || "",
    address: initialData?.address || "",
    move_in_date: initialData?.move_in_date || "",
    description: initialData?.description || "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const tokens = useThemeTokens();
  const { colors } = tokens;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      // Prepare data for API call
      const payload = {
        moment_name: formData.moment_name,
        detail_fields: {
          address: formData.address,
          move_in_date: formData.move_in_date,
          description: formData.description,
        },
      };
      
      onContinue(payload);
    } catch (error) {
      console.error("Error saving basics:", error);
      setIsLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold">Setting Up Living Arrangement</h2>
          <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
            Just a moment while we prepare your living arrangement...
          </p>
        </div>
        <GroupSkeletonForm />
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Living Details</h2>
        <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
          Tell us about your shared living arrangement
        </p>
      </div>

      <div className="space-y-5">
        <div>
          <label className="mb-2 block text-sm font-medium" style={{ color: colors.textSecondary }}>
            Living Arrangement Name
          </label>
          <input
            type="text"
            value={formData.moment_name}
            onChange={(e) => handleChange("moment_name", e.target.value)}
            className="w-full rounded-xl border px-4 py-3 text-sm"
            style={{
              background: colors.surfaceContainer,
              borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)`,
              color: colors.textPrimary,
            }}
            placeholder="e.g., Flat 202, MG Road"
            required
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium" style={{ color: colors.textSecondary }}>
            Address
          </label>
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 size-5 -translate-y-1/2 opacity-60" style={{ color: colors.textSecondary }} />
            <input
              type="text"
              value={formData.address}
              onChange={(e) => handleChange("address", e.target.value)}
              className="w-full rounded-xl border pl-10 pr-4 py-3 text-sm"
              style={{
                background: colors.surfaceContainer,
                borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)`,
                color: colors.textPrimary,
              }}
              placeholder="e.g., 123 Main Street, City"
            />
          </div>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium" style={{ color: colors.textSecondary }}>
            Move-in Date
          </label>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 size-5 -translate-y-1/2 opacity-60" style={{ color: colors.textSecondary }} />
            <input
              type="date"
              value={formData.move_in_date}
              onChange={(e) => handleChange("move_in_date", e.target.value)}
              className="w-full rounded-xl border pl-10 pr-4 py-3 text-sm"
              style={{
                background: colors.surfaceContainer,
                borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)`,
                color: colors.textPrimary,
              }}
            />
          </div>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium" style={{ color: colors.textSecondary }}>
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => handleChange("description", e.target.value)}
            rows={4}
            className="w-full rounded-xl border px-4 py-3 text-sm"
            style={{
              background: colors.surfaceContainer,
              borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)`,
              color: colors.textPrimary,
            }}
            placeholder="Describe your living arrangement..."
          />
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
          type="submit"
          disabled={!formData.moment_name}
          className="flex-1 rounded-xl py-3 text-sm font-semibold transition-opacity disabled:opacity-50"
          style={{
            background: colors.primaryContainer,
            color: colors.brandOnPrimary,
          }}
        >
          Continue
        </button>
      </div>
    </form>
  );
}