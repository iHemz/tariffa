"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchHealth, fetchPing } from "@/lib/api";

function StatusRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-6 rounded-lg border border-black/[.08] px-4 py-3 dark:border-white/[.145]">
      <span className="font-medium text-zinc-700 dark:text-zinc-300">{label}</span>
      <span className="text-sm">{children}</span>
    </div>
  );
}

export default function Home() {
  // Phase 0 round-trip: prove browser → FastAPI → (Claude, for /ping) works end to end.
  const health = useQuery({ queryKey: ["health"], queryFn: fetchHealth });

  // The agent call is opt-in (it costs an LLM request and needs ANTHROPIC_API_KEY).
  const ping = useQuery({ queryKey: ["ping"], queryFn: fetchPing, enabled: false });

  return (
    <main className="mx-auto flex w-full max-w-xl flex-1 flex-col gap-8 px-6 py-24">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-semibold tracking-tight">Tariffa</h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          Phase 0 skeleton — confirming the full stack talks to itself.
        </p>
      </header>

      <section className="flex flex-col gap-3">
        <StatusRow label="API health">
          {health.isPending ? (
            <span className="text-zinc-500">checking…</span>
          ) : health.isError ? (
            <span className="text-red-600">unreachable — is apps/api running?</span>
          ) : (
            <span className="text-green-600">
              {health.data.status} · {health.data.service}
            </span>
          )}
        </StatusRow>

        <StatusRow label="Agent round-trip (Claude)">
          {ping.isFetching ? (
            <span className="text-zinc-500">calling agent…</span>
          ) : ping.isError ? (
            <span className="text-red-600">{ping.error.message}</span>
          ) : ping.data ? (
            <span className="text-green-600">{ping.data.message}</span>
          ) : (
            <button
              onClick={() => ping.refetch()}
              className="rounded-full bg-foreground px-4 py-1.5 text-background transition-colors hover:opacity-90"
            >
              Run agent
            </button>
          )}
        </StatusRow>
      </section>
    </main>
  );
}
