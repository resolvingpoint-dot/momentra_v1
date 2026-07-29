"use client";

import { useRef, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { putToSignedUrl } from "@/lib/api/client";
import {
  MEMORY_MAX_FILES,
  acceptForMemoryFormat,
  formatFileSize,
  prepareMemoryFile,
  type MemoryMediaFormat,
} from "@/lib/media/memoryUpload";
import {
  confirmTripAttachment,
  createTripAttachmentUploadUrl,
} from "@/repositories/GroupTripQuickAddRepository";

type MemoryMediaUploaderProps = {
  momentId: string;
  format: MemoryMediaFormat;
  paths: string[];
  onChange: (paths: string[]) => void;
  error?: string;
};

type PendingItem = {
  id: string;
  name: string;
  status: "uploading" | "done" | "error";
  message?: string;
};

export function MemoryMediaUploader(props: MemoryMediaUploaderProps) {
  const { colors } = useThemeTokens();
  const inputRef = useRef<HTMLInputElement>(null);
  const [pending, setPending] = useState<PendingItem[]>([]);
  const [localError, setLocalError] = useState<string | null>(null);

  if (props.format === "note") {
    return null;
  }

  const busy = pending.some((p) => p.status === "uploading");

  async function onFilesSelected(fileList: FileList | null) {
    if (!fileList?.length) return;
    setLocalError(null);
    const remaining = MEMORY_MAX_FILES - props.paths.length;
    if (remaining <= 0) {
      setLocalError(`You can attach up to ${MEMORY_MAX_FILES} files.`);
      return;
    }
    const files = Array.from(fileList).slice(0, remaining);
    const nextPaths = [...props.paths];

    for (const file of files) {
      const id = `${file.name}-${file.size}-${Date.now()}`;
      setPending((prev) => [...prev, { id, name: file.name, status: "uploading" }]);
      try {
        const prepared = await prepareMemoryFile(file, props.format);
        const upload = await createTripAttachmentUploadUrl(props.momentId, {
          content_type: prepared.contentType,
          byte_size: prepared.blob.size,
          purpose: "memory",
        });
        await putToSignedUrl(upload.upload_url, prepared.blob, prepared.contentType);
        const confirmed = await confirmTripAttachment(props.momentId, {
          storage_path: upload.storage_path,
          purpose: "memory",
        });
        nextPaths.push(confirmed.storage_path);
        props.onChange([...nextPaths]);
        setPending((prev) =>
          prev.map((p) => (p.id === id ? { ...p, status: "done" as const } : p)),
        );
      } catch (err) {
        const message = err instanceof Error ? err.message : "Upload failed";
        setPending((prev) =>
          prev.map((p) => (p.id === id ? { ...p, status: "error" as const, message } : p)),
        );
        setLocalError(message);
      }
    }
    if (inputRef.current) inputRef.current.value = "";
  }

  function removePath(path: string) {
    props.onChange(props.paths.filter((p) => p !== path));
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-2">
        <p className="text-xs font-bold uppercase tracking-wide" style={{ color: colors.textSecondary }}>
          Attachments
        </p>
        <p className="text-[11px]" style={{ color: colors.textSecondary }}>
          Up to {MEMORY_MAX_FILES} files · 10 MB each
        </p>
      </div>

      <button
        type="button"
        disabled={busy || props.paths.length >= MEMORY_MAX_FILES}
        onClick={() => inputRef.current?.click()}
        className="flex min-h-24 w-full flex-col items-center justify-center rounded-xl border border-dashed px-3 py-4 text-sm"
        style={{
          borderColor: `${colors.brandPrimary}55`,
          color: colors.textSecondary,
          background: `${colors.brandPrimary}0d`,
        }}
      >
        <span className="font-semibold" style={{ color: colors.textPrimary }}>
          {props.format === "photo"
            ? "Add photos"
            : props.format === "video"
              ? "Add video"
              : "Add PDF"}
        </span>
        <span className="mt-1 text-xs">
          {busy ? "Uploading…" : "Tap to choose files (images are compressed under 10 MB)"}
        </span>
      </button>

      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept={acceptForMemoryFormat(props.format)}
        multiple={props.format === "photo"}
        onChange={(e) => void onFilesSelected(e.target.files)}
      />

      {props.paths.length ? (
        <ul className="space-y-1.5">
          {props.paths.map((path) => (
            <li
              key={path}
              className="flex items-center justify-between gap-2 rounded-lg px-3 py-2 text-xs"
              style={{ background: colors.surfaceContainer, color: colors.textPrimary }}
            >
              <span className="truncate">{path.split("/").pop()}</span>
              <button
                type="button"
                className="shrink-0 underline"
                style={{ color: colors.textSecondary }}
                onClick={() => removePath(path)}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      ) : null}

      {pending
        .filter((p) => p.status !== "done")
        .map((p) => (
          <p key={p.id} className="text-xs" style={{ color: p.status === "error" ? colors.error : colors.textSecondary }}>
            {p.name}: {p.status === "uploading" ? "Uploading…" : p.message || "Failed"}
          </p>
        ))}

      {(props.error || localError) && (
        <p className="text-xs" style={{ color: colors.error }}>
          {props.error || localError}
        </p>
      )}
    </div>
  );
}

export function memoryPathsFromState(value: unknown): string[] {
  if (Array.isArray(value)) return value.map(String).filter(Boolean);
  if (typeof value === "string" && value.trim()) {
    return value.split(",").map((p) => p.trim()).filter(Boolean);
  }
  return [];
}

export { formatFileSize };
