export interface BookContentsEntry {
  title: string;
  /** 1-based sequential page index in the reader */
  page: number;
}

export interface BookTransition {
  /** Show after leaving this 1-based sequential page */
  afterPage: number;
  message: string;
  cta: string;
}

export interface BookMilestone {
  id: string;
  message: string;
  /** 1-based sequential page index */
  atPage?: number;
  /** 0–100 completion percent */
  atPercent?: number;
}

export interface BookManifest {
  id: string;
  title: string;
  subtitle: string;
  assetBase: string;
  pages: string[];
  contents: BookContentsEntry[];
  transitions: BookTransition[];
  milestones: BookMilestone[];
}

export interface BookProgress {
  currentPage: number;
  completionPercent: number;
  readingTimeMs: number;
  lastReadAt: string | null;
  bookmarks: number[];
  milestones: string[];
  /** Transition afterPage values already shown (persisted lightly) */
  seenTransitions: number[];
  version: 1;
}

export type BookPhase =
  | "intro"
  | "auth"
  | "resume"
  | "reading"
  | "end";
