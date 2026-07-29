"use client";

import CTAButton from "@/components/marketing/CTAButton";
import { motion } from "framer-motion";
import { fadeUp, staggerContainer, viewportConfig } from "@/lib/marketing/animations";

type Cta = { label: string; href: string; event: string };

export function MarketingPageShell({
  eyebrow,
  title,
  description,
  children,
  primaryCta,
  secondaryCta,
}: {
  eyebrow?: string;
  title: string;
  description: string;
  children?: React.ReactNode;
  primaryCta?: Cta;
  secondaryCta?: Cta;
}) {
  return (
    <main className="relative min-w-0 pt-24 pb-24 sm:pt-28 md:pb-0">
      <section className="pb-16 sm:pb-20">
        <div className="mx-auto w-full min-w-0 max-w-4xl px-4 sm:px-6 lg:px-8">
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
          >
            {eyebrow ? (
              <motion.p
                variants={fadeUp}
                className="mb-3 text-sm font-medium uppercase tracking-widest text-ember-500"
              >
                {eyebrow}
              </motion.p>
            ) : null}
            <motion.h1
              variants={fadeUp}
              className="mb-5 text-3xl font-extrabold tracking-tight break-words text-text-on-dark sm:text-4xl md:text-5xl"
            >
              {title}
            </motion.h1>
            <motion.p
              variants={fadeUp}
              className="mkt-muted mb-8 max-w-2xl text-base leading-relaxed sm:text-lg"
            >
              {description}
            </motion.p>
            {(primaryCta || secondaryCta) && (
              <motion.div
                variants={fadeUp}
                className="flex w-full flex-col gap-3 sm:flex-row"
              >
                {primaryCta ? (
                  <CTAButton
                    variant="primary"
                    href={primaryCta.href}
                    event={primaryCta.event}
                    className="w-full max-w-sm sm:w-auto"
                  >
                    {primaryCta.label}
                  </CTAButton>
                ) : null}
                {secondaryCta ? (
                  <CTAButton
                    variant="secondary"
                    href={secondaryCta.href}
                    event={secondaryCta.event}
                    className="w-full max-w-sm sm:w-auto"
                  >
                    {secondaryCta.label}
                  </CTAButton>
                ) : null}
              </motion.div>
            )}
          </motion.div>
        </div>
      </section>
      {children ? (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={viewportConfig}
          transition={{ duration: 0.6 }}
        >
          {children}
        </motion.div>
      ) : null}
    </main>
  );
}

export function ContentBlock({
  title,
  children,
}: {
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="pb-16 sm:pb-20">
      <div className="mx-auto w-full min-w-0 max-w-4xl px-4 sm:px-6 lg:px-8">
        {title ? (
          <h2 className="mb-4 text-xl font-bold break-words text-text-on-dark sm:text-2xl">
            {title}
          </h2>
        ) : null}
        <div className="mkt-muted space-y-4 break-words text-base leading-relaxed">
          {children}
        </div>
      </div>
    </section>
  );
}
