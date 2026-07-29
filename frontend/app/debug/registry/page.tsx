"use client";

import {
  QUICK_ADD_TEMPLATE_BUNDLES,
  getQuickAddBundle,
  listQuickAddTemplateIds,
} from "@/lib/quick_add/registry";

export default function DebugRegistryPage() {
  if (process.env.NODE_ENV === "production") {
    return (
      <main className="mx-auto max-w-3xl p-6">
        <p className="text-sm opacity-70">Registry inspector is only available in development.</p>
      </main>
    );
  }

  const templateIds = listQuickAddTemplateIds();

  return (
    <main className="mx-auto max-w-4xl space-y-8 p-6 font-mono text-sm">
      <header>
        <h1 className="text-xl font-semibold">Registry Inspector</h1>
        <p className="mt-1 opacity-70">Quick Add template bundles registered on the web client.</p>
      </header>

      <section className="space-y-3">
        <h2 className="text-base font-semibold">Summary</h2>
        <ul className="space-y-1 opacity-90">
          <li>Template bundles: {QUICK_ADD_TEMPLATE_BUNDLES.length}</li>
          <li>Template IDs: {templateIds.join(", ")}</li>
        </ul>
      </section>

      {QUICK_ADD_TEMPLATE_BUNDLES.map((bundle) => {
        const resolved = getQuickAddBundle(bundle.template_id);
        const actions = [
          ...(resolved?.actions ?? []),
          ...(resolved?.sub_flows ?? []),
        ];
        return (
          <section
            key={bundle.template_id}
            className="rounded-xl border border-white/10 p-4"
          >
            <h2 className="font-semibold">{bundle.template_id}</h2>
            <p className="opacity-70">context: {bundle.context}</p>
            <p className="mt-2 opacity-90">actions ({actions.length})</p>
            <ul className="mt-2 list-inside list-disc space-y-1">
              {actions.map((action) => (
                <li key={action.action_id}>
                  {action.action_id} — {action.label}
                  {action.tab_code ? ` [${action.tab_code}]` : ""}
                </li>
              ))}
            </ul>
          </section>
        );
      })}
    </main>
  );
}
