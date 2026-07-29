export type LegalSection = {
  id: string;
  title: string;
  paragraphs: string[];
  bullets?: string[];
};

export type LegalDocument = {
  slug: "privacy" | "terms" | "data-policy" | "cookies";
  title: string;
  description: string;
  lastUpdated: string;
  intro: string[];
  sections: LegalSection[];
  contactNote: string;
};

export const LEGAL_LAST_UPDATED = "22 July 2026";
export const LEGAL_CONTACT_EMAIL = "hello@momentra.app";
export const LEGAL_SERVICE_NAME = "Momentra";
export const LEGAL_SITE = "https://momentra.app";

export const privacyPolicy: LegalDocument = {
  slug: "privacy",
  title: "Privacy Policy",
  description:
    "How Momentra collects, uses, shares, and protects information when you use our website, app, and related services.",
  lastUpdated: LEGAL_LAST_UPDATED,
  intro: [
    "This Privacy Policy explains how Momentra (“Momentra,” “we,” “us,” or “our”) handles personal information when you visit our websites, use the Momentra application, read Life Happens in Moments, or otherwise interact with our services (collectively, the “Services”).",
    "Momentra is a moment-centric platform that helps people plan, coordinate, and remember personal, group, and business moments. Because moments can include people, plans, money, progress, and memory, we treat related information carefully.",
    "By using the Services, you acknowledge this Privacy Policy. If you do not agree, please do not use the Services.",
  ],
  sections: [
    {
      id: "who-we-are",
      title: "1. Who we are",
      paragraphs: [
        "Momentra provides software and related experiences for organizing life and work around moments rather than isolated transactions.",
        `For privacy questions, contact us at ${LEGAL_CONTACT_EMAIL}.`,
      ],
    },
    {
      id: "scope",
      title: "2. Scope",
      paragraphs: [
        "This Policy applies to personal information we process in connection with:",
      ],
      bullets: [
        "Our marketing website and related pages (including philosophy and product pages)",
        "The Momentra web and mobile application experiences",
        "Account creation, authentication, invitations, and support",
        "The digital book experience Life Happens in Moments, where applicable",
        "Analytics, diagnostics, and service improvement tools we operate",
      ],
    },
    {
      id: "information-we-collect",
      title: "3. Information we collect",
      paragraphs: [
        "We collect information in the following categories, depending on how you use the Services.",
      ],
      bullets: [
        "Account and identity information: name, email address, profile photo or avatar, authentication identifiers, and sign-in method (for example Google, email/password, or other providers we support)",
        "Moment and product content: information you create or upload in moments, including purposes, participants, plans, contributions, budgets or money-related entries, timelines, progress, notes, memories, media you choose to attach, roles, and related activity",
        "Invitation and collaboration data: invite links/tokens, participant lists, roles, confirmations, and shared updates within moments you join",
        "Usage and device data: pages viewed, features used, approximate location derived from IP (not precise GPS unless you later enable a feature that requires it), browser/device type, app version, language, referring URLs, and diagnostic logs",
        "Communications: messages you send to support, feedback, and related correspondence",
        "Cookies and similar technologies: as described in our Cookies Policy",
      ],
    },
    {
      id: "sources",
      title: "4. Sources of information",
      paragraphs: [
        "We collect information directly from you, automatically through the Services, and from other users who invite you into moments or add shared context you can see.",
        "If you authenticate with a third-party identity provider, we receive limited account details from that provider consistent with your permissions and their policies.",
      ],
    },
    {
      id: "how-we-use",
      title: "5. How we use information",
      paragraphs: ["We use personal information to:"],
      bullets: [
        "Provide, operate, secure, and improve the Services",
        "Create and manage accounts, authenticate users, and prevent abuse",
        "Enable moment creation, coordination, contributions, pulse/health views, memory, and related product features",
        "Send service communications (for example invites, security notices, and important product updates)",
        "Provide customer support and respond to requests",
        "Measure product and marketing performance using analytics tools",
        "Comply with law, enforce terms, and protect users, Momentra, and the public",
        "Develop new features and understand how the Services are used in aggregate",
      ],
    },
    {
      id: "legal-bases",
      title: "6. Legal bases (where applicable)",
      paragraphs: [
        "If you are in a region that requires a legal basis for processing (for example the EEA/UK), we rely on one or more of: performance of a contract; legitimate interests (such as securing and improving the Services, in a manner that does not override your rights); consent where required (for example certain cookies or marketing); and legal obligation.",
      ],
    },
    {
      id: "sharing",
      title: "7. How we share information",
      paragraphs: [
        "We do not sell your personal information. We may share information in these situations:",
      ],
      bullets: [
        "With other participants in moments you join or create, to the extent needed for shared coordination and visibility inside that moment",
        "With service providers who process data on our behalf (for example hosting, authentication, databases, analytics, email delivery, and error monitoring), under contractual obligations to protect data",
        "For legal, safety, and compliance reasons when we believe disclosure is required or appropriate",
        "In connection with a business transfer (such as a merger, acquisition, or financing), subject to appropriate safeguards",
        "With your direction or consent",
      ],
    },
    {
      id: "retention",
      title: "8. Retention",
      paragraphs: [
        "We retain personal information for as long as needed to provide the Services, maintain account and moment history you expect to keep, comply with legal obligations, resolve disputes, and enforce agreements.",
        "When information is no longer needed, we delete or de-identify it in accordance with our operational practices, subject to backups and legal holds where applicable.",
        "More detail on processing and retention categories appears in our Data Policy.",
      ],
    },
    {
      id: "security",
      title: "9. Security",
      paragraphs: [
        "We use administrative, technical, and organizational measures designed to protect personal information. No method of transmission or storage is completely secure, and we cannot guarantee absolute security.",
        "You are responsible for protecting account credentials and for configuring shared moments thoughtfully when inviting others.",
      ],
    },
    {
      id: "international",
      title: "10. International transfers",
      paragraphs: [
        "We may process and store information in countries other than where you live, including where our providers operate. Where required, we use appropriate transfer mechanisms and contractual protections.",
      ],
    },
    {
      id: "rights",
      title: "11. Your choices and rights",
      paragraphs: [
        "Depending on your location, you may have rights to access, correct, delete, or export personal information; object to or restrict certain processing; withdraw consent where processing is consent-based; and lodge a complaint with a supervisory authority.",
        `To exercise rights, email ${LEGAL_CONTACT_EMAIL}. We may need to verify your request before acting on it.`,
        "You can also update certain profile information in-product and control invitations or participation in moments by leaving or adjusting shared spaces where the product allows.",
      ],
    },
    {
      id: "children",
      title: "12. Children",
      paragraphs: [
        "The Services are not directed to children under 13 (or the minimum age required in your jurisdiction). We do not knowingly collect personal information from children under that age. If you believe a child has provided us information, contact us and we will take appropriate steps.",
      ],
    },
    {
      id: "third-parties",
      title: "13. Third-party services and links",
      paragraphs: [
        "The Services may link to or integrate third-party services (for example identity providers or analytics). Their privacy practices are governed by their own policies. We encourage you to review them.",
      ],
    },
    {
      id: "changes",
      title: "14. Changes to this Policy",
      paragraphs: [
        "We may update this Privacy Policy from time to time. We will post the updated version with a revised “Last updated” date and, when changes are material, provide additional notice as appropriate.",
      ],
    },
  ],
  contactNote: `Questions about privacy: ${LEGAL_CONTACT_EMAIL}`,
};

