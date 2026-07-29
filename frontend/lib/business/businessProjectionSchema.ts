/**
 * Business projection payload schema version.
 * Bump when Pulse/Moments/Life/Memory (or sibling) DTO shapes change incompatibly.
 * Embedded in all client cache keys so old disk/memory entries are ignored.
 */
export const BUSINESS_PROJECTION_SCHEMA_VERSION = 1;

export function businessProjectionSchemaSegment(): string {
  return `v${BUSINESS_PROJECTION_SCHEMA_VERSION}`;
}
