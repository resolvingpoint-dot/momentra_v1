"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { MarketingBrandLogo } from "@/components/marketing/MarketingBrandLogo";
import { footer } from "@/lib/marketing/copy";
import { fadeUp, staggerContainer } from "@/lib/marketing/animations";

export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-indigo-900 py-16 sm:py-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="mb-12 grid grid-cols-2 gap-8 md:grid-cols-3 lg:grid-cols-5 lg:gap-10"
        >
          <motion.div
            variants={fadeUp}
            className="col-span-2 md:col-span-3 lg:col-span-1"
          >
            <Link href="/" className="mb-4 inline-block" aria-label="Momentra home">
              <MarketingBrandLogo className="h-10 w-auto max-w-[180px]" />
            </Link>
            <p className="mkt-muted max-w-xs text-sm leading-relaxed">
              {footer.statement}
            </p>
          </motion.div>

          {footer.columns.map((col) => (
            <motion.div key={col.title} variants={fadeUp}>
              <h4 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-on-dark">
                {col.title}
              </h4>
              <ul className="space-y-3">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <Link
                      href={l.href}
                      className="mkt-muted text-sm transition-colors duration-300 hover:text-text-on-dark"
                    >
                      {l.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </motion.div>

        <div className="border-t border-white/10 pt-8 pb-20 md:pb-0">
          <p className="mkt-muted text-center text-sm">
            &copy; {new Date().getFullYear()} Momentra. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
