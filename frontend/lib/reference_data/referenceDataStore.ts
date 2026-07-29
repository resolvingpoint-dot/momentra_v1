import { diskCacheLoad, diskCacheRemove, diskCacheSave } from "@/lib/cache/cacheStore";
import { MetadataRepository } from "@/lib/metadata/MetadataRepository";
import type { BootstrapVersionFields } from "@/lib/api/bootstrapTypes";
import type { ReferenceDataBootstrap } from "@/lib/reference_data/types";

const DISK_KEY = "reference_data_bootstrap";
const VERSION_DISK_KEY = "reference_data_versions";
const TTL_MS = 24 * 60 * 60 * 1000;

type Snapshot = {
  data: ReferenceDataBootstrap | null;
  loadedAt: number | null;
  isLoading: boolean;
  error: string | null;
};

let snapshot: Snapshot = {
  data: diskCacheLoad<ReferenceDataBootstrap>(DISK_KEY),
  loadedAt: null,
  isLoading: false,
  error: null,
};
snapshot.loadedAt = snapshot.data ? Date.now() : null;

const listeners = new Set<() => void>();

function notify() {
  listeners.forEach((fn) => fn());
}

function setSnapshot(patch: Partial<Snapshot>) {
  snapshot = { ...snapshot, ...patch };
  notify();
}

export function getReferenceDataSnapshot(): Snapshot {
  return snapshot;
}

export function subscribeReferenceData(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function getReferenceData(): ReferenceDataBootstrap | null {
  return snapshot.data;
}

export async function loadReferenceData(options: {
  force?: boolean;
  serverVersion?: number;
  versions?: BootstrapVersionFields;
} = {}): Promise<ReferenceDataBootstrap> {
  const { force = false, serverVersion, versions } = options;
  const cached = snapshot.data;
  const staleByTtl =
    snapshot.loadedAt !== null && Date.now() - snapshot.loadedAt > TTL_MS;

  const cachedVersions = diskCacheLoad<BootstrapVersionFields>(VERSION_DISK_KEY);
  const referenceVersion = versions?.reference_data_version ?? serverVersion;
  const versionMatches =
    referenceVersion === undefined ||
    cached?.reference_data_version === referenceVersion ||
    cached?.metadata_version === referenceVersion ||
    (cachedVersions?.reference_data_version === referenceVersion);

  if (cached && !force && !staleByTtl && versionMatches) {
    return cached;
  }

  setSnapshot({ isLoading: true, error: null });
  try {
    const data = await MetadataRepository.getBootstrap();
    diskCacheSave(DISK_KEY, data);
    if (versions) {
      diskCacheSave(VERSION_DISK_KEY, versions);
    } else if (data.reference_data_version !== undefined) {
      diskCacheSave(VERSION_DISK_KEY, {
        reference_data_version: data.reference_data_version,
        metadata_version: data.metadata_version,
      });
    }
    setSnapshot({ data, loadedAt: Date.now(), isLoading: false, error: null });
    return data;
  } catch (err) {
    const message = err instanceof Error ? err.message : "Failed to load reference data";
    if (cached) {
      setSnapshot({ isLoading: false, error: message });
      return cached;
    }
    setSnapshot({ isLoading: false, error: message });
    throw err;
  }
}

export function invalidateReferenceData(): void {
  diskCacheRemove(DISK_KEY);
  diskCacheRemove(VERSION_DISK_KEY);
  snapshot = { data: null, loadedAt: null, isLoading: false, error: null };
  notify();
}

export function invalidateReferenceDataForVersions(
  previous: BootstrapVersionFields,
  next: BootstrapVersionFields,
): void {
  const referenceChanged =
    previous.reference_data_version !== undefined &&
    next.reference_data_version !== undefined &&
    previous.reference_data_version !== next.reference_data_version;
  const templateChanged =
    previous.template_version !== undefined &&
    next.template_version !== undefined &&
    previous.template_version !== next.template_version;
  const uiSchemaChanged =
    previous.ui_schema_version !== undefined &&
    next.ui_schema_version !== undefined &&
    previous.ui_schema_version !== next.ui_schema_version;

  if (referenceChanged || templateChanged || uiSchemaChanged) {
    invalidateReferenceData();
  }
}

export function clearReferenceDataOnLogout(): void {
  diskCacheRemove(DISK_KEY);
  diskCacheRemove(VERSION_DISK_KEY);
  snapshot = { data: null, loadedAt: null, isLoading: false, error: null };
  notify();
}

export async function ensureReferenceDataForBootstrap(
  versions: BootstrapVersionFields | number | undefined,
): Promise<ReferenceDataBootstrap | null> {
  const normalized: BootstrapVersionFields | undefined =
    typeof versions === "number"
      ? { reference_data_version: versions, metadata_version: versions }
      : versions;

  if (!normalized?.reference_data_version && !normalized?.metadata_version) {
    return snapshot.data;
  }

  const cached = snapshot.data;
  const cachedVersions = diskCacheLoad<BootstrapVersionFields>(VERSION_DISK_KEY);
  const targetVersion =
    normalized.reference_data_version ?? normalized.metadata_version;
  const cachedVersion =
    cachedVersions?.reference_data_version ??
    cached?.reference_data_version ??
    cachedVersions?.metadata_version ??
    cached?.metadata_version;

  if (cached && targetVersion !== undefined && cachedVersion === targetVersion) {
    return cached;
  }

  try {
    return await loadReferenceData({
      serverVersion: targetVersion,
      versions: normalized,
      force: true,
    });
  } catch {
    return cached;
  }
}
