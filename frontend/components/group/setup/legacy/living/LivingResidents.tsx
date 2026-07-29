"use client";

import { useState } from "react";
import { Plus, User, X } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type ResidentInput = {
  display_name: string;
  role_code: string;
  resident_type?: string;
};

type LivingResidentsProps = {
  initialResidents?: ResidentInput[];
  onContinue: (residents: ResidentInput[]) => void;
  onBack: () => void;
};

export function LivingResidents({ initialResidents = [], onContinue, onBack }: LivingResidentsProps) {
  const [residents, setResidents] = useState<ResidentInput[]>(
    initialResidents.length > 0 
      ? initialResidents 
      : [{ display_name: "", role_code: "RESIDENT", resident_type: "ROOMMATE" }]
  );
  const tokens = useThemeTokens();
  const { colors } = tokens;

  const addResident = () => {
    setResidents([...residents, { display_name: "", role_code: "RESIDENT", resident_type: "ROOMMATE" }]);
  };

  const updateResident = (index: number, field: keyof ResidentInput, value: string) => {
    const updatedResidents = [...residents];
    updatedResidents[index] = { ...updatedResidents[index], [field]: value };
    setResidents(updatedResidents);
  };

  const removeResident = (index: number) => {
    if (residents.length > 1) {
      setResidents(residents.filter((_, i) => i !== index));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Filter out empty residents
    const validResidents = residents.filter(resident => resident.display_name.trim() !== "");
    onContinue(validResidents);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Add Residents</h2>
        <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
          Invite residents to join your living arrangement
        </p>
      </div>

      <div className="space-y-4">
        {residents.map((resident, index) => (
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
                  value={resident.display_name}
                  onChange={(e) => updateResident(index, "display_name", e.target.value)}
                  className="w-full rounded-xl border px-4 py-2.5 text-sm"
                  style={{
                    background: colors.surfaceContainer,
                    borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)`,
                    color: colors.textPrimary,
                  }}
                  placeholder="Enter name"
                  required={index === 0} // First resident is required
                />
              </div>
              
              <div>
                <label className="mb-1 block text-xs font-medium" style={{ color: colors.textSecondary }}>
                  Role
                </label>
                <select
                  value={resident.role_code}
                  onChange={(e) => updateResident(index, "role_code", e.target.value)}
                  className="w-full rounded-xl border px-4 py-2.5 text-sm"
                  style={{
                    background: colors.surfaceContainer,
                    borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)`,
                    color: colors.textPrimary,
                  }}
                >
                  <option value="RESIDENT">Resident</option>
                  <option value="HOUSEHOLD_LEAD">Household Lead</option>
                  <option value="GUEST">Guest</option>
                </select>
              </div>
              
              <div>
                <label className="mb-1 block text-xs font-medium" style={{ color: colors.textSecondary }}>
                  Resident Type
                </label>
                <select
                  value={resident.resident_type || "ROOMMATE"}
                  onChange={(e) => updateResident(index, "resident_type", e.target.value)}
                  className="w-full rounded-xl border px-4 py-2.5 text-sm"
                  style={{
                    background: colors.surfaceContainer,
                    borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)`,
                    color: colors.textPrimary,
                  }}
                >
                  <option value="ROOMMATE">Roommate</option>
                  <option value="FAMILY_MEMBER">Family Member</option>
                  <option value="TENANT">Tenant</option>
                  <option value="GUEST">Guest</option>
                </select>
              </div>
            </div>
            
            {residents.length > 1 && (
              <button
                type="button"
                onClick={() => removeResident(index)}
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
        onClick={addResident}
        className="flex w-full items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold"
        style={{
          background: colors.surfaceContainer,
          color: colors.textPrimary,
        }}
      >
        <Plus className="size-4" />
        Add Another Resident
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