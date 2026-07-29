/** Presentation-only field explainers for guided Business setup. */

export type SetupExplainer = { title: string; body: string };

export const SETUP_EXPLAINERS = {
  collection_rate_percent: {
    title: "Collection rate",
    body: "What percentage of expected revenue actually reaches your account? If you invoice ₹10 lakh and usually receive ₹8 lakh, enter 80%.",
  },
  operating_model: {
    title: "Operating model",
    body: "How decisions and responsibilities are organized—centralized, decentralized, hybrid, project-based, or by function.",
  },
  approval_threshold_minor: {
    title: "Approval threshold",
    body: "Spend at or above this amount needs approval before it can proceed. Enter the amount in normal currency units.",
  },
  revenue_model: {
    title: "Revenue model",
    body: "How the business primarily earns money—subscription, services, retail, marketplace, and so on.",
  },
  review_cycle: {
    title: "Review cycle",
    body: "How often this moment should be reviewed so alerts and check-ins stay useful without noise.",
  },
  monitoring_level: {
    title: "Monitoring",
    body: "How closely Momentra watches this moment. Light means important updates only; detailed means more frequent alerts.",
  },
  vendor_dependency_level: {
    title: "Vendor dependency",
    body: "How severely operations would be affected if a key vendor stopped delivering.",
  },
  issue_sensitivity: {
    title: "Issue sensitivity",
    body: "Controls how quickly Momentra highlights operational problems.",
  },
  runway_alert_threshold_months: {
    title: "Alert threshold",
    body: "Momentra warns you when estimated runway falls below this number of months.",
  },
  funding_sources: {
    title: "Funding sources",
    body: "Select every way the business is currently funded. You can choose more than one.",
  },
} as const satisfies Record<string, SetupExplainer>;

export function setupExplainer(key: keyof typeof SETUP_EXPLAINERS): SetupExplainer {
  return SETUP_EXPLAINERS[key];
}
