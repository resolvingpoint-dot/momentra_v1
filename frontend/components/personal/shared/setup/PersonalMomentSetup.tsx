"use client";

import { Activity, Heart, Loader2, Palette, RefreshCw, Rocket } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { glassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import {
  accentFromToken,
  DomainGlassSection,
  DomainIdentityCard,
  DomainInsightCard,
  DomainKvRow,
  DomainProgressGlow,
  DomainSectionHeader,
} from "@/components/personal/shared/domain/DomainWidgets";
import { GuidedSetupShell } from "@/components/setup/GuidedSetupShell";
import type { GuidedSetupStep } from "@/components/setup/guidedSetupTypes";
import { useSetupFlow } from "@/hooks/useSetupFlow";
import {
  PERSONAL_SETUP_COPY,
  personalSetupTemplate,
  personalTemplateForMomentType,
} from "@/lib/personal/setupCatalog";
import type {
  PersonalSetupField,
  PersonalSetupOption,
  PersonalSetupPreview,
  PersonalSetupResponse,
} from "@/lib/api/personal";
import type {
  PersonalEmotionalSecuritySetupPreview,
  PersonalFutureBuildingSetupPreview,
  PersonalLifestyleSetupPreview,
} from "@/lib/api/personalDomainTypes";
import {
  momentTypeBadge,
  type PersonalMomentTypeCode,
} from "@/lib/personal/personalMomentSession";

const SINGLE_SCROLL_STEP: GuidedSetupStep = {
  id: "setup",
  title: "Setup",
  shortTitle: "Setup",
  description: "",
};

type PersonalMomentSetupProps = {
  momentId: string;
  onClose: () => void;
  onActivated: () => void;
};

function accentColor(
  accent: string | null | undefined,
  colors: ReturnType<typeof useThemeTokens>["colors"],
): string {
  return accentFromToken(accent, colors) ?? colors.brandPrimary;
}

function isCompactGrid(fieldKey: string): boolean {
  return fieldKey === "pressure_sources" || fieldKey === "recovery_supports";
}

function isLifeOpsType(typeCode: string): boolean {
  return typeCode === "LIFE_OPERATIONS";
}

function missionIcon(typeCode: string) {
  if (typeCode === "FUTURE_BUILDING") return Rocket;
  if (typeCode === "LIFESTYLE") return Palette;
  if (typeCode === "RELATIONSHIPS") return Heart;
  return Activity;
}

export function PersonalMomentSetup({
  momentId,
  onClose,
  onActivated,
}: PersonalMomentSetupProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const {
    setup,
    template,
    preview,
    answers,
    loading,
    submitting,
    error,
    saveStatus,
    updateAnswer,
    toggleMulti,
    flushPendingSave,
    requestPreview,
    submit,
  } = useSetupFlow(momentId);

  const templateId = personalTemplateForMomentType(setup?.moment_type_code);
  const catalog = personalSetupTemplate(templateId);
  const previewTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const answersKey = JSON.stringify(answers);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  function validateAllRequired(): Record<string, string> {
    if (!setup) return {};
    const errs: Record<string, string> = {};
    for (const field of setup.fields) {
      if (!field.required) continue;
      const value = answers[field.field_key];
      if (field.field_type === "multi_select") {
        if (!Array.isArray(value) || value.length === 0) {
          errs[field.field_key] = "Required";
        }
      } else {
        const str = typeof value === "string" ? value.trim() : "";
        if (!str) errs[field.field_key] = "Required";
      }
    }
    return errs;
  }

  function clearFieldError(fieldKey: string) {
    setFieldErrors((prev) => {
      if (!prev[fieldKey]) return prev;
      const next = { ...prev };
      delete next[fieldKey];
      return next;
    });
  }

  useEffect(() => {
    if (!setup) return;
    if (previewTimer.current) clearTimeout(previewTimer.current);
    previewTimer.current = setTimeout(() => {
      previewTimer.current = null;
      void requestPreview();
    }, 450);
    return () => {
      if (previewTimer.current) clearTimeout(previewTimer.current);
    };
    // Debounced preview when answers change (personal single-scroll).
    // eslint-disable-next-line react-hooks/exhaustive-deps -- answersKey tracks answer changes
  }, [setup, answersKey]);

  async function handleSubmit() {
    const flushed = await flushPendingSave();
    if (!flushed) return;
    const errs = validateAllRequired();
    setFieldErrors(errs);
    if (Object.keys(errs).length > 0) {
      window.requestAnimationFrame(() => {
        document.querySelector('[role="alert"]')?.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });
      });
      return;
    }
    const ok = await submit();
    if (ok) onActivated();
  }

  if (loading || !setup) {
    return (
      <div
        className="fixed inset-0 z-50 flex flex-col items-center justify-center gap-4 px-6"
        style={{ background: colors.background, color: colors.textPrimary }}
      >
        {loading ? (
          <Loader2 className="size-8 animate-spin opacity-70" />
        ) : (
          <>
            <p className="text-center text-sm" style={{ color: colors.error }}>
              {error ?? "Failed to load setup"}
            </p>
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl px-6 py-3 text-sm font-semibold"
              style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
            >
              Back
            </button>
          </>
        )}
      </div>
    );
  }

  const typeCode = setup.moment_type_code as PersonalMomentTypeCode;
  const MissionIcon = missionIcon(typeCode);
  const liveSummary = [
    {
      label: "Moment",
      value: String(answers.moment_name ?? answers.name ?? ""),
    },
    {
      label: "Focus",
      value: String(answers.focus_area ?? answers.building_focus ?? ""),
    },
  ].filter((r) => r.value);

  return (
    <GuidedSetupShell
      contextType="personal"
      layout="singleScroll"
      templateId={templateId}
      momentTypeCode={setup.moment_type_code}
      title={catalog.title}
      subtitle={catalog.subtitle}
      estimatedDuration={PERSONAL_SETUP_COPY.estimated_minutes}
      currentStep={1}
      steps={[SINGLE_SCROLL_STEP]}
      saveState={saveStatus}
      canGoBack={false}
      canContinue={false}
      canPreview
      liveSummary={liveSummary}
      contextHelp={catalog.subtitle}
      footerPrimaryLabel={
        setup.cta_label ?? catalog.activate_cta ?? defaultSetupCta(typeCode)
      }
      error={error}
      submitting={submitting}
      canActivate={!submitting}
      onClose={onClose}
      onPreview={() => void requestPreview()}
      onActivate={() => void handleSubmit()}
    >
      <div className="space-y-7">
        <p className="text-[10px] font-bold tracking-widest opacity-60">
          {template?.hero.badge_label ?? momentTypeBadge(typeCode)}
        </p>

        {setup.mission ? <MissionCard mission={setup.mission} icon={MissionIcon} /> : null}

        {setup.fields.map((field) => (
          <FieldSection
            key={field.field_key}
            field={field}
            answers={answers}
            lifeOpsLayout={isLifeOpsType(typeCode)}
            error={fieldErrors[field.field_key]}
            onSelectSingle={(value) => {
              clearFieldError(field.field_key);
              updateAnswer(field.field_key, value);
            }}
            onToggleMulti={(value) => {
              clearFieldError(field.field_key);
              toggleMulti(field.field_key, value);
            }}
          />
        ))}

        {preview ? <PreviewPanel preview={preview} typeCode={typeCode} /> : null}
        <SummaryPanel setup={setup} answers={answers} />

        {setup.footer_note ? (
          <p
            className="text-center text-[11px] font-medium tracking-[0.2em] opacity-70"
            style={{ color: colors.textSecondary }}
          >
            {setup.footer_note.toUpperCase()}
          </p>
        ) : null}
      </div>
    </GuidedSetupShell>
  );
}

