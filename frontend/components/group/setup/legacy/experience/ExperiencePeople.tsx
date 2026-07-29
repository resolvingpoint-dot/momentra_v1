"use client";

import { useState } from "react";
import { Plus, User, X } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type MemberInput = {
  display_name: string;
  role_code: string;
};

type ExperiencePeopleProps = {
  initialMembers?: MemberInput[];
  onContinue: (members: MemberInput[]) => void;
  onBack: () => void;
};

export function ExperiencePeople({ initialMembers = [], onContinue, onBack }: ExperiencePeopleProps) {
  const [members, setMembers] = useState<MemberInput[]>(initialMembers.length > 0 ? initialMembers : [{ display_name: "", role_code: "PARTICIPANT" }]);
  const tokens = useThemeTokens();
  const { colors } = tokens;

  const addMember = () => {
    setMembers([...members, { display_name: "", role_code: "PARTICIPANT" }]);
  };

  const updateMember = (index: number, field: keyof MemberInput, value: string) => {
    const updatedMembers = [...members];
    updatedMembers[index] = { ...updatedMembers[index], [field]: value };
    setMembers(updatedMembers);
  };

  const removeMember = (index: number) => {
    if (members.length > 1) {
      setMembers(members.filter((_, i) => i !== index));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Filter out empty members
    const validMembers = members.filter(member => member.display_name.trim() !== "");
    onContinue(validMembers);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Add People</h2>
        <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
          Invite people to join your experience
        </p>
      </div>

      <div className="space-y-4">
        {members.map((member, index) => (
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
                  value={member.display_name}
                  onChange={(e) => updateMember(index, "display_name", e.target.value)}
                  className="w-full rounded-xl border px-4 py-2.5 text-sm"
                  style={{
                    background: colors.surfaceContainer,
                    borderColor: `${colors.border}30`,
                    color: colors.textPrimary,
                  }}
                  placeholder="Enter name"
                  required={index === 0} // First member is required
                />
              </div>
              
              <div>
                <label className="mb-1 block text-xs font-medium" style={{ color: colors.textSecondary }}>
                  Role
                </label>
                <select
                  value={member.role_code}
                  onChange={(e) => updateMember(index, "role_code", e.target.value)}
                  className="w-full rounded-xl border px-4 py-2.5 text-sm"
                  style={{
                    background: colors.surfaceContainer,
                    borderColor: `${colors.border}30`,
                    color: colors.textPrimary,
                  }}
                >
                  <option value="PARTICIPANT">Participant</option>
                  <option value="ORGANIZER">Organizer</option>
                  <option value="CO_ORGANIZER">Co-Organizer</option>
                </select>
              </div>
            </div>
            
            {members.length > 1 && (
              <button
                type="button"
                onClick={() => removeMember(index)}
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
        onClick={addMember}
        className="flex w-full items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold"
        style={{
          background: colors.surfaceContainer,
          color: colors.textPrimary,
        }}
      >
        <Plus className="size-4" />
        Add Another Person
      </button>

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