export const termsOfUse: LegalDocument = {
  slug: "terms",
  title: "Terms of Use",
  description:
    "The agreement between you and Momentra for access to and use of our websites, app, and related services.",
  lastUpdated: LEGAL_LAST_UPDATED,
  intro: [
    `These Terms of Use (“Terms”) govern your access to and use of Momentra’s websites, application, book experience, and related services (the “Services”). By accessing or using the Services, you agree to these Terms.`,
    "If you are using the Services on behalf of an organization, you represent that you have authority to bind that organization, and “you” includes that organization.",
  ],
  sections: [
    {
      id: "eligibility",
      title: "1. Eligibility",
      paragraphs: [
        "You must be legally able to enter a binding contract and meet any minimum age requirements in your jurisdiction to use the Services. If you are under the age of majority, you may use the Services only with involvement of a parent or guardian where required by law.",
      ],
    },
    {
      id: "accounts",
      title: "2. Accounts and security",
      paragraphs: [
        "You may need an account to access certain features. You agree to provide accurate information and to keep credentials confidential.",
        "You are responsible for activity under your account. Notify us promptly of any unauthorized use. We may suspend or terminate accounts that appear compromised, abusive, or in violation of these Terms.",
      ],
    },
    {
      id: "services",
      title: "3. The Services",
      paragraphs: [
        "Momentra helps users organize personal, group, and business moments—including people, plans, money-related coordination, progress, and memory. Features may evolve over time.",
        "We may modify, suspend, or discontinue parts of the Services. We do not guarantee uninterrupted or error-free operation.",
      ],
    },
    {
      id: "acceptable-use",
      title: "4. Acceptable use",
      paragraphs: ["You agree not to:"],
      bullets: [
        "Use the Services unlawfully or to harm others",
        "Upload or share content you do not have rights to share",
        "Harass, abuse, defraud, or impersonate others",
        "Attempt to access accounts, systems, or data without authorization",
        "Interfere with or disrupt the Services, including by malware, scraping beyond permitted use, or overloading infrastructure",
        "Reverse engineer the Services except where such restriction is prohibited by law",
        "Use the Services to process sensitive data in ways that violate applicable law without required consents and safeguards",
      ],
    },
    {
      id: "user-content",
      title: "5. Your content",
      paragraphs: [
        "You retain ownership of content you submit to the Services (“User Content”). You grant Momentra a worldwide, non-exclusive, royalty-free license to host, store, process, display, and transmit User Content solely to operate, improve, and provide the Services and as otherwise described in our Privacy Policy and Data Policy.",
        "You represent that you have all rights needed to submit User Content and that it does not violate law or third-party rights.",
        "Shared moments may make your User Content visible to other participants you invite or who are invited by others with access. Choose participants carefully.",
      ],
    },
    {
      id: "invites",
      title: "6. Invitations and collaboration",
      paragraphs: [
        "If you invite others, you are responsible for ensuring invitations are appropriate and that participants understand what they can see and do in a moment.",
        "Moment owners and role holders may control access according to product features. Removing someone may not erase historical records already visible to remaining participants.",
      ],
    },
    {
      id: "financial",
      title: "7. Money-related and coordination features",
      paragraphs: [
        "Momentra may help track goals, contributions, budgets, and related coordination. Momentra is not a bank, payment processor (unless a specific payment feature says otherwise), investment adviser, or licensed financial institution solely by virtue of these features.",
        "You remain responsible for real-world payments, settlements, tax obligations, and decisions. Information in the Services may be estimates or user-entered and should not be treated as official financial, legal, or tax advice.",
      ],
    },
    {
      id: "ai",
      title: "8. Intelligence and suggestions",
      paragraphs: [
        "Some features may provide health indicators, suggestions, or insights (including AI-assisted guidance). These are informational aids, not guarantees. You remain responsible for decisions you make.",
      ],
    },
    {
      id: "ip",
      title: "9. Momentra intellectual property",
      paragraphs: [
        "The Services, including software, design, trademarks, and brand assets (excluding User Content), are owned by Momentra or its licensors. Except for the limited right to use the Services as permitted, no rights are granted.",
        "Life Happens in Moments and related materials are protected by applicable intellectual property laws. Unauthorized redistribution may be prohibited.",
      ],
    },
    {
      id: "third-party",
      title: "10. Third-party services",
      paragraphs: [
        "The Services may depend on third-party platforms (for example authentication or hosting). Your use of those services may be subject to their terms. We are not responsible for third-party services we do not control.",
      ],
    },
    {
      id: "disclaimer",
      title: "11. Disclaimers",
      paragraphs: [
        'THE SERVICES ARE PROVIDED “AS IS” AND “AS AVAILABLE.” TO THE MAXIMUM EXTENT PERMITTED BY LAW, MOMENTRA DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.',
        "We do not warrant that the Services will meet your requirements or be uninterrupted, secure, or error-free.",
      ],
    },
    {
      id: "liability",
      title: "12. Limitation of liability",
      paragraphs: [
        "TO THE MAXIMUM EXTENT PERMITTED BY LAW, MOMENTRA AND ITS AFFILIATES, OFFICERS, EMPLOYEES, AND AGENTS WILL NOT BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, EXEMPLARY, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS, DATA, GOODWILL, OR BUSINESS OPPORTUNITY, ARISING FROM OR RELATED TO THE SERVICES OR THESE TERMS.",
        "TO THE MAXIMUM EXTENT PERMITTED BY LAW, OUR TOTAL LIABILITY FOR ANY CLAIM ARISING OUT OF OR RELATING TO THE SERVICES OR THESE TERMS WILL NOT EXCEED THE GREATER OF (A) THE AMOUNTS YOU PAID TO MOMENTRA FOR THE SERVICES IN THE TWELVE (12) MONTHS BEFORE THE CLAIM OR (B) ONE HUNDRED U.S. DOLLARS (USD $100) IF YOU HAVE NOT PAID ANY AMOUNTS.",
        "Some jurisdictions do not allow certain limitations; in those cases, our liability is limited to the fullest extent permitted.",
      ],
    },
    {
      id: "indemnity",
      title: "13. Indemnification",
      paragraphs: [
        "You agree to defend, indemnify, and hold harmless Momentra and its affiliates from claims, damages, losses, and expenses (including reasonable attorneys’ fees) arising from your User Content, your use of the Services, or your violation of these Terms or applicable law.",
      ],
    },
    {
      id: "termination",
      title: "14. Suspension and termination",
      paragraphs: [
        "You may stop using the Services at any time. We may suspend or terminate access if you violate these Terms, if required by law, or if needed to protect the Services or others.",
        "Provisions that by their nature should survive (including ownership, disclaimers, limitations, and indemnity) will survive termination.",
      ],
    },
    {
      id: "governing-law",
      title: "15. Governing law",
      paragraphs: [
        "These Terms are governed by the laws applicable to Momentra’s principal place of business operations, without regard to conflict-of-law principles, except where mandatory consumer protections in your country require otherwise.",
        "Courts in that jurisdiction will have exclusive jurisdiction over disputes, except where applicable law gives you the right to bring claims in your home courts.",
      ],
    },
    {
      id: "changes-terms",
      title: "16. Changes to these Terms",
      paragraphs: [
        "We may update these Terms from time to time. Continued use after changes become effective constitutes acceptance of the updated Terms, except where additional consent is required by law.",
      ],
    },
    {
      id: "contact-terms",
      title: "17. Contact",
      paragraphs: [
        `Questions about these Terms: ${LEGAL_CONTACT_EMAIL}.`,
      ],
    },
  ],
  contactNote: `Legal inquiries: ${LEGAL_CONTACT_EMAIL}`,
};

