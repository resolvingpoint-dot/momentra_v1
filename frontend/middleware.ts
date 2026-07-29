import { type NextRequest } from "next/server";
import { updateSession } from "@/utils/supabase/middleware";

export async function middleware(request: NextRequest) {
  return updateSession(request);
}

export const config = {
  // Only refresh Supabase session for the product app. Marketing routes skip this.
  matcher: ["/app/:path*"],
};
