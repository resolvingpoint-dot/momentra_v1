"use client";

import { useMemo } from "react";
import {
  Building2,
  Camera,
  ChevronRight,
  DollarSign,
  Gavel,
  Megaphone,
  Package,
  Plus,
  Receipt,
  ShoppingCart,
  Store,
  Truck,
  Users,
  Vote,
  Wrench,
  type LucideIcon,
} from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { TripQuickAddCategory } from "@/repositories/GroupTripQuickAddRepository";

const ICONS: Record<string, LucideIcon> = {
  person_add: Users,
  group_add: Users,
  shopping_cart: ShoppingCart,
  storefront: Store,
  receipt_long: Receipt,
  payments: DollarSign,
  savings: DollarSign,
  how_to_vote: Vote,
  poll: Vote,
  campaign: Megaphone,
  supervised_user_circle: Users,
  local_shipping: Truck,
  photo_library: Camera,
  auto_awesome: Camera,
  checklist: Plus,
  gavel: Gavel,
  inventory_2: Package,
  build: Wrench,
  home: Building2,
  add: Plus,
};

type TemplateQuickAddHubProps = {
  categories: TripQuickAddCategory[];
  chips: string[];
  heroTitle: string;
  heroSubtitle: string;
  onModuleSelect: (moduleCode: string) => void;
};

export function TemplateQuickAddHub({
  categories,
  chips,
  heroTitle,
  heroSubtitle,
  onModuleSelect,
}: TemplateQuickAddHubProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <div className="space-y-8 pb-4">
      <div className="flex gap-2 overflow-x-auto pb-1">
        {chips.map((chip) => (
          <span
            key={chip}
            className="whitespace-nowrap rounded-full border px-3 py-1 text-xs font-medium"
            style={{
              borderColor: `${colors.primaryContainer}40`,
              background: `${colors.primaryContainer}18`,
              color: colors.primaryContainer,
            }}
          >
            {chip}
          </span>
        ))}
      </div>

      <div
        className="relative h-48 overflow-hidden rounded-3xl"
        style={{
          background: `linear-gradient(135deg, ${colors.primaryContainer}55 0%, ${colors.surfaceContainer} 60%)`,
          boxShadow: `0 10px 40px ${colors.primaryContainer}2E`,
        }}
      >
        <div
          className="absolute inset-0"
          style={{
            background: `linear-gradient(135deg, ${colors.primaryContainer}33 0%, transparent 60%)`,
          }}
        />
        <div className="absolute inset-x-0 bottom-0 p-5">
          <h3 className="text-xl font-semibold" style={{ color: colors.textPrimary }}>
            {heroTitle}
          </h3>
          <p className="mt-1 text-sm" style={{ color: colors.textSecondary }}>
            {heroSubtitle}
          </p>
        </div>
      </div>

      {categories.map((category) => (
        <section key={category.id}>
          <h4
            className="mb-3 text-xs font-bold uppercase tracking-widest"
            style={{ color: colors.primaryContainer }}
          >
            {category.label}
          </h4>
          <div className="space-y-3">
            {category.modules.map((module) => {
              const Icon = ICONS[module.icon] ?? Plus;
              return (
                <button
                  key={module.module_code}
                  type="button"
                  onClick={() => onModuleSelect(module.module_code)}
                  className="flex w-full items-center justify-between rounded-3xl border p-4 text-left transition active:scale-[0.98]"
                  style={{
                    background: `${colors.surfaceContainer}CC`,
                    borderColor: `${colors.textSecondary}20`,
                  }}
                >
                  <div className="flex items-center gap-4">
                    <div
                      className="flex size-12 items-center justify-center rounded-xl"
                      style={{ background: `${colors.primaryContainer}18` }}
                    >
                      <Icon className="size-5" style={{ color: colors.primaryContainer }} />
                    </div>
                    <div>
                      <p className="font-semibold" style={{ color: colors.textPrimary }}>
                        {module.label}
                      </p>
                      {module.description ? (
                        <p className="text-sm" style={{ color: colors.textSecondary }}>
                          {module.description}
                        </p>
                      ) : null}
                    </div>
                  </div>
                  <ChevronRight className="size-5" style={{ color: colors.textSecondary }} />
                </button>
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}

export function PurchaseQuickAddHub(props: {
  categories: TripQuickAddCategory[];
  momentName?: string;
  onModuleSelect: (moduleCode: string) => void;
}) {
  const chips = useMemo(
    () => [props.momentName ?? "Purchase", "Shared Purchase", "Quick Add"].filter(Boolean),
    [props.momentName],
  );
  return (
    <TemplateQuickAddHub
      categories={props.categories}
      chips={chips}
      heroTitle="Keep this purchase moving"
      heroSubtitle="Add contributors, items, vendors, ownership, and memories."
      onModuleSelect={props.onModuleSelect}
    />
  );
}

export function LivingQuickAddHub(props: {
  categories: TripQuickAddCategory[];
  momentName?: string;
  onModuleSelect: (moduleCode: string) => void;
}) {
  const chips = useMemo(
    () => [props.momentName ?? "Home", "Shared Living", "Quick Add"].filter(Boolean),
    [props.momentName],
  );
  return (
    <TemplateQuickAddHub
      categories={props.categories}
      chips={chips}
      heroTitle="Keep home life in sync"
      heroSubtitle="Add residents, expenses, chores, rules, and house updates."
      onModuleSelect={props.onModuleSelect}
    />
  );
}
