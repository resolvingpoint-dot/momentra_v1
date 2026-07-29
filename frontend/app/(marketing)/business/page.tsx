import type { Metadata } from "next";
import WorldMarketingPage from "@/components/marketing/WorldMarketingPage";
import { pageCopy } from "@/lib/marketing/copy";

export const metadata: Metadata = {
  title: "Business Moments",
  description: pageCopy.business.description,
};

export default function BusinessPage() {
  return <WorldMarketingPage worldId="business" />;
}
