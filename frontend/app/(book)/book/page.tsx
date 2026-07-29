import type { Metadata } from "next";
import bookManifest from "@/data/books/life-happens-in-moments.json";
import { BookExperience } from "@/components/book/BookExperience";
import type { BookManifest } from "@/lib/book/types";

export const metadata: Metadata = {
  title: "Life Happens in Moments — The Book",
  description:
    "An immersive reading experience exploring the philosophy behind Momentra.",
};

export default function BookPage() {
  const manifest = bookManifest as BookManifest;
  return <BookExperience manifest={manifest} />;
}
