import type { Metadata } from "next";
import WorldMarketingPage from "@/components/marketing/WorldMarketingPage";
import { pageCopy } from "@/lib/marketing/copy";

export const metadata: Metadata = {
  title: "Personal Moments",
  description: pageCopy.personal.description,
};

export default function PersonalPage() {
  return <WorldMarketingPage worldId="personal" />;
}
