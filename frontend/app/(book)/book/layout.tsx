import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Life Happens in Moments",
  description: "The philosophy behind Momentra — an immersive reading experience.",
};

export default function BookLayout({ children }: { children: ReactNode }) {
  return (
    <div className="book-root min-h-dvh bg-[#0a0614] text-white antialiased">
      {children}
    </div>
  );
}
