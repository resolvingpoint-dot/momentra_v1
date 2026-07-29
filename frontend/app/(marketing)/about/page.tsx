import type { Metadata } from "next";
import { MarketingPageShell, ContentBlock } from "@/components/marketing/MarketingPageShell";
import { pageCopy, finalCta } from "@/lib/marketing/copy";

export const metadata: Metadata = {
  title: "About",
  description: pageCopy.about.description,
};

export default function AboutPage() {
  return (
    <MarketingPageShell
      eyebrow="Company"
      title="About Momentra"
      description="Momentra is not software placed on top of life. It is a platform designed around how life actually unfolds."
      primaryCta={finalCta.primaryCta}
    >
      <ContentBlock>
        <p>
          Life happens in moments—birthdays, journeys, homes, goals,
          responsibilities, teams, communities, and new beginnings. Money moves
          through these moments. Momentra begins with the moment itself.
        </p>
        <p>
          The same living architecture—Pulse, Moments, Create, Life, and
          Memory—serves personal life, shared life, and business life.
        </p>
        <p>
          Inspired by the book <em>Life Happens in Moments</em>, Momentra is
          where that philosophy becomes something you can use.
        </p>
      </ContentBlock>
    </MarketingPageShell>
  );
}
