"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X } from "lucide-react";
import { MarketingBrandLogo } from "@/components/marketing/MarketingBrandLogo";
import { nav } from "@/lib/marketing/copy";
import { trackMarketingCta } from "@/lib/marketing/track";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  return (
    <nav className="mkt-nav fixed top-0 left-0 right-0 z-50 border-b border-white/10 backdrop-blur-xl transition-all duration-500">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between gap-4 lg:h-20">
          <Link
            href="/"
            className="flex shrink-0 items-center"
            aria-label="Momentra home"
            onClick={() => setOpen(false)}
          >
            <MarketingBrandLogo className="h-9 w-auto max-w-[160px]" />
          </Link>

          <div className="hidden items-center gap-6 lg:flex xl:gap-8">
            {nav.links.map((link) => {
              const active =
                link.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(link.href);
              return (
                <Link
                  key={link.label}
                  href={link.href}
                  className={`relative group text-sm transition-colors duration-300 ${
                    active
                      ? "text-text-on-dark"
                      : "mkt-muted hover:text-text-on-dark"
                  }`}
                >
                  {link.label}
                  <span
                    className={`absolute -bottom-1 left-0 h-px bg-ember-500 transition-all duration-300 ${
                      active ? "w-full" : "w-0 group-hover:w-full"
                    }`}
                  />
                </Link>
              );
            })}
          </div>

          <div className="hidden items-center gap-3 lg:flex">
            <Link
              href={nav.secondaryCta.href}
              onClick={() => trackMarketingCta(nav.secondaryCta.event)}
              data-cta={nav.secondaryCta.event}
              className="mkt-muted hidden text-sm transition-colors hover:text-text-on-dark xl:inline"
            >
              {nav.secondaryCta.label}
            </Link>
            <motion.a
              href={nav.primaryCta.href}
              onClick={() => trackMarketingCta(nav.primaryCta.event)}
              data-cta={nav.primaryCta.event}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className="bg-gradient-cta inline-flex items-center rounded-full px-4 py-2 text-sm font-semibold shadow-lg shadow-ember-500/25 transition-all duration-300 hover:brightness-110"
            >
              {nav.primaryCta.label}
            </motion.a>
          </div>

          <button
            type="button"
            onClick={() => setOpen(!open)}
            className="mkt-muted p-2 hover:text-text-on-dark lg:hidden"
            aria-label={open ? "Close menu" : "Open menu"}
            aria-expanded={open}
          >
            {open ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 24 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="mkt-nav border-t border-white/10 px-4 py-6 backdrop-blur-xl lg:hidden"
          >
            <div className="flex flex-col gap-1">
              {nav.links.map((link) => (
                <Link
                  key={link.label + "m"}
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="mkt-muted rounded-lg px-3 py-3 text-sm transition-colors hover:bg-white/5 hover:text-text-on-dark"
                >
                  {link.label}
                </Link>
              ))}
              <Link
                href={nav.secondaryCta.href}
                onClick={() => {
                  trackMarketingCta(nav.secondaryCta.event);
                  setOpen(false);
                }}
                data-cta={nav.secondaryCta.event}
                className="mkt-muted mt-2 rounded-lg px-3 py-3 text-sm hover:text-text-on-dark"
              >
                {nav.secondaryCta.label}
              </Link>
              <motion.a
                href={nav.primaryCta.href}
                onClick={() => trackMarketingCta(nav.primaryCta.event)}
                data-cta={nav.primaryCta.event}
                whileTap={{ scale: 0.97 }}
                className="bg-gradient-cta mt-2 inline-flex items-center justify-center rounded-full px-4 py-2.5 text-sm font-semibold"
              >
                {nav.primaryCta.label}
              </motion.a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
