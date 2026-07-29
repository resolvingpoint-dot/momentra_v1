/** Shared WhatsApp-style poll payload for all group QuickAdds. */

export type PollFormLike = Record<string, string | string[] | number | boolean | undefined | null>;

const MAX_OPTIONS = 8;
const MIN_OPTIONS = 2;

export function pollOptionsFromFormState(state: PollFormLike): string[] {
  if (Array.isArray(state.options)) {
    return state.options.map((x) => String(x ?? "").trim()).filter(Boolean);
  }
  const keyed = Array.from({ length: MAX_OPTIONS }, (_, i) => String(state[`option_${i}`] ?? "").trim()).filter(
    Boolean,
  );
  if (keyed.length) return keyed;
  return String(state.options ?? "")
    .split(/[\n,]/)
    .map((x) => x.trim())
    .filter(Boolean);
}

export function allowMultipleFromFormState(state: PollFormLike): boolean {
  if (typeof state.allow_multiple_answers === "boolean") return state.allow_multiple_answers;
  const raw = String(state.allow_multiple_answers ?? "").toLowerCase();
  if (raw === "true" || raw === "1") return true;
  const pollType = String(state.poll_type ?? "").toLowerCase();
  return ["multiple", "multi", "multi_choice", "multiple_choice"].includes(pollType);
}

export function validatePollFormState(state: PollFormLike): Record<string, string> {
  const errors: Record<string, string> = {};
  if (!String(state.question ?? "").trim()) errors.question = "Question is required";
  if (pollOptionsFromFormState(state).length < MIN_OPTIONS) {
    errors.options = "Add at least 2 options";
  }
  return errors;
}

export function buildSharedPollPayload(state: PollFormLike): {
  question: string;
  options: string[];
  allow_multiple_answers: boolean;
} {
  return {
    question: String(state.question ?? "").trim(),
    options: pollOptionsFromFormState(state),
    allow_multiple_answers: allowMultipleFromFormState(state),
  };
}

export function pollReviewRows(state: PollFormLike): Array<{ label: string; value: string }> {
  const payload = buildSharedPollPayload(state);
  return [
    { label: "Question", value: payload.question },
    { label: "Options", value: payload.options.join(", ") },
    { label: "Multiple answers", value: payload.allow_multiple_answers ? "Yes" : "No" },
  ];
}

export const POLL_INITIAL_STATE = {
  options: ["", ""] as string[],
  allow_multiple_answers: false,
};

export { MAX_OPTIONS, MIN_OPTIONS };