export const dataPolicy: LegalDocument = {
  slug: "data-policy",
  title: "Data Policy",
  description:
    "How Momentra processes, stores, retains, and governs product and operational data across moments and systems.",
  lastUpdated: LEGAL_LAST_UPDATED,
  intro: [
    "This Data Policy complements our Privacy Policy. It describes categories of data Momentra processes to operate the product, how long we keep it, and how processing roles work for personal, group, and business moments.",
    "If there is a conflict between this Data Policy and the Privacy Policy on a personal-information topic, the Privacy Policy controls for that topic.",
  ],
  sections: [
    {
      id: "roles",
      title: "1. Roles and responsibilities",
      paragraphs: [
        "For consumer and end-user accounts, Momentra generally acts as a controller (or similar role under applicable law) for account data and product telemetry we determine how to process.",
        "For content inside moments, especially group and business moments, users who create or administer moments may determine purposes for shared content. In those cases, Momentra typically acts as a processor/service provider for that User Content, while still acting as controller for platform operations, security, and billing or account administration where applicable.",
        "Business customers may request a data processing agreement where required. Contact us to discuss enterprise terms.",
      ],
    },
    {
      id: "categories",
      title: "2. Data categories we process",
      paragraphs: ["Operational data categories include:"],
      bullets: [
        "Identity and authentication records",
        "Moment metadata (type, status, timeline, participants, roles)",
        "Financial coordination entries users enter (amounts, goals, contributions, budgets)—not bank credentials unless a future feature explicitly collects them with separate notice",
        "Activity streams, pulse/health signals, and suggested next steps generated by the product",
        "Memory artifacts users attach (notes, photos, learnings)",
        "Invite tokens and acceptance outcomes",
        "Support tickets and operational logs",
        "Analytics events (including marketing CTA and screen views where enabled)",
      ],
    },
    {
      id: "purposes",
      title: "3. Processing purposes",
      paragraphs: ["We process data to:"],
      bullets: [
        "Deliver core moment lifecycle features (create, invite, plan, contribute, coordinate, complete, remember, learn)",
        "Maintain integrity, availability, and security of the platform",
        "Provide customer support and investigate abuse",
        "Improve reliability, performance, and product design",
        "Meet legal and accounting obligations",
      ],
    },
    {
      id: "storage",
      title: "4. Storage and infrastructure",
      paragraphs: [
        "Momentra uses reputable cloud infrastructure and service providers for application hosting, databases, authentication, file storage, and analytics. Data may be replicated across availability zones for resilience.",
        "Access to production systems is limited to authorized personnel with a need to know, subject to internal controls.",
      ],
    },
    {
      id: "subprocessors",
      title: "5. Subprocessors and vendors",
      paragraphs: [
        "We use vendors to help run the Services. Categories include authentication, application hosting, databases, analytics, email/transactional messaging, and monitoring.",
        "Current examples may include providers such as Firebase (authentication/analytics), Supabase or equivalent database/auth infrastructure, and hosting platforms used to serve the web application. The specific vendor set can change as we scale; we require appropriate contractual protections.",
        `For an updated vendor list relevant to your account, contact ${LEGAL_CONTACT_EMAIL}.`,
      ],
    },
    {
      id: "retention-detail",
      title: "6. Retention schedules",
      paragraphs: [
        "Unless a shorter or longer period is required by law or product settings:",
      ],
      bullets: [
        "Account profile data: retained while the account remains active, then deleted or de-identified within a reasonable period after deletion request or account closure (subject to legal holds)",
        "Active and completed moment content: retained while needed for the moment’s lifecycle and user access expectations; archived or deleted according to product workflows and deletion requests",
        "Invite tokens: retained until used, expired, or revoked",
        "Security and server logs: typically retained for a limited operational window (often up to 12 months) unless needed longer for investigations",
        "Analytics events: retained according to the analytics provider configuration and our measurement needs, often in aggregate or pseudonymous form",
        "Support correspondence: retained as needed to resolve issues and for a reasonable follow-up period",
      ],
    },
    {
      id: "deletion",
      title: "7. Deletion and export",
      paragraphs: [
        `You may request deletion or export of personal data by contacting ${LEGAL_CONTACT_EMAIL}. We will verify the requester and complete requests within timeframes required by applicable law.`,
        "Deleting an account may not immediately remove content that other users still need for a shared moment (for example historical contributions visible to remaining participants). We will explain limitations when they apply.",
      ],
    },
    {
      id: "security-controls",
      title: "8. Security controls",
      paragraphs: [
        "Controls may include encryption in transit (TLS), access controls, least-privilege practices, monitoring, and secure development processes. We continually improve these controls as threats evolve.",
      ],
    },
    {
      id: "breach",
      title: "9. Security incidents",
      paragraphs: [
        "If we become aware of a personal-data breach affecting the Services, we will investigate and notify affected users and authorities as required by law.",
      ],
    },
    {
      id: "ai-data",
      title: "10. Product intelligence data",
      paragraphs: [
        "Pulse, health, and AI-assisted insights are generated from moment context you and other participants provide. We use this context to power in-product guidance. We do not sell moment content to third parties for their independent advertising.",
        "Where models or tooling are provided by vendors, we configure them to support product functionality and apply contractual and technical safeguards appropriate to the use case.",
      ],
    },
    {
      id: "changes-data",
      title: "11. Changes",
      paragraphs: [
        "We may update this Data Policy as our systems and legal requirements change. The “Last updated” date will reflect the latest version.",
      ],
    },
  ],
  contactNote: `Data protection requests: ${LEGAL_CONTACT_EMAIL}`,
};

