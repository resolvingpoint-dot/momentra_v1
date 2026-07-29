import { describe, expect, it } from "vitest";
import {
  extractCompanyInviteToken,
  extractInviteToken,
  parseInviteInput,
} from "@/lib/invite/inviteToken";

describe("extractInviteToken", () => {
  it("parses momentra://invite/{token}", () => {
    expect(extractInviteToken("momentra://invite/abc.def.ghi")).toBe("abc.def.ghi");
  });

  it("parses https://momentra.tech/invite/{token}", () => {
    expect(extractInviteToken("https://momentra.tech/invite/abc.def.ghi")).toBe(
      "abc.def.ghi",
    );
  });

  it("parses apex https://momentra.tech/{token}", () => {
    expect(extractInviteToken("https://momentra.tech/abc.def.ghi")).toBe("abc.def.ghi");
  });

  it("parses www host", () => {
    expect(extractInviteToken("https://www.momentra.tech/invite/tok12345")).toBe(
      "tok12345",
    );
  });

  it("returns raw token when not a URL", () => {
    expect(extractInviteToken("rawtoken12")).toBe("rawtoken12");
  });
});

describe("company invite tokens", () => {
  it("parses https company-invite path", () => {
    expect(
      parseInviteInput("https://momentra.tech/company-invite/wsTok123456"),
    ).toEqual({ token: "wsTok123456", kind: "company" });
  });

  it("parses momentra://company-invite/{token}", () => {
    expect(parseInviteInput("momentra://company-invite/wsTok123456")).toEqual({
      token: "wsTok123456",
      kind: "company",
    });
  });

  it("extractCompanyInviteToken accepts raw tokens", () => {
    expect(extractCompanyInviteToken("rawCompanyTok")).toBe("rawCompanyTok");
  });

  it("extractCompanyInviteToken accepts full company links", () => {
    expect(
      extractCompanyInviteToken("https://www.momentra.tech/company-invite/abcXYZ123"),
    ).toBe("abcXYZ123");
  });
});
