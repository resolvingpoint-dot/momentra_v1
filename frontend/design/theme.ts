import { tokensFor } from "@/design/tokens";
import type { AppContext } from "@/lib/appContext";

export function themeForContext(context: AppContext) {
  return tokensFor(context);
}
