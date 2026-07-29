import type { Metadata } from "next";
import { MarketingDocumentTheme } from "@/components/marketing/MarketingDocumentTheme";
import Navbar from "@/components/marketing/Navbar";
import Footer from "@/components/marketing/sections/Footer";
import StickyMobileCTA from "@/components/marketing/StickyMobileCTA";
import { siteMeta } from "@/lib/marketing/copy";

export const metadata: Metadata = {
  title: siteMeta.title,
  description: siteMeta.description,
  keywords: siteMeta.keywords,
};

export default function MarketingLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <MarketingDocumentTheme>
      <Navbar />
      {children}
      <Footer />
      <StickyMobileCTA />
    </MarketingDocumentTheme>
  );
}
