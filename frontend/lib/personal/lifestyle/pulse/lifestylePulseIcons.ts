import { Box, Brush, Compass, Heart, MapPin, Palette, Sparkles, Utensils, type LucideIcon } from "lucide-react";

export const LIFESTYLE_SEGMENT_COLORS = ["#6C4EF2", "#B7EAFF", "#CABEFF", "#483695", "#4cd6ff"];

export function resolveLifestyleActivityIcon(eventType: string, icon?: string | null): LucideIcon {
  const key = (icon ?? eventType).toUpperCase();
  const map: Record<string, LucideIcon> = {
    CREATIVE: Palette,
    EXPERIENCE: MapPin,
    DISCOVERY: Compass,
    WELLBEING: Heart,
    LIFESTYLE_ADJUST: Sparkles,
    RESTAURANT: Utensils,
    BRUSH: Brush,
  };
  return map[key] ?? Sparkles;
}

export function lifestyleQuickAddIcon(index: number): LucideIcon {
  return [Box, Heart, Compass, Palette, Sparkles][index] ?? Sparkles;
}

export const LIFESTYLE_GAUGE_COLORS: Record<string, string> = {
  fulfill: "#6c4ef2",
  vitality: "#4cd6ff",
  explore: "#6c4ef2",
  create: "#6c4ef2",
};
