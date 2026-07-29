"use client";

import { motion } from "framer-motion";

interface PageProps {
  src: string;
  alt: string;
  priority?: boolean;
}

export function Page({ src, alt, priority = false }: PageProps) {
  return (
    <motion.img
      key={src}
      src={src}
      alt={alt}
      decoding="async"
      loading={priority ? "eager" : "lazy"}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="mx-auto block h-auto w-full max-w-3xl select-none"
      draggable={false}
    />
  );
}
