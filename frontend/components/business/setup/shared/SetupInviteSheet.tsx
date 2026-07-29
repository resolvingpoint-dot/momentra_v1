"use client";

/** @deprecated Prefer @/components/setup/shared + catalog methods prop. */
import {
  SetupInviteButton as SharedInviteButton,
  SetupInviteSheet as SharedInviteSheet,
} from "@/components/setup/shared/SetupInviteSheet";
import { setupChoices } from "@/lib/business/setupCatalog";
import type { SetupChoice } from "@/components/setup/shared/setupControlTypes";

type SheetProps = {
  open: boolean;
  onClose: () => void;
  memberName?: string;
  currentMethod?: string;
  methods?: SetupChoice[];
  onSelect: (method: string) => void;
  momentId?: string;
  localId?: string;
  memberEmail?: string | null;
  memberPhone?: string | null;
  onBeforeInvite?: () => Promise<boolean>;
  onEmailRequired?: () => void;
};

export function SetupInviteSheet({ methods, ...rest }: SheetProps) {
  return (
    <SharedInviteSheet
      {...rest}
      methods={methods ?? setupChoices("invite_methods")}
    />
  );
}

type ButtonProps = {
  memberName?: string;
  method?: string;
  methods?: SetupChoice[];
  onSelect: (method: string) => void;
  momentId?: string;
  localId?: string;
  memberEmail?: string | null;
  memberPhone?: string | null;
  onBeforeInvite?: () => Promise<boolean>;
  onEmailRequired?: () => void;
};

export function SetupInviteButton({ methods, ...rest }: ButtonProps) {
  return (
    <SharedInviteButton
      {...rest}
      methods={methods ?? setupChoices("invite_methods")}
    />
  );
}
