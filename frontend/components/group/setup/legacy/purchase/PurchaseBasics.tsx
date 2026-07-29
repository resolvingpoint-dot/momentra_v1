"use client";

import { useState } from "react";
import { DollarSign, Link } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { GroupSkeletonForm } from "@/components/group/shared/skeleton/GroupSkeletonBlocks";

type PurchaseBasicsProps = {
  initialData?: {
    moment_name?: string;
    target_amount?: number;
    target_date?: string;
    purchase_link?: string;
    description?: string;
  };
  onContinue: (data: any) => void;
  onBack: () => void;
};

export function PurchaseBasics({ initialData, onContinue, onBack }: PurchaseBasicsProps) {
  const [formData, setFormData] = useState({
    moment_name: initialData?.moment_name || "",
    target_amount: initialData?.target_amount || 0,
    target_date: initialData?.target_date || "",
    purchase_link: initialData?.purchase_link || "",
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
          target_amount: formData.target_amount,
          target_date: formData.target_date,
          purchase_link: formData.purchase_link,
          description: formData.description,
        },
      };
      
      onContinue(payload);
    } catch (error) {
      console.error("Error saving basics:", error);
      setIsLoading(false);
    }
  };

  const handleChange = (field: string, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold">Setting Up Purchase</h2>
          <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
            Just a moment while we prepare your purchase...
          </p>
        </div>
        <GroupSkeletonForm />
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Purchase Details</h2>
        <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
          Tell us about your shared purchase
        </p>
      </div>

      <div className="space-y-5">
        <div>
          <label className="mb-2 block text-sm font-medium" style={{ color: colors.textSecondary }}>
            Purchase Name
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
            placeholder="e.g., New Laptop for Team"
            required
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium" style={{ color: colors.textSecondary }}>
            Target Amount
          </label>
          <div className="relative">
            <DollarSign className="absolute left-3 top-1/2 size-5 -translate-y-1/2 opacity-60" style={{ color: colors.textSecondary }} />
            <input
              type="number"
              value={formData.target_amount || ""}
              onChange={(e) => handleChange("target_amount", parseFloat(e.target.value) || 0)}
              className="w-full rounded-xl border pl-10 pr-4 py-3 text-sm"
              style={{
                background: colors.surfaceContainer,
                borderColor: `${colors.border}30`,
                color: colors.textPrimary,
              }}
              placeholder="0.00"
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium" style={{ color: colors.textSecondary }}>
            Target Date
          </label>
          <input
            type="date"
            value={formData.target_date}
            onChange={(e) => handleChange("target_date", e.target.value)}
            className="w-full rounded-xl border px-4 py-3 text-sm"
            style={{
              background: colors.surfaceContainer,
              borderColor: `${colors.border}30`,
              color: colors.textPrimary,
            }}
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium" style={{ color: colors.textSecondary }}>
            Purchase Link
          </label>
          <div className="relative">
            <Link className="absolute left-3 top-1/2 size-5 -translate-y-1/2 opacity-60" style={{ color: colors.textSecondary }} />
            <input
              type="url"
              value={formData.purchase_link}
              onChange={(e) => handleChange("purchase_link", e.target.value)}
              className="w-full rounded-xl border pl-10 pr-4 py-3 text-sm"
              style={{
                background: colors.surfaceContainer,
                borderColor: `${colors.border}30`,
                color: colors.textPrimary,
              }}
              placeholder="https://example.com/product"
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
              borderColor: `${colors.border}30`,
              color: colors.textPrimary,
            }}
            placeholder="Describe what this purchase is for..."
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
