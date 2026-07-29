import type { Metadata } from "next";
import WorldMarketingPage from "@/components/marketing/WorldMarketingPage";
import { pageCopy } from "@/lib/marketing/copy";

export const metadata: Metadata = {
  title: "Group Moments",
  description: pageCopy.group.description,
};

export default function GroupPage() {
  return <WorldMarketingPage worldId="group" />;
}
