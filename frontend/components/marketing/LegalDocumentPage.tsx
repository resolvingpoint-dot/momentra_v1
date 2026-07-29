import Link from "next/link";
import { MarketingPageShell, ContentBlock } from "@/components/marketing/MarketingPageShell";
import type { LegalDocument } from "@/lib/marketing/legal";
import { LEGAL_CONTACT_EMAIL } from "@/lib/marketing/legal";

const legalNav = [
  { label: "Privacy Policy", href: "/privacy" },
  { label: "Terms of Use", href: "/terms" },
  { label: "Data Policy", href: "/data-policy" },
  { label: "Cookies Policy", href: "/cookies" },
] as const;

export default function LegalDocumentPage({
  document,
}: {
  document: LegalDocument;
}) {
  return (
    <MarketingPageShell
      eyebrow="Legal"
      title={document.title}
      description={document.description}
    >
      <ContentBlock>
        <p className="text-sm text-white/50">
          Last updated: {document.lastUpdated}
        </p>

        <nav
          aria-label="Legal documents"
          className="flex flex-wrap gap-2 border-b border-white/10 pb-6"
        >
          {legalNav.map((item) => {
            const active = item.href === `/${document.slug}`;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors sm:text-sm ${
                  active
                    ? "border-ember-500/40 bg-ember-500/15 text-ember-200"
                    : "border-white/12 bg-white/[0.03] text-white/65 hover:border-white/25 hover:text-text-on-dark"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        {document.intro.map((p) => (
          <p key={p.slice(0, 48)}>{p}</p>
        ))}
      </ContentBlock>

      {document.sections.map((section) => (
        <ContentBlock key={section.id} title={section.title}>
          {section.paragraphs.map((p) => (
            <p key={p.slice(0, 64)}>{p}</p>
          ))}
          {section.bullets?.length ? (
            <ul className="list-disc space-y-2 pl-5 text-white/75">
              {section.bullets.map((b) => (
                <li key={b.slice(0, 64)}>{b}</li>
              ))}
            </ul>
          ) : null}
        </ContentBlock>
      ))}

      <ContentBlock title="Contact">
        <p>{document.contactNote}</p>
        <p>
          Email{" "}
          <a
            href={`mailto:${LEGAL_CONTACT_EMAIL}`}
            className="text-ember-300 underline-offset-2 hover:underline"
          >
            {LEGAL_CONTACT_EMAIL}
          </a>
          .
        </p>
      </ContentBlock>
    </MarketingPageShell>
  );
}
