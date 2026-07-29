import { useCallback, useEffect, useState } from "react";
import { PersonalRepository } from "@/repositories/PersonalRepository";
import type {
  UnifiedActivityInsight,
  UnifiedActivitySnapshot,
  UnifiedPersonalActivityItem,
} from "@/lib/personal/template/activity/types";

const EMPTY_SNAPSHOT: UnifiedActivitySnapshot = {
  headline: "Start logging moments and your life story will appear here.",
  today_activity_count: 0,
  today_amount_minor: 0,
  today_mood_label: null,
  today_domain_labels: [],
};

export function useUnifiedActivity(filters: {
  range: string;
  domain: string;
  kind: string;
  q: string;
}) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [items, setItems] = useState<UnifiedPersonalActivityItem[]>([]);
  const [snapshot, setSnapshot] = useState<UnifiedActivitySnapshot>(EMPTY_SNAPSHOT);
  const [insights, setInsights] = useState<UnifiedActivityInsight[]>([]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await PersonalRepository.listUnifiedActivity({
        range: filters.range,
        domain: filters.domain,
        kind: filters.kind,
        q: filters.q.trim() || undefined,
        limit: 100,
      });
      setItems(data.items ?? []);
      setSnapshot(data.snapshot ?? EMPTY_SNAPSHOT);
      setInsights(data.insights ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load your life story.");
      setItems([]);
      setSnapshot(EMPTY_SNAPSHOT);
      setInsights([]);
    } finally {
      setLoading(false);
    }
  }, [filters.domain, filters.kind, filters.q, filters.range]);

  useEffect(() => {
    void load();
  }, [load]);

  return { loading, error, items, snapshot, insights, reload: load };
}
