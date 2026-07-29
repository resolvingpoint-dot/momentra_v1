import { describe, expect, it } from "vitest";
import {
  MEMORY_MAX_BYTES,
  MEMORY_MAX_FILES,
  acceptForMemoryFormat,
  formatFileSize,
  isAllowedMimeForFormat,
} from "./memoryUpload";

describe("memoryUpload", () => {
  it("exposes 10 MB / 10 file limits", () => {
    expect(MEMORY_MAX_BYTES).toBe(10 * 1024 * 1024);
    expect(MEMORY_MAX_FILES).toBe(10);
  });

  it("gates accept strings by format", () => {
    expect(acceptForMemoryFormat("photo")).toContain("image/");
    expect(acceptForMemoryFormat("video")).toContain("video/");
    expect(acceptForMemoryFormat("pdf")).toContain("application/pdf");
    expect(acceptForMemoryFormat("note")).toBe("");
  });

  it("validates MIME by format", () => {
    expect(isAllowedMimeForFormat("photo", "image/jpeg")).toBe(true);
    expect(isAllowedMimeForFormat("video", "video/mp4")).toBe(true);
    expect(isAllowedMimeForFormat("pdf", "application/pdf")).toBe(true);
    expect(isAllowedMimeForFormat("photo", "application/pdf")).toBe(false);
    expect(isAllowedMimeForFormat("video", "image/png")).toBe(false);
  });

  it("formats sizes", () => {
    expect(formatFileSize(512)).toBe("512 B");
    expect(formatFileSize(2048)).toContain("KB");
    expect(formatFileSize(MEMORY_MAX_BYTES)).toContain("MB");
  });
});
