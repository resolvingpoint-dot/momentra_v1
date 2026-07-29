import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";

describe("Shared Living routing cutover", () => {
  it("GroupLivingSetup module exports SharedLivingSetup", () => {
    const src = readFileSync(
      join(process.cwd(), "components/group/setup/GroupLivingSetup.tsx"),
      "utf8",
    );
    expect(src).toContain('from "./living/SharedLivingSetup"');
    expect(src).toContain("SharedLivingSetup as GroupLivingSetup");
  });

  it("Group home imports all three dedicated setup modules", () => {
    const src = readFileSync(
      join(process.cwd(), "components/home/GroupHomePlaceholder.tsx"),
      "utf8",
    );
    expect(src).toContain('from "@/components/group/setup/GroupLivingSetup"');
    expect(src).toContain('from "@/components/group/setup/GroupPurchaseSetup"');
    expect(src).toContain('from "@/components/group/setup/GroupTripSetup"');
    expect(src).not.toMatch(
      /from ["']@\/components\/group\/setup\/GroupMomentSetup["']/,
    );
    expect(src).not.toMatch(/setup\/legacy/);
    expect(src).toMatch(/SHARED_LIVING[\s\S]*GroupLivingSetup/);
    expect(src).toMatch(/SHARED_PURCHASE[\s\S]*GroupPurchaseSetup/);
  });

  it("GroupMomentSetup lives only under legacy and has no production aliases", () => {
    const src = readFileSync(
      join(process.cwd(), "components/group/setup/legacy/GroupMomentSetup.tsx"),
      "utf8",
    );
    expect(src).toContain("export function GroupMomentSetup");
    expect(src).toContain("quarantined");
    expect(src).not.toContain("export function GroupLivingSetup");
    expect(src).not.toContain("export function GroupPurchaseSetup");
  });

  it("SharedLivingSetup uses group context, invite reuse, and no Business imports", () => {
    const src = readFileSync(
      join(process.cwd(), "components/group/setup/living/SharedLivingSetup.tsx"),
      "utf8",
    );
    expect(src).toContain('contextType="group"');
    expect(src).toContain('TEMPLATE_ID = "shared_living"');
    expect(src).toContain("GroupSetupInviteSection");
    expect(src).toContain("Invite housemates");
    expect(src).toContain("GuidedSetupShell");
    expect(src).not.toMatch(/@\/lib\/business|@\/components\/business/);
  });

  it("production routing no longer selects GroupMomentSetup for living", () => {
    const home = readFileSync(
      join(process.cwd(), "components/home/GroupHomePlaceholder.tsx"),
      "utf8",
    );
    const livingModule = readFileSync(
      join(process.cwd(), "components/group/setup/GroupLivingSetup.tsx"),
      "utf8",
    );
    expect(livingModule).not.toContain("GroupMomentSetup");
    expect(home).toContain("GroupLivingSetup");
    expect(home).not.toContain("GroupMomentSetup");
  });
});
