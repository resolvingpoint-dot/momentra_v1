/** sessionStorage keys for invite tokens / accept results awaiting the app shell. */
export const PENDING_INVITE_KEY = "momentra:pending-invite";
export const PENDING_COMPANY_INVITE_KEY = "momentra:pending-company-invite";
export const PENDING_INVITE_RESULT_KEY = "momentra:invite-joined-result";

export type StashedInviteResult = {
  moment_id: string;
  moment_name: string;
  moment_type?: string | null;
  already_member?: boolean;
  participant_id?: string | null;
};

export function stashPendingInvite(token: string): void {
  if (typeof window === "undefined") return;
  const t = token.trim();
  if (!t) return;
  sessionStorage.setItem(PENDING_INVITE_KEY, t);
}

export function consumePendingInvite(): string | null {
  if (typeof window === "undefined") return null;
  const t = sessionStorage.getItem(PENDING_INVITE_KEY);
  sessionStorage.removeItem(PENDING_INVITE_KEY);
  return t?.trim() || null;
}

export function stashPendingCompanyInvite(token: string): void {
  if (typeof window === "undefined") return;
  const t = token.trim();
  if (!t) return;
  sessionStorage.setItem(PENDING_COMPANY_INVITE_KEY, t);
}

export function consumePendingCompanyInvite(): string | null {
  if (typeof window === "undefined") return null;
  const t = sessionStorage.getItem(PENDING_COMPANY_INVITE_KEY);
  sessionStorage.removeItem(PENDING_COMPANY_INVITE_KEY);
  return t?.trim() || null;
}

export function stashInviteJoinedResult(result: StashedInviteResult): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(PENDING_INVITE_RESULT_KEY, JSON.stringify(result));
}

export function consumeInviteJoinedResult(): StashedInviteResult | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(PENDING_INVITE_RESULT_KEY);
  sessionStorage.removeItem(PENDING_INVITE_RESULT_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as StashedInviteResult;
    if (!parsed?.moment_id) return null;
    return parsed;
  } catch {
    return null;
  }
}
