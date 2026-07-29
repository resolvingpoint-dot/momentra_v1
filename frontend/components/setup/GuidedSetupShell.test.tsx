/** @vitest-environment jsdom */
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { GuidedSetupShell } from "@/components/setup/GuidedSetupShell";

vi.mock("@/components/theme/AppContextProvider", () => ({
  useThemeTokens: () => ({
    colors: {
      background: "#fff",
      textPrimary: "#111",
      textSecondary: "#666",
      border: "#ddd",
      surfaceContainer: "#f5f5f5",
      primary: "#0a7",
      primaryContainer: "#0a7",
      brandOnPrimary: "#fff",
      error: "#c00",
    },
  }),
}));

const steps = [
  { id: "basics", title: "Team basics", shortTitle: "Basics", description: "Step one" },
  { id: "config", title: "Configuration", shortTitle: "Config", description: "Step two" },
  { id: "people", title: "People", shortTitle: "People", description: "Step three" },
  { id: "review", title: "Review", shortTitle: "Review", description: "Step four" },
];

describe("GuidedSetupShell", () => {
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    container.remove();
  });

  it("renders step nav, summary rows, and save indicator", () => {
    act(() => {
      root.render(
        <GuidedSetupShell
          title="Team Operations Setup"
          currentStep={1}
          steps={steps}
          saveState="saved"
          liveSummary={[
            { label: "Type", value: "Team Operations" },
            { label: "Currency", value: "INR" },
          ]}
          canContinue
          onContinue={() => undefined}
          onClose={() => undefined}
        >
          <p>Content</p>
        </GuidedSetupShell>,
      );
    });

    expect(container.querySelector("[data-guided-setup-shell]")).toBeTruthy();
    expect(container.textContent).toContain("Basics");
    expect(container.textContent).toContain("Team Operations");
    expect(container.textContent).toContain("INR");
    expect(container.textContent).toContain("Saved");
    expect(container.textContent).toContain("Continue");
  });

  it("singleScroll hides step nav and shows Activate", () => {
    act(() => {
      root.render(
        <GuidedSetupShell
          layout="singleScroll"
          contextType="personal"
          title="Future Building Setup"
          currentStep={1}
          steps={[{ id: "setup", title: "Setup", shortTitle: "Setup", description: "" }]}
          saveState="saved"
          canPreview
          canActivate
          footerPrimaryLabel="Begin Building My Future"
          onPreview={() => undefined}
          onActivate={() => undefined}
          onClose={() => undefined}
        >
          <p>All fields</p>
        </GuidedSetupShell>,
      );
    });

    expect(container.textContent).toContain("Future Building Setup");
    expect(container.textContent).not.toContain("Step 1 of");
    expect(container.textContent).not.toContain("Basics");
    expect(container.textContent).toContain("Begin Building My Future");
    expect(container.textContent).toContain("Preview");
  });

  it("shows Activate on review and Preview only when canPreview", () => {
    const onPreview = vi.fn();
    const onActivate = vi.fn();
    act(() => {
      root.render(
        <GuidedSetupShell
          title="Review"
          currentStep={4}
          steps={steps}
          saveState="idle"
          canPreview
          canActivate
          footerPrimaryLabel="Activate Team Operations"
          onPreview={onPreview}
          onActivate={onActivate}
          onClose={() => undefined}
        >
          <p>Review body</p>
        </GuidedSetupShell>,
      );
    });

    expect(container.textContent).toContain("Activate Team Operations");
    expect(container.textContent).toContain("Preview");
    const buttons = Array.from(container.querySelectorAll("button"));
    const previewBtn = buttons.find((b) => b.textContent === "Preview");
    const activateBtn = buttons.find((b) => b.textContent?.includes("Activate"));
    expect(previewBtn).toBeTruthy();
    expect(activateBtn).toBeTruthy();
    act(() => {
      previewBtn?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    expect(onPreview).toHaveBeenCalledTimes(1);
  });

  it("offers Retry when saveState is error", () => {
    const onRetrySave = vi.fn();
    act(() => {
      root.render(
        <GuidedSetupShell
          title="Setup"
          currentStep={2}
          steps={steps}
          saveState="error"
          onRetrySave={onRetrySave}
          onClose={() => undefined}
        >
          <p>Body</p>
        </GuidedSetupShell>,
      );
    });
    expect(container.textContent).toContain("Couldn't save");
    const retry = Array.from(container.querySelectorAll("button")).find((b) =>
      b.textContent?.includes("Retry"),
    );
    act(() => {
      retry?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    expect(onRetrySave).toHaveBeenCalledTimes(1);
  });

  it("announces current step for accessibility", () => {
    act(() => {
      root.render(
        <GuidedSetupShell
          title="Setup"
          currentStep={2}
          steps={steps}
          onClose={() => undefined}
        >
          <p>Body</p>
        </GuidedSetupShell>,
      );
    });
    expect(container.textContent).toContain("Step 2 of 4");
    const current = container.querySelector('[aria-current="step"]');
    expect(current?.textContent).toContain("Config");
  });
});
