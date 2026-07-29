import type { Metadata } from "next";
import HowMomentsWorkClient from "./HowMomentsWorkClient";
import { pageCopy } from "@/lib/marketing/copy";

export const metadata: Metadata = {
  title: "How Moments Work",
  description: pageCopy.howMomentsWork.description,
};

export default function HowMomentsWorkPage() {
  return <HowMomentsWorkClient />;
}
