import { describe, expect, it } from "vitest";
import {
  isActiveBusinessMomentStatus,
  resolveBusinessMomentManageContext,
  resolveBusinessMomentSwitcherOptions,
  resolveSelectedBusinessMoment,
} from "@/components/business/shared/businessMomentRouting";
import type {
  BusinessCreateOptionCard,
  BusinessMomentResponse,
  BusinessMomentTypeCard,
} from "@/lib/api/business";

function homeCard(
  overrides: Partial<BusinessMomentTypeCard> & Pick<BusinessMomentTypeCard, "moment_type_code">,
): BusinessMomentTypeCard {
  return {
    moment_type_id: overrides.moment_type_id ?? overrides.moment_type_code,
    moment_type_code: overrides.moment_type_code,
    moment_type_name: overrides.moment_type_name ?? overrides.moment_type_code,
    display_order: overrides.display_order ?? 1,
    linked_moment_id: overrides.linked_moment_id ?? null,
    linked_moment_status: overrides.linked_moment_status ?? null,
    is_active: overrides.is_active,
    action_label: overrides.action_label ?? "Open",
  };
}

function createCard(
  overrides: Partial<BusinessCreateOptionCard> & Pick<BusinessCreateOptionCard, "moment_type_code">,
): BusinessCreateOptionCard {
  return {
    moment_type_id: overrides.moment_type_id ?? overrides.moment_type_code,
    moment_type_code: overrides.moment_type_code,
    moment_type_name: overrides.moment_type_name ?? overrides.moment_type_code,
    display_order: overrides.display_order ?? 1,
    linked_moment_id: overrides.linked_moment_id ?? null,
    linked_moment_status: overrides.linked_moment_status ?? null,
    is_active: overrides.is_active,
  };
}

function moment(
  overrides: Partial<BusinessMomentResponse> &
    Pick<BusinessMomentResponse, "moment_id" | "moment_type_code" | "status">,
): BusinessMomentResponse {
  return {
    moment_id: overrides.moment_id,
    moment_type_id: overrides.moment_type_id ?? overrides.moment_type_code ?? "t",
    moment_type_code: overrides.moment_type_code,
    moment_name: overrides.moment_name ?? overrides.moment_type_code ?? "m",
    status: overrides.status,
  };
}

describe("resolveBusinessMomentSwitcherOptions", () => {
  it("prefers bootstrap.moments inventory (Group parity) for three ACTIVE types", () => {
    const options = resolveBusinessMomentSwitcherOptions(
      [],
      [],
      [
        moment({
          moment_id: "m-team",
          moment_type_code: "TEAM_OPERATIONS",
          status: "ACTIVE",
          moment_name: "Team Ops",
        }),
        moment({
          moment_id: "m-runway",
          moment_type_code: "BUSINESS_RUNWAY",
          status: "ACTIVE",
          moment_name: "Runway",
        }),
        moment({
          moment_id: "m-ops",
          moment_type_code: "BUSINESS_OPERATIONS",
          status: "ACTIVE",
          moment_name: "Ops",
        }),
        moment({
          moment_id: "m-draft",
          moment_type_code: "TEAM_OPERATIONS",
          status: "DRAFT",
          moment_name: "Draft",
        }),
      ],
    );
    expect(options.map((o) => o.typeCode)).toEqual([
      "TEAM_OPERATIONS",
      "BUSINESS_RUNWAY",
      "BUSINESS_OPERATIONS",
    ]);
    expect(options.find((o) => o.typeCode === "TEAM_OPERATIONS")?.momentId).toBe("m-team");
  });

  it("falls back to home/create cards when moments empty", () => {
    const options = resolveBusinessMomentSwitcherOptions(
      [
        homeCard({
          moment_type_code: "TEAM_OPERATIONS",
          linked_moment_id: "m-team",
          linked_moment_status: "ACTIVE",
          is_active: true,
          display_order: 1,
        }),
      ],
      [
        createCard({
          moment_type_code: "BUSINESS_RUNWAY",
          linked_moment_id: "m-runway",
          linked_moment_status: "ACTIVE",
          is_active: true,
          display_order: 2,
        }),
      ],
      [],
    );
    expect(options.map((o) => o.typeCode)).toEqual(["TEAM_OPERATIONS", "BUSINESS_RUNWAY"]);
  });

  it("excludes DRAFT from card fallback", () => {
    const options = resolveBusinessMomentSwitcherOptions(
      [
        homeCard({
          moment_type_code: "TEAM_OPERATIONS",
          linked_moment_id: "m-draft",
          linked_moment_status: "DRAFT",
          is_active: false,
        }),
        homeCard({
          moment_type_code: "BUSINESS_RUNWAY",
          linked_moment_id: "m-active",
          linked_moment_status: "ACTIVE",
          is_active: true,
        }),
      ],
      [],
      [],
    );
    expect(options.map((o) => o.typeCode)).toEqual(["BUSINESS_RUNWAY"]);
  });

  it("isActiveBusinessMomentStatus matches Personal ACTIVE-family", () => {
    expect(isActiveBusinessMomentStatus("ACTIVE")).toBe(true);
    expect(isActiveBusinessMomentStatus("paused")).toBe(true);
    expect(isActiveBusinessMomentStatus("COMPLETED")).toBe(true);
    expect(isActiveBusinessMomentStatus("DRAFT")).toBe(false);
  });
});

describe("resolveSelectedBusinessMoment", () => {
  it("binds type and momentId from switcher option", () => {
    const options = resolveBusinessMomentSwitcherOptions(
      [],
      [],
      [
        moment({
          moment_id: "m1",
          moment_type_code: "BUSINESS_RUNWAY",
          status: "ACTIVE",
        }),
      ],
    );
    expect(resolveSelectedBusinessMoment(options, "", null)).toEqual({
      typeCode: "BUSINESS_RUNWAY",
      momentId: "m1",
    });
  });
});

describe("resolveBusinessMomentManageContext", () => {
  it("prefers ACTIVE inventory moment over create DRAFT", () => {
    const ctx = resolveBusinessMomentManageContext(
      "TEAM_OPERATIONS",
      [
        createCard({
          moment_type_code: "TEAM_OPERATIONS",
          linked_moment_id: "m-draft",
          linked_moment_status: "DRAFT",
        }),
      ],
      [],
      [
        moment({
          moment_id: "m-active",
          moment_type_code: "TEAM_OPERATIONS",
          status: "ACTIVE",
        }),
      ],
    );
    expect(ctx?.momentId).toBe("m-active");
    expect(ctx?.status).toBe("ACTIVE");
  });
});
