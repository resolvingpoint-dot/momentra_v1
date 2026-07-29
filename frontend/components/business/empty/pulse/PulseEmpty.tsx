"use client";

import { ArrowRight, Activity, Eye, GitBranch, Brain, TrendingUp } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { businessCardStyle, businessScrollShellStyle } from "@/components/business/empty/shared/emptyStyles";

type PulseEmptyProps = {
  onCreateMoment: () => void;
  bottomPadding?: number;
};

const dimensions = [
  {
    title: "Team Operations",
    description: "Align teams, track activities and execute together.",
    image: "/business/dim-team.jpg",
    accent: "#5B5CEB",
    available: true,
  },
  {
    title: "Business Runway",
    description: "Track cash, burn and runway to stay ahead.",
    image: "/business/dim-runway.jpg",
    accent: "#10B981",
    available: true,
  },
  {
    title: "Business Operations",
    description: "Run daily operations smoothly and improve efficiency.",
    image: "/business/dim-department.jpg",
    accent: "#F97316",
    available: true,
  },
  {
    title: "Project Operations",
    description: "Coming soon — not available in v1.",
    image: "/business/dim-project.jpg",
    accent: "#00CED1",
    available: false,
  },
  {
    title: "Event Operations",
    description: "Coming soon — not available in v1.",
    image: "/business/dim-event.jpg",
    accent: "#F59E0B",
    available: false,
  },
  {
    title: "Vendor Operations",
    description: "Coming soon — not available in v1.",
    image: "/business/dim-vendor.jpg",
    accent: "#8B5CF6",
    available: false,
  },
  {
    title: "Custom Operational Moment",
    description: "Coming soon — not available in v1.",
    image: "/business/dim-custom.jpg",
    accent: "#5B5CEB",
    available: false,
    wide: true,
  },
] as const;

const benefits = [
  { icon: Eye, title: "Complete Visibility", description: "See everything that impacts your business in one place." },
  { icon: GitBranch, title: "Better Coordination", description: "Align teams, vendors and departments effortlessly." },
  { icon: Brain, title: "Smarter Decisions", description: "Get the right insights at the right time to make confident calls." },
  { icon: Activity, title: "Operational Control", description: "Catch issues early, stay on track and drive outcomes." },
  { icon: TrendingUp, title: "Continuous Growth", description: "Improve every day with data-backed learnings from operations." },
] as const;

const intelligenceTags = [
  "Spending Patterns",
  "Approval Bottlenecks",
  "Vendor Performance",
  "Operational Improvements",
  "Growth Opportunities",
] as const;

