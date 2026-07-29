import type { Metadata } from "next";
import { MarketingPageShell, ContentBlock } from "@/components/marketing/MarketingPageShell";
import { pageCopy } from "@/lib/marketing/copy";

export const metadata: Metadata = {
  title: "Contact",
  description: pageCopy.contact.description,
};

export default function ContactPage() {
  return (
    <MarketingPageShell
      eyebrow="Company"
      title="Contact"
      description="We would love to hear from you—whether you are exploring Momentra, the book, or partnerships."
    >
      <ContentBlock>
        <p>
          Email us at{" "}
          <a
            href="mailto:hello@momentra.app"
            className="text-ember-300 underline-offset-2 hover:underline"
          >
            hello@momentra.app
          </a>
          .
        </p>
        <p className="text-sm text-white/45">
          Careers and press inquiries can use the same address with the subject
          line Careers or Press.
        </p>
      </ContentBlock>
    </MarketingPageShell>
  );
}
