"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { TextField, Toggle } from "@/components/group/action-center/fields";
import type { FormState } from "@/components/group/action-center/ProgressiveActionForm";
import { MAX_OPTIONS, MIN_OPTIONS } from "@/lib/quick_add/payloadBuilders/sharedPoll";

type PollComposerProps = {
  state: FormState;
  set: (key: string, value: FormState[string]) => void;
  errors: Record<string, string>;
};

function optionsFromState(state: FormState): string[] {
  if (Array.isArray(state.options) && state.options.length >= MIN_OPTIONS) {
    return state.options.map((x) => String(x ?? ""));
  }
  return ["", ""];
}

/** WhatsApp-style poll create: question, option rows, allow multiple answers. */
export function PollComposer({ state, set, errors }: PollComposerProps) {
  const { colors } = useThemeTokens();
  const options = optionsFromState(state);
  const allowMultiple = Boolean(state.allow_multiple_answers);

  const setOption = (index: number, value: string) => {
    const next = [...options];
    next[index] = value;
    set("options", next);
  };

  const addOption = () => {
    if (options.length >= MAX_OPTIONS) return;
    set("options", [...options, ""]);
  };

  const removeOption = (index: number) => {
    if (options.length <= MIN_OPTIONS) return;
    set(
      "options",
      options.filter((_, i) => i !== index),
    );
  };

  return (
    <div className="space-y-4">
      <TextField
        label="Question"
        value={String(state.question ?? "")}
        onChange={(v) => set("question", v)}
        required
        error={errors.question}
        placeholder="Ask a question"
      />

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wide" style={{ color: colors.textSecondary }}>
            Options *
          </span>
          {options.length < MAX_OPTIONS ? (
            <button
              type="button"
              onClick={addOption}
              className="text-xs font-semibold"
              style={{ color: colors.brandPrimary }}
            >
              + Add option
            </button>
          ) : null}
        </div>
        <div className="space-y-2">
          {options.map((opt, i) => (
            <div key={i} className="flex items-center gap-2">
              <input
                type="text"
                value={opt}
                onChange={(e) => setOption(i, e.target.value)}
                placeholder={`Option ${i + 1}`}
                className="w-full rounded-xl px-3 py-2.5 text-sm"
                style={{
                  background: colors.surfaceContainer,
                  color: colors.textPrimary,
                  border: `1px solid ${colors.textSecondary}22`,
                }}
              />
              {options.length > MIN_OPTIONS ? (
                <button
                  type="button"
                  onClick={() => removeOption(i)}
                  className="shrink-0 px-2 text-xs font-semibold"
                  style={{ color: colors.error }}
                  aria-label={`Remove option ${i + 1}`}
                >
                  Remove
                </button>
              ) : null}
            </div>
          ))}
        </div>
        {errors.options ? (
          <p className="text-xs" style={{ color: colors.error }}>
            {errors.options}
          </p>
        ) : null}
      </div>

      <Toggle
        label="Allow multiple answers"
        value={allowMultiple}
        onChange={(v) => set("allow_multiple_answers", v)}
      />
    </div>
  );
}
