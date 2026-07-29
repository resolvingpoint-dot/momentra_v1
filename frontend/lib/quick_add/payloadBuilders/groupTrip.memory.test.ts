import { describe, expect, it } from "vitest";
import { buildTripQuickAddPayload } from "./groupTrip";

describe("buildTripQuickAddPayload MEMORY", () => {
  it("includes media_storage_paths and format metadata", () => {
    const payload = buildTripQuickAddPayload("MEMORY", {
      title: "Sunset at the beach",
      description: "Golden hour",
      caption: "Golden hour",
      memory_format: "photo",
      memory_category: "highlight",
      media_storage_paths: ["trip-attachments/abc/one.jpg", "trip-attachments/abc/two.jpg"],
    });
    expect(payload.title).toBe("Sunset at the beach");
    expect(payload.media_storage_paths).toEqual([
      "trip-attachments/abc/one.jpg",
      "trip-attachments/abc/two.jpg",
    ]);
    expect(payload.memory_format).toBe("photo");
    expect(payload.memory_category).toBe("highlight");
  });
});
