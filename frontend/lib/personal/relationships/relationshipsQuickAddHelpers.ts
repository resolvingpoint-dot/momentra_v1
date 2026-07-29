export const RS_EVENT_TYPES = new Set([
  "CONNECTION",
  "SUPPORT",
  "SHARED_EXPERIENCE",
  "RELATIONSHIP_INVESTMENT",
  "RELATIONSHIP_ADJUST",
  "ADJUST",
]);

export function normalizeRelationshipsEventType(eventType: string): string {
  return eventType === "RELATIONSHIP_ADJUST" ? "ADJUST" : eventType;
}

export function rsSelectorBlurb(eventType: string): string {
  switch (normalizeRelationshipsEventType(eventType)) {
    case "SHARED_EXPERIENCE":
      return "Record time shared together";
    case "CONNECTION":
      return "Capture meaningful contact";
    case "SUPPORT":
      return "Record care or help";
    case "RELATIONSHIP_INVESTMENT":
      return "Log intentional relationship effort";
    case "ADJUST":
      return "Change a relationship priority";
    default:
      return "";
  }
}

export function rsGuidingQuestion(eventType: string): string {
  switch (normalizeRelationshipsEventType(eventType)) {
    case "SHARED_EXPERIENCE":
      return "What did you do together?";
    case "CONNECTION":
      return "Who did you connect with?";
    case "SUPPORT":
      return "What support happened?";
    case "RELATIONSHIP_INVESTMENT":
      return "What did you invest in this relationship?";
    case "ADJUST":
      return "What would you like to change?";
    default:
      return "What happened in your relationships?";
  }
}

export function rsTitlePlaceholder(eventType: string): string {
  switch (normalizeRelationshipsEventType(eventType)) {
    case "SHARED_EXPERIENCE":
      return "Dinner with my family";
    case "CONNECTION":
      return "Caught up after several months";
    case "SUPPORT":
      return "Helped a friend prepare for an interview";
    case "RELATIONSHIP_INVESTMENT":
      return "Planned a weekend together";
    case "ADJUST":
      return "Make more time for close friends";
    default:
      return "What happened?";
  }
}

export function rsSuccessMessage(eventType: string): string {
  switch (normalizeRelationshipsEventType(eventType)) {
    case "SHARED_EXPERIENCE":
      return "Shared experience saved";
    case "CONNECTION":
      return "Connection saved";
    case "SUPPORT":
      return "Support saved";
    case "RELATIONSHIP_INVESTMENT":
      return "Relationship investment saved";
    case "ADJUST":
      return "Relationship priority updated";
    default:
      return "Entry saved";
  }
}

export function rsErrorMessage(eventType: string): string {
  switch (normalizeRelationshipsEventType(eventType)) {
    case "SHARED_EXPERIENCE":
      return "Couldn't save the shared experience. Try again.";
    case "CONNECTION":
      return "Couldn't save the connection. Try again.";
    case "SUPPORT":
      return "Couldn't save the support entry. Try again.";
    case "RELATIONSHIP_INVESTMENT":
      return "Couldn't save the relationship investment. Try again.";
    case "ADJUST":
      return "Couldn't update the relationship. Try again.";
    default:
      return "Couldn't save. Try again.";
  }
}

export function requiredKeysForTab(tab: string): Set<string> {
  switch (normalizeRelationshipsEventType(tab)) {
    case "CONNECTION":
      return new Set(["connection_type"]);
    case "SUPPORT":
      return new Set(["support_type", "support_direction"]);
    case "SHARED_EXPERIENCE":
      return new Set(["experience_type"]);
    case "RELATIONSHIP_INVESTMENT":
      return new Set(["investment_type"]);
    case "ADJUST":
      return new Set(["adjustment_area"]);
    default:
      return new Set();
  }
}

export function canSubmitRelationships(
  tab: string,
  values: Record<string, string>,
  eventTitle: string,
): boolean {
  if (!eventTitle.trim()) return false;
  return [...requiredKeysForTab(tab)].every((key) => Boolean(values[key]?.trim()));
}

export const FIELD_TO_PAYLOAD_KEY: Record<string, string> = {
  notes: "notes",
  amount: "amount",
  spend_category: "spend_category",
  connection_type: "connection_type",
  relationship_type: "relationship_type",
  connection_quality: "connection_quality",
  emotional_tone: "emotional_tone",
  time_invested: "time_invested",
  support_type: "support_type",
  support_direction: "support_direction",
  support_impact: "support_impact",
  experience_type: "experience_type",
  value_received: "value_received",
  investment_type: "investment_type",
  investment_purpose: "investment_purpose",
  perceived_value: "perceived_value",
  adjustment_area: "adjustment_area",
  relationship_focus: "relationship_focus",
  priority_level: "priority_level",
  confidence_level: "confidence_level",
};

export function buildEmotionalSecurityPayload(values: Record<string, string>) {
  const payload: Record<string, string> = {};
  for (const [fieldKey, payloadKey] of Object.entries(FIELD_TO_PAYLOAD_KEY)) {
    const trimmed = values[fieldKey]?.trim();
    if (trimmed) payload[payloadKey] = trimmed;
  }
  return payload;
}
