import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";

describe("Shared Purchase routing cutover", () => {
  it("GroupPurchaseSetup module exports SharedPurchaseSetup", () => {
    const src = readFileSync(
      join(process.cwd(), "components/group/setup/GroupPurchaseSetup.tsx"),
      "utf8",
    );
    expect(src).toContain('from "./purchase/SharedPurchaseSetup"');
    expect(src).toContain("SharedPurchaseSetup as GroupPurchaseSetup");
  });

  it("Group home imports purchase setup from dedicated module", () => {
    const src = readFileSync(
      join(process.cwd(), "components/home/GroupHomePlaceholder.tsx"),
      "utf8",
    );
    expect(src).toContain('from "@/components/group/setup/GroupPurchaseSetup"');
    expect(src).toContain('from "@/components/group/setup/GroupTripSetup"');
    expect(src).toMatch(/SHARED_PURCHASE[\s\S]*GroupPurchaseSetup/);
    expect(src).not.toMatch(/GroupMomentSetup/);
  });

  it("GroupMomentSetup is quarantined under legacy/", () => {
    const src = readFileSync(
      join(process.cwd(), "components/group/setup/legacy/GroupMomentSetup.tsx"),
      "utf8",
    );
    expect(src).toContain("quarantined");
    expect(src).toContain("export function GroupMomentSetup");
    expect(src).not.toContain("export function GroupPurchaseSetup");
  });

  it("SharedPurchaseSetup uses group context and no Business imports", () => {
    const src = readFileSync(
      join(process.cwd(), "components/group/setup/purchase/SharedPurchaseSetup.tsx"),
      "utf8",
    );
    expect(src).toContain('contextType="group"');
    expect(src).toContain('TEMPLATE_ID = "shared_purchase"');
    expect(src).toContain("GroupSetupInviteSection");
    expect(src).not.toMatch(/@\/lib\/business|@\/components\/business/);
  });
});
