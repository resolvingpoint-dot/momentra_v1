/** Activity list filter / page domain model — forwarded as server query params. */

export type ActivitySort = "newest" | "oldest";

export type BusinessActivityFilters = {
  search?: string;
  actionTypes?: string[];
  memberId?: string | null;
  status?: "all" | "active" | "voided";
  dateFrom?: string | null;
  dateTo?: string | null;
  sort?: ActivitySort;
};

export type BusinessActivityPage = {
  page: number;
  pageSize: number;
};

export const DEFAULT_ACTIVITY_PAGE_SIZE = 20;

export function activityFilterKey(
  filters?: BusinessActivityFilters | null,
  page?: BusinessActivityPage,
): string {
  const f = filters ?? {};
  const p = page ?? { page: 1, pageSize: DEFAULT_ACTIVITY_PAGE_SIZE };
  return [
    f.search ?? "",
    (f.actionTypes ?? []).slice().sort().join(","),
    f.memberId ?? "",
    f.status ?? "active",
    f.dateFrom ?? "",
    f.dateTo ?? "",
    f.sort ?? "newest",
    String(p.page),
    String(p.pageSize),
  ].join("|");
}

/** Build GET .../activity query string. Repository forwards these; no client filtering. */
export function buildActivityQuery(
  filters?: BusinessActivityFilters | null,
  page?: BusinessActivityPage | null,
): string {
  const f = filters ?? {};
  const p = page ?? { page: 1, pageSize: DEFAULT_ACTIVITY_PAGE_SIZE };
  const params = new URLSearchParams();

  if (f.actionTypes?.length) {
    params.set("action", f.actionTypes.map((a) => a.toUpperCase()).join(","));
  }
  if (f.memberId) params.set("member", f.memberId);
  params.set("status", f.status ?? "active");
  if (f.dateFrom) params.set("from", f.dateFrom);
  if (f.dateTo) params.set("to", f.dateTo);
  params.set("page", String(Math.max(1, p.page ?? 1)));
  params.set("page_size", String(p.pageSize ?? DEFAULT_ACTIVITY_PAGE_SIZE));
  params.set("sort", f.sort ?? "newest");
  if (f.search?.trim()) params.set("q", f.search.trim());

  const qs = params.toString();
  return qs ? `?${qs}` : "";
}
