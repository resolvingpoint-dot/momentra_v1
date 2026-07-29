"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { trackMarketingCta } from "@/lib/marketing/track";
import { finalCta } from "@/lib/marketing/copy";

/** Compact sticky CTA for mobile marketing pages */
export default function StickyMobileCTA() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > 420);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <AnimatePresence>
      {visible ? (
        <motion.div
          initial={{ y: 80, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 80, opacity: 0 }}
          transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="fixed inset-x-0 bottom-0 z-40 border-t border-white/10 bg-indigo-900/95 p-3 backdrop-blur-xl md:hidden"
        >
          <a
            href={finalCta.primaryCta.href}
            data-cta={finalCta.primaryCta.event}
            onClick={() => trackMarketingCta(finalCta.primaryCta.event)}
            className="bg-gradient-cta flex w-full items-center justify-center rounded-full px-4 py-3 text-sm font-semibold shadow-lg shadow-ember-500/25"
          >
            {finalCta.primaryCta.label}
          </a>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
