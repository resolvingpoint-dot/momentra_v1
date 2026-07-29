"use client";

import { useState, type ReactNode } from "react";
import {
  ArrowRight,
  Bell,
  CheckCircle2,
  ChevronLeft,
  CreditCard,
  Home,
  Shield,
  ShoppingBag,
  Sparkles,
  Users,
} from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { groupGlassCardStyle } from "@/components/group/empty/shared/emptyStyles";
import { groupTypography } from "@/lib/group/groupTypography";

type CreateEmptyProps = {
  onCreateMoment: () => void;
  onSharedExperience?: () => void;
  onSharedLiving?: () => void;
  onSharedPurchase?: () => void;
  onClose: () => void;
};

type MomentType = "SHARED_EXPERIENCE" | "SHARED_PURCHASE" | "SHARED_LIVING" | null;

type MomentCard = {
  title: string;
  badge: string;
  description: string;
  tags: string[];
  image: string;
  type: MomentType;
  comingSoon?: boolean;
  accent: string;
  icon: ReactNode;
};

const featureItems = [
  { label: "Everyone on the same page", Icon: Users, tone: "primary" as const },
  { label: "Money organized & transparent", Icon: CreditCard, tone: "secondary" as const },
  { label: "Real-time updates", Icon: Bell, tone: "tertiary" as const },
  { label: "Memories that last", Icon: Shield, tone: "container" as const },
];

