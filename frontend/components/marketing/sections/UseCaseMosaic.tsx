"use client";

import { motion } from "framer-motion";
import { mosaic } from "@/lib/marketing/copy";
import {
  fadeUp,
  staggerContainer,
  viewportConfig,
} from "@/lib/marketing/animations";

type Tile = {
  title: string;
  stage: string;
  progress: string;
  update: string;
  people?: string;
};

const columns: { label: string; accent: string; tiles: Tile[] }[] = [
  {
    label: "Personal",
    accent: "border-indigo-300/25",
    tiles: mosaic.personal,
  },
  {
    label: "Group",
    accent: "border-[#ff8a6a]/30",
    tiles: mosaic.group,
  },
  {
    label: "Business",
    accent: "border-amber-500/25",
    tiles: mosaic.business,
  },
];

function TileCard({
  tile,
  accent,
}: {
  tile: Tile;
  accent: string;
}) {
  return (
    <div
      className={`mkt-surface w-full min-w-0 snap-start rounded-xl border p-4 ${accent}`}
    >
      <div className="mb-2 flex items-start justify-between gap-2">
        <h4 className="min-w-0 break-words text-sm font-semibold text-text-on-dark">
          {tile.title}
        </h4>
        <span className="shrink-0 rounded-md bg-white/5 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-white/50">
          {tile.stage}
        </span>
      </div>
      {tile.people ? (
        <p className="mb-1 text-xs text-white/55">{tile.people}</p>
      ) : null}
      <p className="mb-1 text-xs font-medium text-indigo-100/80">{tile.progress}</p>
      <p className="mkt-muted text-xs">{tile.update}</p>
    </div>
  );
}

export default function UseCaseMosaic() {
  return (
    <section id="mosaic" className="py-24 sm:py-32">
      <div className="mx-auto w-full min-w-0 max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.h2
          variants={fadeUp}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          className="mb-12 text-center text-3xl font-extrabold tracking-tight text-text-on-dark sm:text-4xl"
        >
          Moments across life
        </motion.h2>

        <div className="space-y-10">
          {columns.map((col) => (
            <motion.div
              key={col.label}
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={viewportConfig}
            >
              <h3 className="mb-4 text-sm font-semibold uppercase tracking-widest text-white/45">
                {col.label}
              </h3>
              <div className="flex w-full min-w-0 snap-x gap-3 overflow-x-auto pb-2 sm:grid sm:grid-cols-2 sm:overflow-visible md:grid-cols-5 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
                {col.tiles.map((tile) => (
                  <motion.div
                    key={tile.title}
                    variants={fadeUp}
                    className="w-[min(200px,75vw)] shrink-0 sm:w-auto sm:min-w-0"
                  >
                    <TileCard tile={tile} accent={col.accent} />
                  </motion.div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
