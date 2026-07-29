import type { Metadata } from "next";
import LegalDocumentPage from "@/components/marketing/LegalDocumentPage";
import { termsOfUse } from "@/lib/marketing/legal";
import { pageCopy } from "@/lib/marketing/copy";

export const metadata: Metadata = {
  title: "Terms of Use",
  description: pageCopy.terms.description,
};

export default function TermsPage() {
  return <LegalDocumentPage document={termsOfUse} />;
}
