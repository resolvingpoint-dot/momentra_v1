/** Extract invite JWT from QR payload / deep link / pasted text. */
export function extractInviteToken(raw: string): string | null {
  const parsed = parseInviteInput(raw);
  return parsed?.token ?? null;
}

export type InviteKind = "moment" | "company";

export type ParsedInvite = {
  token: string;
  kind: InviteKind;
};

/** Parse pasted/scanned invite text into token + kind (company vs moment). */
export function parseInviteInput(raw: string): ParsedInvite | null {
  const s = raw.trim();
  if (!s) return null;

  try {
    const url = new URL(s);
    const host = url.hostname.toLowerCase();
    const pathParts = url.pathname.split("/").filter(Boolean);
    const isInviteHost = host === "invite" || host === "company-invite";
    const companyIdx = pathParts.findIndex(
      (p) => p.toLowerCase() === "company-invite",
    );
    const inviteIdx = pathParts.findIndex((p) => p.toLowerCase() === "invite");
    const isMomentraHttps =
      url.protocol === "https:" &&
      (host === "momentra.tech" || host === "www.momentra.tech");
    const isMomentraScheme = url.protocol === "momentra:";

    if (
      isMomentraScheme ||
      isInviteHost ||
      companyIdx >= 0 ||
      inviteIdx >= 0 ||
      isMomentraHttps
    ) {
      const q = url.searchParams.get("token");
      const kind: InviteKind =
        host === "company-invite" ||
        companyIdx >= 0 ||
        (isMomentraScheme && host === "company-invite")
          ? "company"
          : "moment";

      if (q?.trim()) return { token: q.trim(), kind };

      if (host === "company-invite" || host === "invite") {
        const token = pathParts[0] || url.pathname.replace(/^\//, "");
        if (token && token.toLowerCase() !== "invite" && token.toLowerCase() !== "company-invite") {
          return { token, kind: host === "company-invite" ? "company" : "moment" };
        }
        return null;
      }
      if (companyIdx >= 0 && pathParts[companyIdx + 1]) {
        return { token: pathParts[companyIdx + 1], kind: "company" };
      }
      if (inviteIdx >= 0 && pathParts[inviteIdx + 1]) {
        return { token: pathParts[inviteIdx + 1], kind: "moment" };
      }
      const last = pathParts[pathParts.length - 1];
      if (last && last.toLowerCase() !== "invite" && last.toLowerCase() !== "company-invite") {
        return { token: last, kind };
      }
    }
  } catch {
    /* not a URL — treat as raw token */
  }

  if (s.length >= 8) return { token: s, kind: "moment" };
  return null;
}

/** Prefer company kind when pasting into Join Company (raw tokens are company). */
export function extractCompanyInviteToken(raw: string): string | null {
  const s = raw.trim();
  if (!s) return null;
  const parsed = parseInviteInput(s);
  if (!parsed) return null;
  if (parsed.kind === "company") return parsed.token;
  // Raw non-URL paste into Join Company → treat as workspace token
  try {
    new URL(s);
    return null;
  } catch {
    return parsed.token;
  }
}

export function isBusinessMomentType(momentType: string | null | undefined): boolean {
  const t = (momentType || "").toUpperCase().replace(/-/g, "_");
  if (
    t === "TEAM_OPERATIONS" ||
    t === "BUSINESS_RUNWAY" ||
    t === "BUSINESS_OPERATIONS" ||
    t === "PROJECT_OPERATIONS" ||
    t === "EVENT_OPERATIONS" ||
    t === "DEPARTMENT_OPERATIONS" ||
    t === "VENDOR_OPERATIONS" ||
    t === "CUSTOM_OPERATIONAL_MOMENT" ||
    t === "ORG"
  ) {
    return true;
  }
  return t.includes("BUSINESS") || t.startsWith("BIZ") || t.startsWith("TEAM_");
}
