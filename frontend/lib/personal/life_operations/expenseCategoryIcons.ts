import type { LucideIcon } from "lucide-react";
import {
  AlertTriangle,
  Briefcase,
  Bus,
  CalendarCheck,
  Car,
  CircleEllipsis,
  Coffee,
  CreditCard,
  Film,
  Fuel,
  Gift,
  Heart,
  Home,
  Landmark,
  MoreHorizontal,
  PiggyBank,
  Pill,
  Repeat,
  ShoppingBag,
  Sparkles,
  Stethoscope,
  CarTaxiFront,
  TrendingUp,
  Utensils,
  UtensilsCrossed,
  Wallet,
  Wrench,
  Zap,
} from "lucide-react";

/** Material icon name → Lucide (expense taxonomy + common money icons). */
const MATERIAL_MAP: Record<string, LucideIcon> = {
  restaurant: Utensils,
  restaurant_menu: UtensilsCrossed,
  local_grocery_store: ShoppingBag,
  local_cafe: Coffee,
  directions_car: Car,
  local_gas_station: Fuel,
  local_taxi: CarTaxiFront,
  directions_bus: Bus,
  home: Home,
  apartment: Home,
  bolt: Zap,
  handyman: Wrench,
  favorite: Heart,
  local_pharmacy: Pill,
  medical_services: Stethoscope,
  movie: Film,
  theaters: Film,
  subscriptions: Repeat,
  more_horiz: MoreHorizontal,
  payments: Landmark,
  work: Briefcase,
  trending_up: TrendingUp,
  card_giftcard: Gift,
  account_balance: Landmark,
  account_balance_wallet: Wallet,
  savings: PiggyBank,
  credit_card: CreditCard,
  edit: CircleEllipsis,
};

/** Category / subcategory code → Material name (fallback when payload has no icon). */
const CODE_TO_MATERIAL: Record<string, string> = {
  FOOD: "restaurant",
  TRANSPORT: "directions_car",
  HOUSING: "home",
  HEALTH: "favorite",
  ENTERTAINMENT: "movie",
  OTHER: "more_horiz",
  GROCERIES: "local_grocery_store",
  DINING_OUT: "restaurant_menu",
  COFFEE: "local_cafe",
  FUEL: "local_gas_station",
  RIDESHARE: "local_taxi",
  TRANSIT: "directions_bus",
  RESIDENTIAL_RENT: "apartment",
  UTILITIES: "bolt",
  MAINTENANCE: "handyman",
  PHARMACY: "local_pharmacy",
  CLINIC: "medical_services",
  MOVIES: "theaters",
  SUBSCRIPTIONS: "subscriptions",
};

const PARENT_COLORS: Record<string, string> = {
  FOOD: "#F5C542",
  TRANSPORT: "#5B8DEF",
  HOUSING: "#9B7EDE",
  HEALTH: "#E85D75",
  ENTERTAINMENT: "#FF8C42",
  OTHER: "#8E8E93",
  GROCERIES: "#F5C542",
  DINING_OUT: "#F5C542",
  COFFEE: "#F5C542",
  FUEL: "#5B8DEF",
  RIDESHARE: "#5B8DEF",
  TRANSIT: "#5B8DEF",
  RESIDENTIAL_RENT: "#9B7EDE",
  UTILITIES: "#9B7EDE",
  MAINTENANCE: "#9B7EDE",
  PHARMACY: "#E85D75",
  CLINIC: "#E85D75",
  MOVIES: "#FF8C42",
  SUBSCRIPTIONS: "#FF8C42",
};

export function resolveExpenseCategoryIcon(
  icon?: string | null,
  categoryCode?: string | null,
  subcategoryCode?: string | null,
): LucideIcon {
  const material =
    (icon && icon.trim()) ||
    CODE_TO_MATERIAL[(subcategoryCode || "").toUpperCase()] ||
    CODE_TO_MATERIAL[(categoryCode || "").toUpperCase()] ||
    "";
  const key = material.toLowerCase();
  if (key && MATERIAL_MAP[key]) return MATERIAL_MAP[key];
  return Sparkles;
}

export function resolveExpenseCategoryColor(
  color?: string | null,
  categoryCode?: string | null,
  subcategoryCode?: string | null,
): string | null {
  if (color && color.trim()) return color.trim();
  const code = (subcategoryCode || categoryCode || "").toUpperCase();
  return PARENT_COLORS[code] ?? null;
}

export function resolveImpactIcon(impactLabel?: string | null): LucideIcon {
  const key = (impactLabel || "").trim().toLowerCase();
  if (key === "essential" || key === "pressure source") return AlertTriangle;
  if (key === "planned") return CalendarCheck;
  if (key === "unexpected") return Zap;
  return CircleEllipsis;
}
