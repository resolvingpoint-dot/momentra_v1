"use client";

import { useState } from "react";
import { Calendar, DollarSign, Image, MapPin, Plus, Users } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { QuickAddSectionModule } from "@/lib/api/group";

type GroupExperienceQuickAddProps = {
  sections: Record<string, QuickAddSectionModule[]>;
  onModuleSelect: (moduleCode: string) => void;
};

export function GroupExperienceQuickAdd({ sections, onModuleSelect }: GroupExperienceQuickAddProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // Get all categories
  const categories = Object.keys(sections);

  // Get modules for selected category or first category
  const currentCategory = selectedCategory || categories[0] || "";
  const modules = sections[currentCategory] || [];

  // Icon mapping
  const getIcon = (moduleCode: string) => {
    switch (moduleCode) {
      case "PARTICIPANT":
        return Users;
      case "BOOKING":
        return Calendar;
      case "PLANNING_ITEM":
        return Plus;
      case "EXPENSE":
        return DollarSign;
      case "MEMORY":
        return Image;
      default:
        return Plus;
    }
  };

  return (
    <div className="space-y-6">
      {/* Category Tabs */}
      {categories.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-2">
          {categories.map((category) => (
            <button
              key={category}
              type="button"
              onClick={() => setSelectedCategory(category)}
              className="whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium"
              style={{
                background:
                  currentCategory === category
                    ? colors.primaryContainer
                    : colors.surfaceContainer,
                color:
                  currentCategory === category
                    ? colors.brandOnPrimary
                    : colors.textPrimary,
              }}
            >
              {category}
            </button>
          ))}
        </div>
      )}

      {/* Modules Grid */}
      <div className="grid grid-cols-3 gap-3">
        {modules.map((module) => {
          const Icon = getIcon(module.module_code);
          return (
            <button
              key={module.module_code}
              type="button"
              onClick={() => onModuleSelect(module.module_code)}
              className="flex flex-col items-center gap-2 rounded-xl p-3 text-center transition-transform hover:scale-[1.03]"
              style={{ background: colors.surfaceContainer }}
            >
              <div
                className="flex size-12 items-center justify-center rounded-full"
                style={{ background: `${colors.primaryContainer}20` }}
              >
                <Icon className="size-6" style={{ color: colors.primaryContainer }} />
              </div>
              <span className="text-xs font-medium">{module.module_label}</span>
            </button>
          );
        })}
      </div>

      {/* Quick Tips */}
      <div
        className="rounded-2xl p-4 text-sm"
        style={{ background: `${colors.primaryContainer}15` }}
      >
        <h3 className="font-semibold">Quick Tip</h3>
        <p className="mt-1 opacity-80" style={{ color: colors.textSecondary }}>
          Add bookings, expenses, and memories as they happen to keep everyone in the loop.
        </p>
      </div>
    </div>
  );
}
