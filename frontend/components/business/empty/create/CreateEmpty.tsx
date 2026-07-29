"use client";

import {
  ArrowRight,
  BarChart3,
  Calendar,
  FolderKanban,
  Handshake,
  Loader2,
  Lightbulb,
  Settings,
  Users,
  Wallet,
  X,
} from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { businessCardStyle } from "@/components/business/empty/shared/emptyStyles";
import type { BusinessCreateOptionCard, BusinessCreateOptionsResponse } from "@/lib/api/business";

type CreateEmptyProps = {
  options?: BusinessCreateOptionsResponse | null;
  onCreateMoment: (typeCode?: string) => void;
  onClose: () => void;
  creatingType?: string | null;
};

type CardMeta = {
  moment_type_code: string;
  title: string;
  description: string;
  badge: string;
  tags: string[];
  accent: string;
  available: boolean;
  image: string;
  Icon: typeof Users;
};

const CREATE_IMAGE_BY_TYPE: Record<string, string> = {
  TEAM_OPERATIONS: "/business/create-team.jpg",
  BUSINESS_RUNWAY: "/business/create-runway.jpg",
  BUSINESS_OPERATIONS: "/business/create-department.jpg",
  DEPARTMENT_OPERATIONS: "/business/create-department.jpg",
  PROJECT_OPERATIONS: "/business/create-project.jpg",
  EVENT_OPERATIONS: "/business/create-event.jpg",
  VENDOR_OPERATIONS: "/business/create-vendor.jpg",
};

const CREATE_HERO = "/business/create-hero.jpg";

const FALLBACK_CARDS: CardMeta[] = [
  {
    moment_type_code: "TEAM_OPERATIONS",
    title: "Team Operations",
    description:
      "Coordinate your people, meetings, responsibilities and day-to-day execution from one shared place.",
    badge: "Recommended First",
    tags: ["Meetings", "Tasks", "Attendance", "Decisions", "Team Health"],
    accent: "#5B5CEB",
    available: true,
    image: CREATE_IMAGE_BY_TYPE.TEAM_OPERATIONS,
    Icon: Users,
  },
  {
    moment_type_code: "BUSINESS_RUNWAY",
    title: "Business Runway",
    description:
      "Monitor cash flow, spending and runway so your business can make confident financial decisions.",
    badge: "Most Popular",
    tags: ["Cash Flow", "Revenue", "Expenses", "Burn Rate", "Runway"],
    accent: "#10B981",
    available: true,
    image: CREATE_IMAGE_BY_TYPE.BUSINESS_RUNWAY,
    Icon: Wallet,
  },
  {
    moment_type_code: "BUSINESS_OPERATIONS",
    title: "Business Operations",
    description:
      "Keep everyday business operations organized across departments, processes and workflows.",
    badge: "Run Efficiently",
    tags: ["Operations", "Inventory", "Compliance", "Processes", "Administration"],
    accent: "#F97316",
    available: true,
    image: CREATE_IMAGE_BY_TYPE.BUSINESS_OPERATIONS,
    Icon: Settings,
  },
  {
    moment_type_code: "PROJECT_OPERATIONS",
    title: "Project Operations",
    description:
      "Plan, coordinate and deliver projects while keeping teams, timelines and milestones aligned.",
    badge: "Deliver Projects",
    tags: ["Planning", "Timeline", "Resources", "Deliverables", "Risks"],
    accent: "#3B82F6",
    available: false,
    image: CREATE_IMAGE_BY_TYPE.PROJECT_OPERATIONS,
    Icon: FolderKanban,
  },
  {
    moment_type_code: "EVENT_OPERATIONS",
    title: "Event Operations",
    description:
      "Organize business events from planning through execution with complete team coordination.",
    badge: "Coordinate Events",
    tags: ["Conferences", "Launches", "Workshops", "Client Events", "Internal Events"],
    accent: "#F59E0B",
    available: false,
    image: CREATE_IMAGE_BY_TYPE.EVENT_OPERATIONS,
    Icon: Calendar,
  },
  {
    moment_type_code: "VENDOR_OPERATIONS",
    title: "Vendor Operations",
    description:
      "Manage vendors, procurement, contracts and supplier relationships from one organized workspace.",
    badge: "Partner Management",
    tags: ["Procurement", "Contracts", "Suppliers", "Purchase Orders", "Deliveries"],
    accent: "#8B5A2B",
    available: false,
    image: CREATE_IMAGE_BY_TYPE.VENDOR_OPERATIONS,
    Icon: Handshake,
  },
];