function defaultSetupCta(typeCode: PersonalMomentTypeCode): string {
  switch (typeCode) {
    case "FUTURE_BUILDING":
      return "Begin Building My Future";
    case "LIFESTYLE":
      return "Activate My Lifestyle";
    case "RELATIONSHIPS":
      return "Activate My Relationships";
    default:
      return "Begin My New Rhythm";
  }
}

function MissionCard({
  mission,
  icon: Icon,
}: {
  mission: NonNullable<PersonalSetupResponse["mission"]>;
  icon: typeof Activity;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <div className="rounded-2xl p-5" style={glassCardStyle(tokens)}>
      <div className="mb-2 flex items-center gap-2 text-xs font-bold tracking-widest" style={{ color: colors.brandPrimary }}>
        <Icon className="size-4" />
        {mission.badge_label.toUpperCase()}
      </div>
      <h3 className="mb-2 text-lg font-semibold">{mission.title}</h3>
      <p className="text-sm leading-relaxed opacity-80" style={{ color: colors.textSecondary }}>
        {mission.body}
      </p>
    </div>
  );
}

function FieldSection({
  field,
  answers,
  lifeOpsLayout,
  error,
  onSelectSingle,
  onToggleMulti,
}: {
  field: PersonalSetupField;
  answers: Record<string, string | string[]>;
  lifeOpsLayout: boolean;
  error?: string;
  onSelectSingle: (value: string) => void;
  onToggleMulti: (value: string) => void;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const selectedSingle = answers[field.field_key] as string | undefined;
  const selectedMulti = Array.isArray(answers[field.field_key])
    ? (answers[field.field_key] as string[])
    : [];

  return (
    <section>
      {lifeOpsLayout ? (
        <h3 className="mb-1 text-lg font-semibold">{field.label}</h3>
      ) : (
        <DomainSectionHeader title={field.label} />
      )}
      {field.helper_text ? (
        <p className="mb-3 text-sm opacity-70" style={{ color: colors.textSecondary }}>
          {field.helper_text}
        </p>
      ) : null}

      {field.field_type === "single_select" ? (
        lifeOpsLayout ? (
          <div className="grid grid-cols-2 gap-3">
            {field.options?.map((option) => (
              <LifeStateCard
                key={option.value}
                option={option}
                selected={selectedSingle === option.value}
                error={error}
                onSelect={() => onSelectSingle(option.value)}
              />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {field.options?.map((option) => (
              <DomainOptionCard
                key={option.value}
                option={option}
                selected={selectedSingle === option.value}
                error={error}
                onSelect={() => onSelectSingle(option.value)}
              />
            ))}
          </div>
        )
      ) : isCompactGrid(field.field_key) ? (
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {field.options?.map((option) => (
            <CompactChip
              key={option.value}
              label={option.label}
              selected={selectedMulti.includes(option.value)}
              error={error}
              onToggle={() => onToggleMulti(option.value)}
            />
          ))}
        </div>
      ) : (
        <div className="flex flex-wrap gap-2">
          {field.options?.map((option) => (
            <WrapChip
              key={option.value}
              label={option.label}
              selected={selectedMulti.includes(option.value)}
              error={error}
              onToggle={() => onToggleMulti(option.value)}
            />
          ))}
        </div>
      )}

      {error ? (
        <p className="mt-2 text-sm" style={{ color: colors.error }} role="alert">
          {error}
        </p>
      ) : null}
    </section>
  );
}

function LifeStateCard({
  option,
  selected,
  error,
  onSelect,
}: {
  option: PersonalSetupOption;
  selected: boolean;
  error?: string;
  onSelect: () => void;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const barHeight = `${Math.round((option.bar_level ?? 0.5) * 100)}%`;
  const accent = accentColor(option.accent, colors);
  const outlineColor = selected
    ? colors.brandPrimary
    : error
      ? colors.error
      : undefined;

  return (
    <button
      type="button"
      onClick={onSelect}
      className="rounded-xl p-3 text-left transition-transform hover:scale-[1.02] active:scale-[0.98]"
      style={{
        ...glassCardStyle(tokens),
        outline: outlineColor ? `2px solid ${outlineColor}` : undefined,
      }}
    >
      <div className="flex gap-3">
        <div
          className="relative w-2 shrink-0 overflow-hidden rounded"
          style={{ height: 40, background: `color-mix(in srgb, ${colors.textSecondary} 20%, transparent)` }}
        >
          <div
            className="absolute bottom-0 left-0 right-0 rounded"
            style={{ height: barHeight, background: accent }}
          />
        </div>
        <div className="min-w-0">
          <p
            className="text-sm font-semibold leading-tight"
            style={{ color: selected ? colors.brandPrimary : colors.textPrimary }}
          >
            {option.label}
          </p>
          {option.description ? (
            <p className="mt-1 text-xs leading-snug opacity-70" style={{ color: colors.textSecondary }}>
              {option.description}
            </p>
          ) : null}
        </div>
      </div>
      {selected ? (
        <span
          className="mt-2 inline-block size-1.5 animate-pulse rounded-full"
          style={{ background: colors.brandPrimary }}
        />
      ) : null}
    </button>
  );
}

function DomainOptionCard({
  option,
  selected,
  error,
  onSelect,
}: {
  option: PersonalSetupOption;
  selected: boolean;
  error?: string;
  onSelect: () => void;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const barHeight = `${Math.round((option.bar_level ?? 0.5) * 100)}%`;
  const accent = accentColor(option.accent, colors);
  const outlineColor = selected
    ? colors.brandPrimary
    : error
      ? colors.error
      : undefined;

  return (
    <button
      type="button"
      onClick={onSelect}
      className="flex w-full gap-3 rounded-xl p-3.5 text-left transition-transform hover:scale-[1.01] active:scale-[0.99]"
      style={{
        ...glassCardStyle(tokens),
        outline: outlineColor ? `2px solid ${outlineColor}` : undefined,
      }}
    >
      <div
        className="relative w-2 shrink-0 overflow-hidden rounded"
        style={{ height: 48, background: `color-mix(in srgb, ${colors.textSecondary} 20%, transparent)` }}
      >
        <div
          className="absolute bottom-0 left-0 right-0 rounded"
          style={{ height: barHeight, background: accent }}
        />
      </div>
      <div className="min-w-0">
        <p
          className="text-base font-semibold"
          style={{ color: selected ? colors.brandPrimary : colors.textPrimary }}
        >
          {option.label}
        </p>
        {option.description ? (
          <p className="mt-1 text-sm opacity-70" style={{ color: colors.textSecondary }}>
            {option.description}
          </p>
        ) : null}
      </div>
    </button>
  );
}

function WrapChip({
  label,
  selected,
  error,
  onToggle,
}: {
  label: string;
  selected: boolean;
  error?: string;
  onToggle: () => void;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const borderColor = selected
    ? colors.brandPrimary
    : error
      ? colors.error
      : `color-mix(in srgb, ${colors.border} 40%, transparent)`;
  return (
    <button
      type="button"
      onClick={onToggle}
      className="rounded-full px-3.5 py-2 text-sm transition-colors"
      style={{
        color: selected ? colors.brandPrimary : colors.textSecondary,
        background: selected ? `color-mix(in srgb, ${colors.brandPrimary} 12%, transparent)` : "transparent",
        border: `1px solid ${borderColor}`,
      }}
    >
      {label}
    </button>
  );
}

function CompactChip({
  label,
  selected,
  error,
  onToggle,
}: {
  label: string;
  selected: boolean;
  error?: string;
  onToggle: () => void;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const borderColor = selected
    ? colors.brandPrimary
    : error
      ? colors.error
      : `color-mix(in srgb, ${colors.border} 40%, transparent)`;
  return (
    <button
      type="button"
      onClick={onToggle}
      className="rounded-lg px-2 py-2 text-center text-[11px] leading-tight transition-colors"
      style={{
        color: selected ? colors.brandPrimary : colors.textSecondary,
        background: selected ? `color-mix(in srgb, ${colors.brandPrimary} 12%, transparent)` : "transparent",
        border: `1px solid ${borderColor}`,
      }}
    >
      {label}
    </button>
  );
}

function PreviewPanel({
  preview,
  typeCode,
}: {
  preview: PersonalSetupPreview;
  typeCode: PersonalMomentTypeCode;
}) {
  switch (typeCode) {
    case "FUTURE_BUILDING":
      return preview.future_building ? (
        <FutureBuildingPreviewPanel block={preview.future_building} />
      ) : null;
    case "LIFESTYLE":
      return preview.lifestyle ? <LifestylePreviewPanel block={preview.lifestyle} /> : null;
    case "RELATIONSHIPS":
      return preview.emotional_security ? (
        <EmotionalSecurityPreviewPanel block={preview.emotional_security} />
      ) : null;
    default:
      return <LifeOpsPreviewPanel preview={preview} />;
  }
}

function LifeOpsPreviewPanel({ preview }: { preview: PersonalSetupPreview }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <div className="rounded-xl p-4" style={glassCardStyle(tokens)}>
      <div className="mb-3 flex items-center gap-2">
        <h3 className="flex-1 text-lg font-semibold" style={{ color: colors.brandTertiary }}>
          Momentra is shaping your rhythm
        </h3>
        <RefreshCw className="size-4 opacity-70" style={{ color: colors.brandTertiary }} />
      </div>
      <p className="mb-3 text-sm leading-relaxed opacity-80" style={{ color: colors.textSecondary }}>
        {preview.narrative}
      </p>
      <MeterRow name="Rhythm" meter={preview.rhythm} color={colors.brandPrimary} />
      <MeterRow name="Pressure" meter={preview.pressure} color={colors.error} />
      <MeterRow name="Recovery" meter={preview.recovery} color={colors.brandTertiary} />
      <ul className="mt-3 space-y-2">
        {preview.runtime_priorities.map((priority) => (
          <li key={priority} className="flex items-center gap-2 text-sm">
            <span className="size-1.5 rounded-full" style={{ background: colors.brandTertiary }} />
            {priority}
          </li>
        ))}
      </ul>
      <div className="mt-4 flex flex-wrap gap-2">
        {preview.identity_chips.map((chip) => (
          <span
            key={chip}
            className="rounded-full px-2.5 py-1 text-[10px] font-semibold tracking-wide"
            style={{
              color: colors.brandPrimary,
              background: `color-mix(in srgb, ${colors.brandPrimary} 10%, transparent)`,
              border: `1px solid color-mix(in srgb, ${colors.brandPrimary} 20%, transparent)`,
            }}
          >
            {chip.toUpperCase()}
          </span>
        ))}
      </div>
    </div>
  );
}

function FutureBuildingPreviewPanel({ block }: { block: PersonalFutureBuildingSetupPreview }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <div className="space-y-3">
      <DomainIdentityCard
        badgeLabel={block.assigned_identity.badge_label}
        title={block.assigned_identity.title}
        body={block.assigned_identity.body}
      />
      <DomainGlassSection>
        <DomainSectionHeader title="Runtime Projection" />
        <div className="mt-3">
          {block.runtime_projection.map((row) => (
            <DomainKvRow
              key={row.label}
              label={row.label}
              value={row.value}
              accent={accentFromToken(row.accent, colors)}
            />
          ))}
        </div>
      </DomainGlassSection>
      <DomainGlassSection>
        <DomainSectionHeader title="Future Horizon Preview" />
        <div className="mt-3">
          <DomainKvRow label="Trajectory" value={block.future_horizon.trajectory} />
          <DomainProgressGlow percent={block.future_horizon.momentum_percent} />
          <DomainKvRow
            label="Opportunity"
            value={block.future_horizon.opportunity}
            accent={colors.brandTertiary}
          />
          <DomainKvRow
            label="Breakthrough"
            value={block.future_horizon.breakthrough}
            accent={colors.brandPrimary}
          />
          <DomainInsightCard
            title={block.future_horizon.obstacle_title}
            body={block.future_horizon.obstacle_body}
          />
        </div>
      </DomainGlassSection>
    </div>
  );
}

function LifestylePreviewPanel({ block }: { block: PersonalLifestyleSetupPreview }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <div className="space-y-3">
      <DomainIdentityCard
        badgeLabel={block.assigned_identity.badge_label}
        title={block.assigned_identity.title}
        body={block.assigned_identity.body}
      />
      <DomainGlassSection>
        <DomainSectionHeader title="Lifestyle Snapshot" />
        <div className="mt-3">
          {block.lifestyle_snapshot.map((row) => (
            <DomainKvRow
              key={row.label}
              label={row.label}
              value={row.value}
              accent={accentFromToken(row.accent, colors)}
            />
          ))}
        </div>
      </DomainGlassSection>
      <DomainGlassSection>
        <DomainSectionHeader title="Lifestyle Horizon Preview" />
        <div className="mt-3">
          <DomainKvRow label="Trajectory" value={block.lifestyle_horizon.trajectory} />
          <DomainProgressGlow percent={block.lifestyle_horizon.vitality_percent} />
          <DomainKvRow
            label="Opportunity"
            value={block.lifestyle_horizon.opportunity}
            accent={colors.brandTertiary}
          />
          <DomainKvRow
            label="Fulfillment"
            value={block.lifestyle_horizon.fulfillment}
            accent={colors.brandPrimary}
          />
          <DomainInsightCard
            title={block.lifestyle_horizon.gap_title}
            body={block.lifestyle_horizon.gap_body}
          />
        </div>
      </DomainGlassSection>
    </div>
  );
}

function EmotionalSecurityPreviewPanel({ block }: { block: PersonalEmotionalSecuritySetupPreview }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <div className="space-y-3">
      <DomainIdentityCard
        badgeLabel={block.assigned_identity.badge_label}
        title={block.assigned_identity.title}
        body={block.assigned_identity.body}
      />
      <DomainGlassSection>
        <DomainSectionHeader title="Relationship Snapshot" />
        <div className="mt-3">
          {block.relationship_snapshot.map((row) => (
            <DomainKvRow
              key={row.label}
              label={row.label}
              value={row.value}
              accent={accentFromToken(row.accent, colors)}
            />
          ))}
        </div>
      </DomainGlassSection>
      <DomainGlassSection>
        <DomainSectionHeader title="Relationship Horizon Preview" />
        <div className="mt-3">
          <DomainKvRow label="Trajectory" value={block.relationship_horizon.trajectory} />
          <DomainProgressGlow percent={block.relationship_horizon.bond_percent} />
          <DomainKvRow
            label="Opportunity"
            value={block.relationship_horizon.opportunity}
            accent={colors.brandTertiary}
          />
          <DomainKvRow
            label="Potential"
            value={block.relationship_horizon.potential}
            accent={colors.brandPrimary}
          />
          <DomainInsightCard
            title={block.relationship_horizon.gap_title}
            body={block.relationship_horizon.gap_body}
          />
        </div>
      </DomainGlassSection>
    </div>
  );
}

function MeterRow({
  name,
  meter,
  color,
}: {
  name: string;
  meter: PersonalSetupPreview["rhythm"];
  color: string;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <div className="mb-3">
      <div className="mb-1 flex justify-between text-[11px] font-medium uppercase tracking-wide opacity-70">
        <span>{name}</span>
        <span>{meter.label}</span>
      </div>
      <div
        className="h-1 overflow-hidden rounded-full"
        style={{ background: colors.surfaceContainer }}
      >
        <div
          className="h-full rounded-full transition-all duration-300"
          style={{ width: `${meter.pct}%`, background: color }}
        />
      </div>
    </div>
  );
}

function SummaryPanel({
  setup,
  answers,
}: {
  setup: PersonalSetupResponse;
  answers: Record<string, string | string[]>;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const rows = buildSummaryRows(setup, answers);
  if (rows.length === 0) return null;

  return (
    <div
      className="rounded-xl p-4"
      style={{ background: `color-mix(in srgb, ${colors.surfaceContainer} 60%, transparent)` }}
    >
      <h4 className="mb-3 text-sm font-semibold tracking-wide opacity-80">Intelligence Profile</h4>
      {rows.map(([label, value]) => (
        <div key={label} className="mb-2 flex justify-between gap-4 text-sm">
          <span>{label}</span>
          <span className="text-right font-medium" style={{ color: colors.brandPrimary }}>
            {value}
          </span>
        </div>
      ))}
    </div>
  );
}

export function buildSummaryRows(
  setup: PersonalSetupResponse,
  answers: Record<string, string | string[]>,
): [string, string][] {
  const rows: [string, string][] = [];
  for (const field of setup.fields) {
    const value = answers[field.field_key];
    if (typeof value === "string" && value) {
      const label = optionLabel(setup, field.field_key, value);
      if (label) rows.push([field.label, label]);
    } else if (Array.isArray(value) && value.length > 0) {
      const labels = value
        .map((v) => optionLabel(setup, field.field_key, v))
        .filter(Boolean) as string[];
      if (labels.length) rows.push([field.label, labels.join(" + ")]);
    }
  }
  return rows;
}

function optionLabel(
  setup: PersonalSetupResponse,
  fieldKey: string,
  value: string,
): string | undefined {
  return setup.fields
    .find((f) => f.field_key === fieldKey)
    ?.options?.find((o) => o.value === value)?.label;
}