export const cookiesPolicy: LegalDocument = {
  slug: "cookies",
  title: "Cookies Policy",
  description:
    "How Momentra uses cookies, local storage, and similar technologies on our websites and apps.",
  lastUpdated: LEGAL_LAST_UPDATED,
  intro: [
    "This Cookies Policy explains how Momentra uses cookies and similar technologies (such as local storage, pixels, and SDKs) when you use our websites and Services.",
    "It should be read together with our Privacy Policy.",
  ],
  sections: [
    {
      id: "what-are-cookies",
      title: "1. What are cookies and similar technologies?",
      paragraphs: [
        "Cookies are small text files stored on your device. Similar technologies include local storage, session storage, pixels, and mobile/web SDKs that store or read identifiers on your device.",
        "We use these technologies to keep you signed in, remember preferences, understand how the Services are used, and improve reliability and marketing measurement.",
      ],
    },
    {
      id: "types",
      title: "2. Types we use",
      paragraphs: ["We group technologies as follows:"],
      bullets: [
        "Strictly necessary: required for core functions such as authentication, security, load balancing, and remembering essential settings. These typically do not require consent where law provides an exemption.",
        "Functional: remember choices that improve experience (for example UI preferences).",
        "Analytics/performance: help us understand visits, feature usage, funnel completion, and errors (for example Firebase Analytics screen views and custom events).",
        "Marketing: if enabled in the future, may measure campaign effectiveness. We will update this Policy and consent flows if we introduce non-essential marketing cookies that require consent.",
      ],
    },
    {
      id: "examples",
      title: "3. Examples relevant to Momentra",
      paragraphs: [
        "Depending on configuration, examples include:",
      ],
      bullets: [
        "Session and authentication cookies/tokens used to keep you logged in to /app",
        "Preference storage for theme or context selection",
        "Firebase Analytics identifiers and events for product and marketing measurement (including marketing CTA events tagged with a marketing surface)",
        "Local storage entries that remember lightweight client state",
        "Security and bot-mitigation cookies from infrastructure providers",
      ],
    },
    {
      id: "duration",
      title: "4. Duration",
      paragraphs: [
        "Session technologies expire when you close the browser or after a short period. Persistent technologies remain until they expire or you delete them. Exact durations vary by provider and configuration.",
      ],
    },
    {
      id: "manage",
      title: "5. How to manage cookies",
      paragraphs: [
        "You can control cookies through your browser settings (block, delete, or alert on cookies). Mobile OS settings may limit ad or analytics identifiers.",
        "If you block strictly necessary technologies, parts of the Services may not work (including sign-in).",
        "Where required by law, we will present a consent mechanism for non-essential cookies and honor your choices.",
      ],
    },
    {
      id: "do-not-track",
      title: "6. Do Not Track and global privacy controls",
      paragraphs: [
        "Browsers may send “Do Not Track” signals. There is no consistent industry response standard. Where a Global Privacy Control or similar legally recognized signal applies to us, we will process it as required by applicable law.",
      ],
    },
    {
      id: "updates-cookies",
      title: "7. Updates",
      paragraphs: [
        "We may update this Cookies Policy when our technologies or legal requirements change. Check the “Last updated” date for the latest version.",
      ],
    },
    {
      id: "contact-cookies",
      title: "8. Contact",
      paragraphs: [
        `Questions about cookies: ${LEGAL_CONTACT_EMAIL}.`,
      ],
    },
  ],
  contactNote: `Cookie questions: ${LEGAL_CONTACT_EMAIL}`,
};

export const legalDocuments = {
  privacy: privacyPolicy,
  terms: termsOfUse,
  "data-policy": dataPolicy,
  cookies: cookiesPolicy,
} as const;
