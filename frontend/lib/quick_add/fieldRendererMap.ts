import type { QuickAddFieldType } from "./types";

/** Maps registry field types to existing UI component keys per platform. */
export const FIELD_RENDERER_MAP = {
  web: {
    amount: "LifeOpsHeroAmountField",
    text: "LifeOpsQuickAddTextField",
    textarea: "LifeOpsQuickAddTextField",
    single_select: "LifeOpsWrapChipGrid",
    multi_select: "LifeOpsWrapChipGrid",
    segmented: "LifeOpsSegmentedControl",
    chip_grid: "LifeOpsWrapChipGrid",
    icon_grid: "LifeOpsMoodIconGrid",
    date: "LifeOpsQuickAddTextField",
    toggle: "LifeOpsToggleField",
    account_picker: "LifeOpsAccountPickerRow",
    member_picker: "LifeOpsMemberPickerField",
    media_upload: "LifeOpsMediaUploadField",
    runtime_signals: "LifeOpsRuntimeSignalCards",
  },
  android: {
    amount: "LifeOpsHeroAmountField",
    text: "LifeOpsQuickAddTextField",
    textarea: "LifeOpsQuickAddTextField",
    single_select: "LifeOpsWrapChipGrid",
    multi_select: "LifeOpsWrapChipGrid",
    segmented: "LifeOpsSegmentedControl",
    chip_grid: "LifeOpsWrapChipGrid",
    icon_grid: "LifeOpsMoodIconGrid",
    date: "LifeOpsQuickAddTextField",
    toggle: "LifeOpsToggleField",
    account_picker: "LifeOpsAccountPickerRow",
    member_picker: "LifeOpsMemberPickerField",
    media_upload: "LifeOpsMediaUploadField",
    runtime_signals: "LifeOpsRuntimeSignalCards",
  },
  ios: {
    amount: "LifeOpsHeroAmountField",
    text: "LifeOpsQuickAddTextField",
    textarea: "LifeOpsQuickAddTextField",
    single_select: "LifeOpsWrapChipGrid",
    multi_select: "LifeOpsWrapChipGrid",
    segmented: "LifeOpsSegmentedControl",
    chip_grid: "LifeOpsWrapChipGrid",
    icon_grid: "LifeOpsMoodIconGrid",
    date: "LifeOpsQuickAddTextField",
    toggle: "LifeOpsToggleField",
    account_picker: "LifeOpsAccountPickerRow",
    member_picker: "LifeOpsMemberPickerField",
    media_upload: "LifeOpsMediaUploadField",
    runtime_signals: "LifeOpsRuntimeSignalCards",
  },
} as const satisfies Record<
  "web" | "android" | "ios",
  Record<QuickAddFieldType, string>
>;

export type QuickAddPlatform = keyof typeof FIELD_RENDERER_MAP;

export function getFieldRendererComponent(
  platform: QuickAddPlatform,
  fieldType: QuickAddFieldType,
): string {
  return FIELD_RENDERER_MAP[platform][fieldType];
}
