import { describe, expect, it } from "vitest";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const setupRoot = join(process.cwd(), "components/group/setup");

function collectTsFiles(dir: string, out: string[] = []): string[] {
  if (!existsSync(dir)) return out;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === "legacy" || entry.name === "node_modules") continue;
      collectTsFiles(full, out);
    } else if (/\.(ts|tsx)$/.test(entry.name) && !entry.name.endsWith(".test.ts")) {
      out.push(full);
    }
  }
  return out;
}

describe("Phase 2D Group guided setup cleanup", () => {
  it("quarantines GroupMomentSetup under legacy/", () => {
    expect(existsSync(join(setupRoot, "GroupMomentSetup.tsx"))).toBe(false);
    expect(existsSync(join(setupRoot, "legacy/GroupMomentSetup.tsx"))).toBe(true);
    expect(existsSync(join(setupRoot, "legacy/README.md"))).toBe(true);
  });

  it("quarantines legacy wizards and GroupSetupShell", () => {
    expect(existsSync(join(setupRoot, "legacy/experience/ExperienceSetup.tsx"))).toBe(true);
    expect(existsSync(join(setupRoot, "legacy/purchase/PurchaseSetup.tsx"))).toBe(true);
    expect(existsSync(join(setupRoot, "legacy/living/LivingSetup.tsx"))).toBe(true);
    expect(existsSync(join(setupRoot, "legacy/shared/GroupSetupShell.tsx"))).toBe(true);
    expect(existsSync(join(setupRoot, "shared/GroupSetupShell.tsx"))).toBe(false);
  });

  it("production setup modules do not import GroupMomentSetup or legacy wizards", () => {
    const files = collectTsFiles(setupRoot);
    files.push(join(process.cwd(), "components/home/GroupHomePlaceholder.tsx"));
    for (const file of files) {
      const src = readFileSync(file, "utf8");
      expect(src, file).not.toMatch(/GroupMomentSetup/);
      expect(src, file).not.toMatch(/setup\/legacy\//);
      expect(src, file).not.toMatch(/\bExperienceSetup\b/);
      expect(src, file).not.toMatch(/\bPurchaseSetup\b/);
      expect(src, file).not.toMatch(/\bLivingSetup\b/);
      expect(src, file).not.toMatch(/GroupSetupShell/);
    }
  });

  it("Group home routes only dedicated adapters", () => {
    const home = readFileSync(
      join(process.cwd(), "components/home/GroupHomePlaceholder.tsx"),
      "utf8",
    );
    expect(home).toContain('from "@/components/group/setup/GroupTripSetup"');
    expect(home).toContain('from "@/components/group/setup/GroupPurchaseSetup"');
    expect(home).toContain('from "@/components/group/setup/GroupLivingSetup"');
    expect(home).not.toMatch(/GroupMomentSetup/);
    expect(home).not.toMatch(/setup\/legacy/);
  });

  it("all three adapters reuse GroupSetupInviteSection", () => {
    for (const rel of [
      "experience/SharedExperienceSetup.tsx",
      "purchase/SharedPurchaseSetup.tsx",
      "living/SharedLivingSetup.tsx",
    ]) {
      const src = readFileSync(join(setupRoot, rel), "utf8");
      expect(src).toContain("GroupSetupInviteSection");
      expect(src).toContain('contextType="group"');
      expect(src).not.toMatch(/@\/lib\/business|@\/components\/business/);
    }
  });

  it("legacy GroupMomentSetup no longer exports production aliases", () => {
    const src = readFileSync(join(setupRoot, "legacy/GroupMomentSetup.tsx"), "utf8");
    expect(src).toContain("export function GroupMomentSetup");
    expect(src).not.toContain("export function GroupTripSetup");
    expect(src).not.toContain("export function GroupPurchaseSetup");
    expect(src).not.toContain("export function GroupLivingSetup");
  });
});
