"use client";

import { useState } from "react";
import { Calendar, MapPin } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { GroupSkeletonForm } from "@/components/group/shared/skeleton/GroupSkeletonBlocks";

type ExperienceBasicsProps = {
  initialData?: {
    moment_name?: string;
    location?: string;
    start_date?: string;
    end_date?: string;
    description?: string;
  };
  onContinue: (data: any) => void;
  onBack: () => void;
};

export function ExperienceBasics({ initialData, onContinue, onBack }: ExperienceBasicsProps) {
  const [formData, setFormData] = useState({
    moment_name: initialData?.moment_name || "",
    location: initialData?.location || "",
    start_date: initialData?.start_date || "",
    end_date: initialData?.end_date || "",
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
          location: formData.location,
          start_date: formData.start_date,
          end_date: formData.end_date,
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
          <h2 className="text-2xl font-bold">Setting Up Experience</h2>
          <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
            Just a moment while we prepare your experience...
          </p>
        </div>
        <GroupSkeletonForm />
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Experience Details</h2>
        <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
          Tell us about your shared experience
        </p>
      </div>

      <div className="space-y-5">
        <div>
          <label className="mb-2 block text-sm font-medium" style={{ color: colors.textSecondary }}>
            Experience Name
          </label>
          <input
            type="text"
            value={formData.moment_name}
            onChange={(e) => handleChange("moment_name", e.target.value)}
            className="w-full rounded-xl border px-4 py-3 text-sm"
            style={{
              background: colors.surfaceContainer,
              borderColor: `${colors.border}30`,
              color: colors.textPrimary,
            }}
            placeholder="e.g., Goa Trip 2024"
            required
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium" style={{ color: colors.textSecondary }}>
            Location
          </label>
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 size-5 -translate-y-1/2 opacity-60" style={{ color: colors.textSecondary }} />
            <input
              type="text"
              value={formData.location}
              onChange={(e) => handleChange("location", e.target.value)}
              className="w-full rounded-xl border pl-10 pr-4 py-3 text-sm"
              style={{
                background: colors.surfaceContainer,
                borderColor: `${colors.border}30`,
                color: colors.textPrimary,
              }}
              placeholder="Where is this experience happening?"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm font-medium" style={{ color: colors.textSecondary }}>
              Start Date
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 size-5 -translate-y-1/2 opacity-60" style={{ color: colors.textSecondary }} />
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => handleChange("start_date", e.target.value)}
                className="w-full rounded-xl border pl-10 pr-4 py-3 text-sm"
                style={{
                  background: colors.surfaceContainer,
                  borderColor: `${colors.border}30`,
                  color: colors.textPrimary,
                }}
              />
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium" style={{ color: colors.textSecondary }}>
              End Date
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 size-5 -translate-y-1/2 opacity-60" style={{ color: colors.textSecondary }} />
              <input
                type="date"
                value={formData.end_date}
                onChange={(e) => handleChange("end_date", e.target.value)}
                className="w-full rounded-xl border pl-10 pr-4 py-3 text-sm"
                style={{
                  background: colors.surfaceContainer,
                  borderColor: `${colors.border}30`,
                  color: colors.textPrimary,
                }}
              />
            </div>
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
              borderColor: `${colors.border}30`,
              color: colors.textPrimary,
            }}
            placeholder="Describe what this experience is about..."
          />
        </div>
      </div>

      <div className="flex gap-3 pt-4">
        <button
          type="button"
          onClick={onBack}
          className="flex-1 rounded-xl border py-3 text-sm font-semibold"
          style={{
            borderColor: `${colors.border}30`,
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