export function CreateEmpty({
  onSharedExperience,
  onSharedLiving,
  onSharedPurchase,
  onClose,
}: CreateEmptyProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const [selectedType, setSelectedType] = useState<string | null>(null);

  const accentExperience = colors.brandPrimary;
  const accentPurchase = colors.brandSecondary;
  const accentLiving = colors.brandTertiary;
  const accentMuted = colors.textSecondary;

  const momentCards: MomentCard[] = [
    {
      title: "Shared Experience",
      badge: "LIFE'S BEST MOMENTS",
      description: "Plan, coordinate and remember every shared experience in one place.",
      tags: ["Trips", "Weddings", "Birthdays", "Celebrations", "Outings"],
      image: "/group/type-experience.jpg",
      type: "SHARED_EXPERIENCE",
      accent: accentExperience,
      icon: <Users className="size-4 text-white" />,
    },
    {
      title: "Shared Purchase",
      badge: "BUY TOGETHER",
      description: "Collect money, track contributions and manage every purchase together.",
      tags: ["Gifts", "Furniture", "Gadgets", "Appliances", "Ownership"],
      image: "/group/type-purchase.jpg",
      type: "SHARED_PURCHASE",
      accent: accentPurchase,
      icon: <ShoppingBag className="size-4 text-white" />,
    },
    {
      title: "Shared Living",
      badge: "UNDER ONE ROOF",
      description: "Keep your home organized with shared expenses, responsibilities and everyday coordination.",
      tags: ["Families", "Couples", "Flatmates", "Shared Homes"],
      image: "/group/type-living.jpg",
      type: "SHARED_LIVING",
      accent: accentLiving,
      icon: <Home className="size-4 text-white" />,
    },
    {
      title: "Shared Goal",
      badge: "ACHIEVE TOGETHER",
      description: "Plan, save and stay motivated while working toward something meaningful together.",
      tags: ["Vacation Fund", "Dream Home", "Education", "Startup", "Emergency"],
      image: "/group/type-goal.jpg",
      type: null,
      comingSoon: true,
      accent: accentMuted,
      icon: <CheckCircle2 className="size-4 text-white" />,
    },
    {
      title: "Community",
      badge: "BRING PEOPLE TOGETHER",
      description: "Coordinate people, activities and contributions across your community with clarity.",
      tags: ["Societies", "Schools", "Clubs", "NGOs", "Neighborhoods"],
      image: "/group/type-community.jpg",
      type: null,
      comingSoon: true,
      accent: accentMuted,
      icon: <Users className="size-4 text-white" />,
    },
  ];

  function selectType(type: MomentType) {
    if (!type) return;
    setSelectedType(type);
    if (type === "SHARED_EXPERIENCE") onSharedExperience?.();
    else if (type === "SHARED_PURCHASE") onSharedPurchase?.();
    else if (type === "SHARED_LIVING") onSharedLiving?.();
  }

  function featureToneColor(tone: (typeof featureItems)[number]["tone"]) {
    if (tone === "secondary") return colors.brandSecondary;
    if (tone === "tertiary") return colors.brandTertiary;
    if (tone === "container") return colors.primaryContainer;
    return colors.brandPrimary;
  }

  return (
    <div
      data-momentra-context="group"
      className="fixed inset-0 z-50 flex flex-col overflow-y-auto"
      style={{
        background: colors.background,
        color: colors.textPrimary,
        fontFamily: groupTypography.display.fontFamily,
      }}
    >
      <header
        className="sticky top-0 z-50 flex items-center justify-between px-6 pb-4 pt-4"
        style={{ background: colors.background }}
      >
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="flex size-10 items-center justify-center rounded-full border"
          style={{
            background: "rgba(255,255,255,0.05)",
            borderColor: "rgba(255,255,255,0.1)",
          }}
        >
          <ChevronLeft className="size-5" style={{ color: colors.textSecondary }} />
        </button>
        <h1 className="text-lg font-semibold" style={{ color: colors.textPrimary, opacity: 0.9 }}>
          Choose a Moment
        </h1>
        <div className="size-10" />
      </header>

      <main className="mx-auto w-full max-w-[640px] space-y-6 px-6 pb-16">
        <section
          className="relative overflow-hidden rounded-3xl pt-4"
          style={{
            background: `radial-gradient(circle at top right, color-mix(in srgb, ${colors.brandPrimary} 15%, transparent), transparent 60%)`,
          }}
        >
          <div className="flex items-center justify-between gap-4">
            <div className="z-10 w-[60%]">
              <h2
                className="mb-3 text-3xl font-extrabold leading-tight tracking-tight"
                style={{ fontFamily: groupTypography.display.fontFamily }}
              >
                Plan life together,
                <br />
                in one place.
              </h2>
              <p
                className="max-w-[220px] text-sm leading-relaxed"
                style={{ color: colors.textSecondary }}
              >
                Create a moment to plan, contribute, coordinate and stay in sync.
              </p>
            </div>
            <div className="flex w-[40%] justify-end">
              <img
                src="/group/create-hero.jpg"
                alt=""
                className="aspect-square w-full rounded-2xl border object-cover shadow-2xl"
                style={{ borderColor: "rgba(255,255,255,0.1)" }}
              />
            </div>
          </div>

          <div
            className="mt-6 grid grid-cols-4 gap-4 border-t pt-6"
            style={{ borderColor: "rgba(255,255,255,0.05)" }}
          >
            {featureItems.map(({ label, Icon, tone }) => {
              const toneColor = featureToneColor(tone);
              return (
                <div key={label} className="flex flex-col items-center space-y-3 text-center">
                  <div
                    className="flex size-11 items-center justify-center rounded-xl"
                    style={{ background: `color-mix(in srgb, ${toneColor} 20%, transparent)` }}
                  >
                    <Icon className="size-5" style={{ color: toneColor }} />
                  </div>
                  <span
                    className="text-[10px] font-medium leading-tight"
                    style={{ color: colors.textSecondary }}
                  >
                    {label}
                  </span>
                </div>
              );
            })}
          </div>
        </section>

        <h3
          className="text-xs font-semibold tracking-wider"
          style={{ color: colors.textSecondary }}
        >
          Choose what you want to do together
        </h3>

        <div className="space-y-4">
          {momentCards.map((card) => {
            const enabled = !card.comingSoon;
            const selected = card.type != null && selectedType === card.type;
            return (
              <button
                key={card.title}
                type="button"
                disabled={!enabled}
                onClick={() => selectType(card.type)}
                className={`relative flex min-h-[145px] w-full items-center gap-4 rounded-[28px] p-5 text-left transition-transform ${
                  enabled ? "active:scale-[0.98]" : "cursor-not-allowed opacity-70"
                }`}
                style={{
                  ...groupGlassCardStyle(tokens),
                  boxShadow: selected ? "0 10px 40px rgba(255, 122, 61, 0.15)" : undefined,
                  borderColor: selected
                    ? `color-mix(in srgb, ${colors.primaryContainer} 50%, transparent)`
                    : "rgba(255,255,255,0.08)",
                }}
              >
                <div className="relative size-28 shrink-0 overflow-hidden rounded-2xl shadow-lg">
                  <img
                    src={card.image}
                    alt=""
                    className={`size-full object-cover ${card.comingSoon ? "opacity-60" : ""}`}
                  />
                  <div
                    className="absolute left-2 top-2 flex size-8 items-center justify-center rounded-lg"
                    style={{
                      background: enabled
                        ? `color-mix(in srgb, ${card.accent} 90%, #000)`
                        : "rgba(0,0,0,0.55)",
                    }}
                  >
                    {card.icon}
                  </div>
                </div>

                <div className="flex-1 py-1 pr-10">
                  <div className="mb-2 flex flex-col gap-0.5">
                    <h4 className="text-lg font-bold">{card.title}</h4>
                    <span
                      className="inline-block w-fit rounded px-2 py-0.5 text-[8px] font-bold uppercase tracking-wider"
                      style={{
                        background: `color-mix(in srgb, ${card.accent} 20%, transparent)`,
                        color: card.accent,
                        border: `1px solid color-mix(in srgb, ${card.accent} 30%, transparent)`,
                      }}
                    >
                      {card.comingSoon ? "Coming Soon" : card.badge}
                    </span>
                  </div>
                  <p
                    className="mb-3 text-xs leading-snug"
                    style={{ color: colors.textSecondary }}
                  >
                    {card.description}
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {card.tags.map((tag) => (
                      <span
                        key={tag}
                        className="rounded-full border px-2.5 py-0.5 text-[9px] font-medium"
                        style={{
                          background: "rgba(255,255,255,0.05)",
                          borderColor: "rgba(255,255,255,0.1)",
                          color: colors.textSecondary,
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <span
                  className="absolute right-4 top-1/2 flex size-10 -translate-y-1/2 items-center justify-center rounded-full"
                  style={{
                    background: enabled
                      ? `color-mix(in srgb, ${card.accent} 85%, #000)`
                      : "rgba(255,255,255,0.08)",
                    boxShadow: enabled
                      ? `0 8px 20px color-mix(in srgb, ${card.accent} 25%, transparent)`
                      : undefined,
                  }}
                >
                  <ArrowRight
                    className="size-5"
                    style={{ color: enabled ? colors.brandOnPrimary : colors.textSecondary }}
                  />
                </span>
              </button>
            );
          })}
        </div>

        <div
          className="mt-2 flex items-center justify-between gap-4 rounded-[28px] p-6"
          style={{
            ...groupGlassCardStyle(tokens),
            borderColor: `color-mix(in srgb, ${colors.brandPrimary} 20%, transparent)`,
          }}
        >
          <div className="flex items-center gap-4">
            <div
              className="flex size-12 shrink-0 items-center justify-center rounded-full"
              style={{ background: `color-mix(in srgb, ${colors.brandPrimary} 10%, transparent)` }}
            >
              <Sparkles className="size-6" style={{ color: colors.brandPrimary }} />
            </div>
            <div>
              <h4 className="text-sm font-bold">Not sure where to start?</h4>
              <p className="text-[11px]" style={{ color: colors.textSecondary }}>
                Create a Custom Moment from scratch.
              </p>
            </div>
          </div>
          <button
            type="button"
            disabled
            className="cursor-not-allowed whitespace-nowrap rounded-full border px-5 py-2 text-xs font-bold opacity-60"
            style={{
              borderColor: `color-mix(in srgb, ${colors.brandPrimary} 50%, transparent)`,
              color: colors.textPrimary,
            }}
          >
            Create Custom
          </button>
        </div>
      </main>
    </div>
  );
}
