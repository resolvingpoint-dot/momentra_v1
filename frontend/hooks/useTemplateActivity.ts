import { useCallback, useEffect, useMemo, useState } from "react";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";
import { getActivityAdapter } from "@/lib/personal/template/activity/getActivityAdapter";
import type {
  TemplateActivityItem,
  TemplateActivitySummary,
} from "@/lib/personal/template/activity/types";
import { PersonalRepository } from "@/repositories/PersonalRepository";

function computeSummary(items: TemplateActivityItem[]): TemplateActivitySummary {
  const monthStart = new Date();
  monthStart.setDate(1);
  monthStart.setHours(0, 0, 0, 0);
  return {
    total_logs: items.length,
    this_month: items.filter((item) => new Date(item.occurred_at) >= monthStart).length,
    total_amount_minor: items.reduce((sum, item) => sum + (item.amount_minor || 0), 0),
  };
}

export function useTemplateActivity(
  momentTypeCode: PersonalMomentTypeCode,
  momentId: string | null,
) {
  const adapter = useMemo(() => getActivityAdapter(momentTypeCode), [momentTypeCode]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [items, setItems] = useState<TemplateActivityItem[]>([]);

  const load = useCallback(async () => {
    if (!momentId) {
      setItems([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await PersonalRepository.listTemplateActivity(momentTypeCode, momentId);
      setItems(data.items ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load activity.");
    } finally {
      setLoading(false);
    }
  }, [momentId, momentTypeCode]);

  useEffect(() => {
    void load();
  }, [load]);

  const summary = useMemo(() => computeSummary(items), [items]);

  return {
    adapter,
    loading,
    error,
    items,
    summary,
    reload: load,
  };
}
