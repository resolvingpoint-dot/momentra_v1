import type { Metadata } from "next";
import LegalDocumentPage from "@/components/marketing/LegalDocumentPage";
import { dataPolicy } from "@/lib/marketing/legal";
import { pageCopy } from "@/lib/marketing/copy";

export const metadata: Metadata = {
  title: "Data Policy",
  description: pageCopy.dataPolicy.description,
};

export default function DataPolicyPage() {
  return <LegalDocumentPage document={dataPolicy} />;
}
