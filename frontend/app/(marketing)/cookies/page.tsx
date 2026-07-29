import type { Metadata } from "next";
import LegalDocumentPage from "@/components/marketing/LegalDocumentPage";
import { cookiesPolicy } from "@/lib/marketing/legal";
import { pageCopy } from "@/lib/marketing/copy";

export const metadata: Metadata = {
  title: "Cookies Policy",
  description: pageCopy.cookies.description,
};

export default function CookiesPage() {
  return <LegalDocumentPage document={cookiesPolicy} />;
}
