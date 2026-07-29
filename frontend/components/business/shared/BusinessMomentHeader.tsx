"use client";

import { ContextMomentHeader } from "@/components/shared/ContextMomentHeader";
import type { BusinessMomentSwitcherOption } from "@/components/business/shared/businessMomentRouting";

type BusinessMomentHeaderProps = {
  tabLabel: string;
  options: BusinessMomentSwitcherOption[];
  selectedTypeCode: string;
  onSelect: (option: BusinessMomentSwitcherOption) => void;
  onManageClick?: () => void;
  onInviteMoment?: (option: BusinessMomentSwitcherOption) => void;
  onDeleteMoment?: (option: BusinessMomentSwitcherOption) => void;
};

export function BusinessMomentHeader(props: BusinessMomentHeaderProps) {
  return (
    <ContextMomentHeader
      contextLabel="Business"
      tabLabel={props.tabLabel}
      options={props.options}
      selectedTypeCode={props.selectedTypeCode}
      onSelect={props.onSelect}
      onManageClick={props.onManageClick}
      onInviteMoment={props.onInviteMoment}
      onDeleteMoment={props.onDeleteMoment}
      accentVariant="business"
    />
  );
}
