/** Client-side media helpers for Group Memory uploads (≤10 MB). */

export const MEMORY_MAX_BYTES = 10 * 1024 * 1024;
export const MEMORY_MAX_FILES = 10;

export type MemoryMediaFormat = "photo" | "video" | "pdf" | "note";

const IMAGE_TYPES = new Set([
  "image/jpeg",
  "image/jpg",
  "image/png",
  "image/webp",
  "image/heic",
  "image/gif",
]);
const VIDEO_TYPES = new Set(["video/mp4", "video/quicktime", "video/webm"]);
const PDF_TYPES = new Set(["application/pdf"]);

export function acceptForMemoryFormat(format: MemoryMediaFormat): string {
  switch (format) {
    case "photo":
      return "image/jpeg,image/png,image/webp,image/heic,image/gif,image/*";
    case "video":
      return "video/mp4,video/quicktime,video/webm,video/*";
    case "pdf":
      return "application/pdf";
    default:
      return "";
  }
}

export function isAllowedMimeForFormat(format: MemoryMediaFormat, mime: string): boolean {
  const ct = (mime || "").toLowerCase();
  if (format === "photo") return IMAGE_TYPES.has(ct) || ct.startsWith("image/");
  if (format === "video") return VIDEO_TYPES.has(ct) || ct.startsWith("video/");
  if (format === "pdf") return PDF_TYPES.has(ct);
  return false;
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * Re-encode an image as JPEG under maxBytes via canvas resize + quality loop.
 * Returns null when the image cannot be brought under the limit.
 */
export async function compressImageToMaxBytes(
  file: File,
  maxBytes: number = MEMORY_MAX_BYTES,
): Promise<{ blob: Blob; contentType: string } | null> {
  if (!file.type.startsWith("image/") && !IMAGE_TYPES.has(file.type.toLowerCase())) {
    return null;
  }
  if (file.size <= maxBytes && (file.type === "image/jpeg" || file.type === "image/jpg")) {
    return { blob: file, contentType: "image/jpeg" };
  }

  const bitmap = await createImageBitmap(file);
  try {
    let width = bitmap.width;
    let height = bitmap.height;
    const maxDim = 4096;
    if (width > maxDim || height > maxDim) {
      const scale = Math.min(maxDim / width, maxDim / height);
      width = Math.max(1, Math.round(width * scale));
      height = Math.max(1, Math.round(height * scale));
    }

    for (let attempt = 0; attempt < 6; attempt++) {
      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      if (!ctx) return null;
      ctx.drawImage(bitmap, 0, 0, width, height);

      let quality = 0.92;
      while (quality >= 0.35) {
        const blob = await new Promise<Blob | null>((resolve) =>
          canvas.toBlob((b) => resolve(b), "image/jpeg", quality),
        );
        if (blob && blob.size <= maxBytes) {
          return { blob, contentType: "image/jpeg" };
        }
        quality -= 0.12;
      }

      width = Math.max(1, Math.round(width * 0.75));
      height = Math.max(1, Math.round(height * 0.75));
    }
  } finally {
    bitmap.close();
  }
  return null;
}

export async function prepareMemoryFile(
  file: File,
  format: MemoryMediaFormat,
): Promise<{ blob: Blob; contentType: string; name: string }> {
  if (format === "note") {
    throw new Error("Notes do not include media attachments.");
  }
  if (!isAllowedMimeForFormat(format, file.type)) {
    throw new Error(`This file type is not allowed for ${format}.`);
  }

  if (format === "photo") {
    const compressed = await compressImageToMaxBytes(file, MEMORY_MAX_BYTES);
    if (!compressed) {
      throw new Error("Could not compress this image under 10 MB. Try a smaller photo.");
    }
    return {
      blob: compressed.blob,
      contentType: compressed.contentType,
      name: file.name.replace(/\.[^.]+$/, "") + ".jpg",
    };
  }

  if (file.size > MEMORY_MAX_BYTES) {
    throw new Error(
      `${format === "video" ? "Video" : "PDF"} must be 10 MB or smaller (${formatFileSize(file.size)}).`,
    );
  }
  return {
    blob: file,
    contentType: file.type || (format === "pdf" ? "application/pdf" : "video/mp4"),
    name: file.name,
  };
}
