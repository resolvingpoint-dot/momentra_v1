import type { Metadata } from "next";
import LegalDocumentPage from "@/components/marketing/LegalDocumentPage";
import { privacyPolicy } from "@/lib/marketing/legal";
import { pageCopy } from "@/lib/marketing/copy";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: pageCopy.privacy.description,
};

export default function PrivacyPage() {
  return <LegalDocumentPage document={privacyPolicy} />;
}