export function PulseEmpty({ onCreateMoment, bottomPadding = 0 }: PulseEmptyProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <div
      data-momentra-context="business"
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={businessScrollShellStyle(tokens, bottomPadding)}
    >
      <div className="relative mx-auto flex w-full max-w-[600px] flex-col gap-6 px-5 py-6 md:max-w-[1080px] md:px-20 md:py-8">
        <section className="-mx-5 overflow-hidden rounded-none md:-mx-20 md:rounded-3xl">
          <div className="relative h-[280px] md:h-[360px]">
            <img
              src="/business/pulse-hero.jpg"
              alt=""
              className="absolute inset-0 size-full object-cover"
            />
            <div
              className="absolute inset-0"
              style={{
                background: `linear-gradient(to top, ${colors.background}, color-mix(in srgb, ${colors.background} 45%, transparent), transparent)`,
              }}
            />
            <div className="absolute inset-x-0 bottom-0 space-y-3 px-5 pb-8 pt-16 text-center md:px-12">
              <span
                className="inline-block rounded-full px-3 py-1 text-[10px] font-bold tracking-widest"
                style={{ background: "rgba(91, 92, 235, 0.25)", color: "#C7C8FF" }}
              >
                Business Pulse
              </span>
              <h2 className="text-[28px] font-bold leading-9 tracking-tight md:text-[32px]">
                Every Business Action Becomes Visibility.
              </h2>
              <p className="mx-auto max-w-md text-sm opacity-80" style={{ color: colors.textSecondary }}>
                Track, coordinate and improve every operational moment across your business.
              </p>
              <button
                type="button"
                onClick={onCreateMoment}
                className="inline-flex items-center gap-2 rounded-2xl px-6 py-3 text-sm font-semibold"
                style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
              >
                Create Your First Moment
                <ArrowRight className="size-4" />
              </button>
            </div>
          </div>
        </section>

        <section className="space-y-3">
          <div>
            <h3 className="text-xl font-semibold">Choose What You Want To Operate</h3>
            <p className="text-sm opacity-70" style={{ color: colors.textSecondary }}>
              Choose what you want to run and we&apos;ll help you manage it end to end.
            </p>
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {dimensions.map((dim) => (
              <button
                key={dim.title}
                type="button"
                disabled={!dim.available}
                onClick={() => {
                  if (dim.available) onCreateMoment();
                }}
                className={`group relative overflow-hidden rounded-2xl text-left ${"wide" in dim && dim.wide ? "md:col-span-2 h-40" : "h-44"} ${
                  dim.available ? "hover:-translate-y-0.5" : "cursor-not-allowed"
                }`}
              >
                <img
                  src={dim.image}
                  alt=""
                  className={`absolute inset-0 size-full object-cover transition-transform duration-500 ${
                    dim.available ? "group-hover:scale-105" : "opacity-60"
                  }`}
                />
                <div
                  className="absolute inset-0"
                  style={{
                    background: `linear-gradient(to top, color-mix(in srgb, ${colors.background} 92%, transparent), color-mix(in srgb, ${dim.accent} 18%, transparent) 45%, transparent)`,
                  }}
                />
                <div className="relative flex h-full flex-col justify-end p-4">
                  {!dim.available ? (
                    <span className="mb-1 text-[9px] font-bold tracking-widest opacity-80">COMING SOON</span>
                  ) : null}
                  <h4 className="font-semibold">{dim.title}</h4>
                  <p className="mt-1 text-xs opacity-80">{dim.description}</p>
                </div>
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-2xl p-5" style={businessCardStyle(tokens)}>
          <span className="text-[10px] font-bold tracking-widest" style={{ color: "#5B5CEB" }}>
            Operational Intelligence
          </span>
          <h3 className="mt-2 text-lg font-semibold">Your Business Learns From Every Action</h3>
          <p className="mt-1 text-sm opacity-80" style={{ color: colors.textSecondary }}>
            Momentra automatically transforms activity into operational intelligence.
          </p>
          <div className="relative mt-4 h-32 overflow-hidden rounded-xl">
            <img
              src="/business/intelligence.jpg"
              alt=""
              className="size-full object-cover"
            />
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {intelligenceTags.map((tag) => (
              <span
                key={tag}
                className="rounded-full px-3 py-1 text-xs font-medium"
                style={{ background: "rgba(91, 92, 235, 0.15)", color: "#8B8CF0" }}
              >
                {tag}
              </span>
            ))}
          </div>
        </section>

        <section className="space-y-4 rounded-2xl p-5" style={businessCardStyle(tokens)}>
          <h3 className="text-lg font-semibold">Why Businesses Use Pulse</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {benefits.map((item) => (
              <div key={item.title} className="flex gap-3">
                <div
                  className="flex size-9 shrink-0 items-center justify-center rounded-lg"
                  style={{ background: "rgba(91, 92, 235, 0.15)" }}
                >
                  <item.icon className="size-4" style={{ color: "#5B5CEB" }} />
                </div>
                <div>
                  <p className="text-sm font-medium">{item.title}</p>
                  <p className="text-xs opacity-70" style={{ color: colors.textSecondary }}>
                    {item.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <p className="text-center text-xs opacity-60">Your data is private and secure</p>
      </div>
    </div>
  );
}
