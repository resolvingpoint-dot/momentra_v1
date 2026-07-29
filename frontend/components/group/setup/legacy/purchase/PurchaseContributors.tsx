"use client";

import { useState } from "react";
import { Plus, User, X, IndianRupee } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type ContributorInput = {
  display_name: string;
  role_code: string;
  contribution_amount?: number;
};

type PurchaseContributorsProps = {
  initialContributors?: ContributorInput[];
  onContinue: (contributors: ContributorInput[]) => void;
  onBack: () => void;
};

export function PurchaseContributors({ initialContributors = [], onContinue, onBack }: PurchaseContributorsProps) {
  const [contributors, setContributors] = useState<ContributorInput[]>(
    initialContributors.length > 0 
      ? initialContributors 
      : [{ display_name: "", role_code: "CONTRIBUTOR", contribution_amount: 0 }]
  );
  const tokens = useThemeTokens();
  const { colors } = tokens;

  const addContributor = () => {
    setContributors([...contributors, { display_name: "", role_code: "CONTRIBUTOR", contribution_amount: 0 }]);
  };

  const updateContributor = (index: number, field: keyof ContributorInput, value: string | number) => {
    const updatedContributors = [...contributors];
    updatedContributors[index] = { ...updatedContributors[index], [field]: value };
    setContributors(updatedContributors);
  };

  const removeContributor = (index: number) => {
    if (contributors.length > 1) {
      setContributors(contributors.filter((_, i) => i !== index));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Filter out empty contributors
    const validContributors = contributors.filter(contributor => contributor.display_name.trim() !== "");
    onContinue(validContributors);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Add Contributors</h2>
        <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
          Invite people to contribute to your purchase
        </p>
      </div>

      <div className="space-y-4">
        {contributors.map((contributor, index) => (
          <div key={index} className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-full" style={{ background: colors.surfaceContainer }}>
              <User className="size-5 opacity-60" style={{ color: colors.textSecondary }} />
            </div>
            
            <div className="flex-1 space-y-3">
              <div>
                <label className="mb-1 block text-xs font-medium" style={{ color: colors.textSecondary }}>
                  Name
                </label>
                <input
                  type="text"
                  value={contributor.display_name}
                  onChange={(e) => updateContributor(index, "display_name", e.target.value)}
                  className="w-full rounded-xl border px-4 py-2.5 text-sm"
                  style={{
                    background: colors.surfaceContainer,
                    borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)`,
                    color: colors.textPrimary,
                  }}
                  placeholder="Enter name"
                  required={index === 0} // First contributor is required
                />
              </div>
              
              <div>
                <label className="mb-1 block text-xs font-medium" style={{ color: colors.textSecondary }}>
                  Role
                </label>
                <select
                  value={contributor.role_code}
                  onChange={(e) => updateContributor(index, "role_code", e.target.value)}
                  className="w-full rounded-xl border px-4 py-2.5 text-sm"
                  style={{
                    background: colors.surfaceContainer,
                    borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)`,
                    color: colors.textPrimary,
                  }}
                >
                  <option value="CONTRIBUTOR">Contributor</option>
                  <option value="ORGANIZER">Organizer</option>
                  <option value="CO_ORGANIZER">Co-Organizer</option>
                </select>
              </div>
              
              <div>
                <label className="mb-1 block text-xs font-medium" style={{ color: colors.textSecondary }}>
                  Contribution Amount (₹)
                </label>
                <div className="relative">
                  <IndianRupee className="absolute left-3 top-1/2 size-4 -translate-y-1/2 opacity-60" style={{ color: colors.textSecondary }} />
                  <input
                    type="number"
                    value={contributor.contribution_amount || ""}
                    onChange={(e) => updateContributor(index, "contribution_amount", parseFloat(e.target.value) || 0)}
                    className="w-full rounded-xl border pl-10 pr-4 py-2.5 text-sm"
                    style={{
                      background: colors.surfaceContainer,
                      borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)`,
                      color: colors.textPrimary,
                    }}
                    placeholder="0.00"
                    min="0"
                    step="0.01"
                  />
                </div>
              </div>
            </div>
            
            {contributors.length > 1 && (
              <button
                type="button"
                onClick={() => removeContributor(index)}
                className="flex size-10 shrink-0 items-center justify-center rounded-full"
                style={{ background: colors.surfaceContainer }}
              >
                <X className="size-4" style={{ color: colors.textSecondary }} />
              </button>
            )}
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={addContributor}
        className="flex w-full items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold"
        style={{
          background: colors.surfaceContainer,
          color: colors.textPrimary,
        }}
      >
        <Plus className="size-4" />
        Add Another Contributor
      </button>

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
          className="flex-1 rounded-xl py-3 text-sm font-semibold"
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