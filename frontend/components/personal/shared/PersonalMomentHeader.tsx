"use client";

import { ContextMomentHeader } from "@/components/shared/ContextMomentHeader";
import type { PersonalMomentSwitcherOption } from "@/components/personal/shared/personalMomentRouting";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";

type PersonalMomentHeaderProps = {
  tabLabel: string;
  options: PersonalMomentSwitcherOption[];
  selectedTypeCode: PersonalMomentTypeCode;
  onSelect: (option: PersonalMomentSwitcherOption) => void;
  onManageClick?: () => void;
  onDeleteMoment?: (option: PersonalMomentSwitcherOption) => void;
};

export function PersonalMomentHeader(props: PersonalMomentHeaderProps) {
  return (
    <ContextMomentHeader
      contextLabel="Personal"
      tabLabel={props.tabLabel}
      options={props.options}
      selectedTypeCode={props.selectedTypeCode}
      onSelect={(option) => props.onSelect(option as PersonalMomentSwitcherOption)}
      onManageClick={props.onManageClick}
      onDeleteMoment={
        props.onDeleteMoment
          ? (option) => props.onDeleteMoment!(option as PersonalMomentSwitcherOption)
          : undefined
      }
      accentVariant="personal"
    />
  );
}
