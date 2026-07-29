"use client";

import { motion } from "framer-motion";
import { emotional } from "@/lib/marketing/copy";
import { viewportConfig } from "@/lib/marketing/animations";

export default function EmotionalStatement() {
  return (
    <section
      id="emotional"
      className="bg-[#08060f] py-28 sm:py-36 lg:py-44"
    >
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="space-y-8 sm:space-y-10">
          {emotional.lines.map((line, i) => (
            <motion.p
              key={line}
              initial={{ opacity: 0, y: 28 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={viewportConfig}
              transition={{
                duration: 0.8,
                delay: i * 0.15,
                ease: [0.16, 1, 0.3, 1],
              }}
              className={`text-2xl font-semibold tracking-tight sm:text-3xl md:text-4xl lg:text-5xl ${
                i === emotional.lines.length - 1
                  ? "text-text-on-dark"
                  : "text-white/45"
              }`}
            >
              {line}
            </motion.p>
          ))}
        </div>
      </div>
    </section>
  );
}