const BENEFITS = [
  { label: "Keep teams aligned", Icon: Users, tint: "#5B5CEB" },
  { label: "Track business progress", Icon: BarChart3, tint: "#3B82F6" },
  { label: "Stay financially aware", Icon: Wallet, tint: "#10B981" },
  { label: "Build organizational memory", Icon: Lightbulb, tint: "#F59E0B" },
] as const;

function mergeCards(apiCards: BusinessCreateOptionCard[] | undefined): CardMeta[] {
  return FALLBACK_CARDS.map((fallback) => {
    const api = apiCards?.find((c) => c.moment_type_code === fallback.moment_type_code);
    return {
      ...fallback,
      title: api?.moment_type_name ?? fallback.title,
      description: api?.create_tagline?.trim() || fallback.description,
      badge: api?.badge_label?.trim() || fallback.badge,
      accent: api?.accent_main?.trim() || fallback.accent,
      available: api ? api.is_available !== false : fallback.available,
      image: CREATE_IMAGE_BY_TYPE[fallback.moment_type_code] ?? fallback.image,
    };
  });
}

export function CreateEmpty({
  options,
  onCreateMoment,
  onClose,
  creatingType = null,
}: CreateEmptyProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const creating = Boolean(creatingType);
  const cards = mergeCards(options?.cards);

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col overflow-y-auto"
      style={{ background: colors.background, color: colors.textPrimary }}
      aria-busy={creating}
    >
      {creating ? (
        <div
          className="absolute inset-0 z-20 flex flex-col items-center justify-center gap-3"
          style={{ background: `color-mix(in srgb, ${colors.background} 82%, transparent)` }}
          role="status"
          aria-live="polite"
        >
          <Loader2 className="size-8 animate-spin opacity-80" aria-hidden />
          <p className="text-sm font-medium">Loading setup…</p>
        </div>
      ) : null}

      <div className="mx-auto flex w-full max-w-lg flex-col px-5 pb-12 pt-4">
        <button
          type="button"
          onClick={onClose}
          disabled={creating}
          aria-label="Close"
          className="mb-6 flex size-10 items-center justify-center rounded-full self-start disabled:opacity-50"
          style={{ background: colors.surfaceContainer }}
        >
          <X className="size-5" />
        </button>

        <section className="mb-8 flex flex-col gap-6 md:flex-row md:items-center">
          <div className="flex-1">
            <p
              className="mb-3 text-sm font-medium uppercase tracking-wide"
              style={{ color: colors.textSecondary }}
            >
              Choose Your Business Moment
            </p>
            <h1 className="mb-4 text-[28px] font-bold leading-9 tracking-tight">
              Run every part of your business with{" "}
              <span style={{ color: colors.brandPrimary }}>clarity.</span>
            </h1>
            <p className="text-sm leading-relaxed" style={{ color: colors.textSecondary }}>
              Create a business moment to organize teams, operations, projects, events, vendors and
              financial runway in one place.
            </p>
          </div>
          <div
            className="hidden aspect-[4/3] w-[42%] overflow-hidden rounded-2xl border md:block"
            style={{ borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)` }}
          >
            <img src={CREATE_HERO} alt="" className="size-full object-cover" />
          </div>
        </section>

        <section
          className="mb-8 grid grid-cols-4 gap-2 rounded-2xl p-4 text-center"
          style={businessCardStyle(tokens)}
        >
          {BENEFITS.map(({ label, Icon, tint }) => (
            <div key={label} className="flex flex-col items-center gap-2">
              <div
                className="flex size-11 items-center justify-center rounded-xl"
                style={{ background: `color-mix(in srgb, ${tint} 20%, transparent)` }}
              >
                <Icon className="size-5" style={{ color: tint }} />
              </div>
              <p className="text-[10px] leading-tight" style={{ color: colors.textSecondary }}>
                {label}
              </p>
            </div>
          ))}
        </section>

        <section className="mb-4">
          <h2 className="text-lg font-semibold">Choose the part of your business</h2>
          <p className="text-sm" style={{ color: colors.textSecondary }}>
            you want to manage.
          </p>
        </section>

        <section className="space-y-4">
          {cards.map((card) => {
            const enabled = card.available && !creating;
            const { Icon } = card;
            return (
              <button
                key={card.moment_type_code}
                type="button"
                disabled={!enabled}
                onClick={() => {
                  if (enabled) onCreateMoment(card.moment_type_code);
                }}
                className={`relative flex w-full gap-4 overflow-hidden rounded-3xl p-4 text-left transition-transform ${
                  enabled ? "enabled:hover:scale-[1.01] enabled:active:scale-[0.99]" : "cursor-not-allowed opacity-70"
                }`}
                style={{
                  ...businessCardStyle(tokens),
                  border: `1px solid color-mix(in srgb, ${card.accent} 25%, transparent)`,
                }}
              >
                <div className="relative h-24 w-32 shrink-0 overflow-hidden rounded-2xl">
                  <img src={card.image} alt="" className="size-full object-cover" />
                  <div
                    className="absolute left-2 top-2 flex size-7 items-center justify-center rounded-lg"
                    style={{ background: card.accent, color: "#fff" }}
                  >
                    <Icon className="size-3.5" />
                  </div>
                </div>
                <div className="min-w-0 flex-1 space-y-2 pr-10">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-base font-bold">{card.title}</h3>
                    <span
                      className="rounded-full border px-2 py-0.5 text-[9px] font-medium"
                      style={{
                        background: `color-mix(in srgb, ${card.accent} 20%, transparent)`,
                        color: card.accent,
                        borderColor: `color-mix(in srgb, ${card.accent} 30%, transparent)`,
                      }}
                    >
                      {card.available ? card.badge : `${card.badge} · Soon`}
                    </span>
                  </div>
                  <p className="text-xs leading-relaxed" style={{ color: colors.textSecondary }}>
                    {card.description}
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {card.tags.map((tag) => (
                      <span
                        key={tag}
                        className="rounded-md px-2 py-1 text-[9px]"
                        style={{
                          background: `color-mix(in srgb, ${colors.textPrimary} 5%, transparent)`,
                          color: colors.textSecondary,
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                <span
                  className="absolute bottom-4 right-4 flex size-9 items-center justify-center rounded-full"
                  style={{
                    background: card.available ? card.accent : colors.surfaceContainerHigh,
                    color: "#fff",
                  }}
                  aria-hidden
                >
                  {creatingType === card.moment_type_code ? (
                    <Loader2 className="size-4 animate-spin" />
                  ) : (
                    <ArrowRight className="size-4" />
                  )}
                </span>
              </button>
            );
          })}
        </section>

        <section
          className="mt-8 flex flex-col gap-4 rounded-3xl p-5 sm:flex-row sm:items-center sm:justify-between"
          style={{
            ...businessCardStyle(tokens),
            border: `1px solid color-mix(in srgb, ${colors.brandPrimary} 25%, transparent)`,
            background: `color-mix(in srgb, ${colors.brandPrimary} 10%, ${colors.surfaceContainer})`,
          }}
        >
          <div className="flex items-start gap-4">
            <div
              className="flex size-12 shrink-0 items-center justify-center rounded-2xl"
              style={{ background: `color-mix(in srgb, ${colors.brandPrimary} 20%, transparent)` }}
            >
              <Lightbulb className="size-6" style={{ color: colors.brandPrimary }} />
            </div>
            <div>
              <h3 className="mb-1 text-base font-bold">Not sure where to start?</h3>
              <p className="max-w-sm text-xs leading-relaxed" style={{ color: colors.textSecondary }}>
                Start with Team Operations and build your business operating system one moment at a
                time.
              </p>
            </div>
          </div>
          <button
            type="button"
            disabled={creating}
            onClick={() => onCreateMoment("TEAM_OPERATIONS")}
            className="rounded-full border-2 px-6 py-3 text-center text-sm font-semibold disabled:opacity-50"
            style={{ borderColor: colors.brandPrimary, color: colors.textPrimary }}
          >
            {creatingType === "TEAM_OPERATIONS" ? (
              <Loader2 className="mx-auto size-5 animate-spin" />
            ) : (
              "Start with Team Operations"
            )}
          </button>
        </section>
      </div>
    </div>
  );
}
