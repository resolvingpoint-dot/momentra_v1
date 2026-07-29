"use client";

import { ChevronDown, Plus, ScanLine } from "lucide-react";
import { Life360Mark } from "@/components/life360/Life360Mark";
import { UserAvatar } from "@/components/profile/UserAvatar";
import { brandTokens } from "@/lib/brandTokens";
import type { UserResponse } from "@/lib/api/types";

type MomentraTopBarProps = {
  user?: UserResponse | null;
  onSettingsClick?: () => void;
  onNewMomentClick?: () => void;
  onLife360Click?: () => void;
  /** Show QR join scanner (Group / Business). */
  showScanInviteButton?: boolean;
  onScanInviteClick?: () => void;
  /** Business company workspace chrome */
  businessMode?: boolean;
  companyName?: string | null;
  onCompanySwitcherClick?: () => void;
};

export function MomentraTopBar({
  user,
  onSettingsClick,
  onNewMomentClick,
  onLife360Click,
  showScanInviteButton = false,
  onScanInviteClick,
  businessMode = false,
  companyName = null,
  onCompanySwitcherClick,
}: MomentraTopBarProps) {
  return (
    <header
      className="flex h-14 shrink-0 items-center gap-2 px-4"
      style={{ backgroundColor: brandTokens.brand }}
    >
      <img
        src="/momentra_logo_dark.svg"
        alt="Momentra"
        className="h-8 w-auto max-w-[140px] shrink-0"
        style={businessMode ? { maxWidth: 110 } : undefined}
      />

      {businessMode ? (
        <button
          type="button"
          onClick={onCompanySwitcherClick}
          className="flex min-w-0 max-w-[min(160px,36vw)] shrink items-center gap-1 rounded-lg px-2 py-1 text-white hover:bg-white/10"
          aria-label="Switch company"
        >
          <span className="truncate text-[15px] font-semibold">
            {companyName || "Select company"}
          </span>
          <ChevronDown className="h-4 w-4 shrink-0 opacity-90" strokeWidth={2.5} />
        </button>
      ) : null}

      <div className="flex-1" />
      <button
        type="button"
        onClick={onLife360Click}
        aria-label="Life 360"
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-white/90 hover:bg-white/10"
      >
        <Life360Mark size={24} />
      </button>
      {showScanInviteButton ? (
        <button
          type="button"
          onClick={onScanInviteClick}
          aria-label="Scan invite QR"
          className="flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-full text-white shadow-md"
          style={{ backgroundColor: `${brandTokens.cta}CC` }}
        >
          <ScanLine className="h-4 w-4" strokeWidth={2.5} />
        </button>
      ) : null}
      <button
        type="button"
        onClick={onNewMomentClick}
        aria-label="New moment"
        className="flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-full text-white shadow-md"
        style={{ backgroundColor: brandTokens.cta }}
      >
        <Plus className="h-4 w-4" strokeWidth={2.5} />
      </button>
      <div className="shrink-0">
        <UserAvatar
          photoUrl={user?.photo_url}
          displayName={user?.display_name}
          email={user?.email}
          size={40}
          onClick={onSettingsClick}
        />
      </div>
    </header>
  );
}
