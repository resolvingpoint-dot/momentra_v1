"use client";

import { motion } from "framer-motion";
import { sharedArchitecture } from "@/lib/marketing/copy";
import {
  fadeUp,
  staggerContainer,
  viewportConfig,
} from "@/lib/marketing/animations";

function BulletList({ points }: { points: string[] }) {
  if (points.length === 0) return null;

  return (
    <ul className="space-y-1.5">
      {points.map((p) => (
        <li key={p} className="text-xs leading-relaxed text-white/55 sm:text-sm">
          · {p}
        </li>
      ))}
    </ul>
  );
}

function AreaHeader({
  index,
  name,
}: {
  index: number;
  name: string;
}) {
  return (
    <>
      <p className="mb-2 text-xs font-medium uppercase tracking-widest text-ember-500">
        {String(index + 1).padStart(2, "0")}
      </p>
      <h3 className="mb-2 text-lg font-bold text-text-on-dark sm:text-xl">
        {name}
      </h3>
    </>
  );
}

export default function SharedArchitecture() {
  return (
    <section id="architecture" className="py-16 sm:py-24 lg:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          className="mb-10 text-center sm:mb-14"
        >
          <motion.h2
            variants={fadeUp}
            className="mb-4 text-3xl font-extrabold tracking-tight text-text-on-dark sm:text-4xl md:text-5xl"
          >
            {sharedArchitecture.heading}
          </motion.h2>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          className="relative flex flex-col gap-4 sm:gap-5 lg:grid lg:grid-cols-6 lg:gap-4"
        >
          {sharedArchitecture.areas.map((area, i) => {
            const isLife = area.name === "Life";
            const supporting =
              "supporting" in area && area.supporting ? area.supporting : null;

            return (
              <motion.div
                key={area.name}
                variants={fadeUp}
                className={`relative mkt-surface flex w-full flex-col rounded-2xl border border-white/10 p-5 sm:p-6 ${
                  isLife ? "lg:col-span-2" : "lg:col-span-1"
                }`}
              >
                {isLife ? (
                  <div className="flex flex-col gap-4 sm:gap-5 lg:grid lg:grid-cols-2 lg:gap-4">
                    <div>
                      <AreaHeader index={i} name={area.name} />
                      <p className="mkt-muted mb-2 text-sm leading-relaxed sm:text-base">
                        {area.description}
                      </p>
                      {supporting ? (
                        <p className="mkt-muted text-sm leading-relaxed sm:text-base lg:mb-0">
                          {supporting}
                        </p>
                      ) : null}
                    </div>
                    <div className="border-t border-white/10 pt-4 lg:border-t-0 lg:pt-0 lg:flex lg:flex-col lg:justify-center">
                      <BulletList points={area.points} />
                    </div>
                  </div>
                ) : (
                  <>
                    <AreaHeader index={i} name={area.name} />
                    <p className="mkt-muted mb-4 text-sm leading-relaxed sm:text-base">
                      {area.description}
                    </p>
                    <BulletList points={area.points} />
                  </>
                )}
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
