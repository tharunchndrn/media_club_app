import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { fetchEvents } from "../api/events";
import { fetchSuggestions } from "../api/suggestions";
import { ErrorBanner } from "../components/ErrorBanner";
import { PageHeader } from "../components/PageHeader";
import { getErrorMessage } from "../api/client";
import type { SuggestionStatus } from "../types";

const PIPELINE: { status: SuggestionStatus; label: string; color: string }[] = [
  { status: "new", label: "New", color: "#e4a830" },
  { status: "reviewing", label: "Reviewing", color: "#5b7fd4" },
  { status: "planned", label: "Planned", color: "#3fa37a" },
  { status: "declined", label: "Declined", color: "#4a5066" },
];

const dayMonth = new Intl.DateTimeFormat(undefined, {
  month: "short",
  day: "numeric",
});

export function DashboardPage() {
  // Pinned once per mount so "upcoming" stays stable across re-renders.
  const [now] = useState(() => Date.now());

  const eventsQuery = useQuery({
    queryKey: ["events", "all-statuses"],
    // status=draft returns drafts only per the API, so we fetch published
    // (default) and draft separately and merge, since there's no "all" value.
    queryFn: async () => {
      const [published, draft] = await Promise.all([
        fetchEvents({}),
        fetchEvents({ status: "draft" }),
      ]);
      return [...published, ...draft];
    },
  });

  const suggestionsQuery = useQuery({
    queryKey: ["suggestions", "all"],
    queryFn: () => fetchSuggestions(),
  });

  const isLoading = eventsQuery.isLoading || suggestionsQuery.isLoading;
  const error = eventsQuery.error ?? suggestionsQuery.error;

  const suggestions = suggestionsQuery.data ?? [];
  const events = eventsQuery.data ?? [];

  const publishedCount = events.filter((e) => e.status === "published").length;
  const draftCount = events.length - publishedCount;

  const pipeline = PIPELINE.map((segment) => ({
    ...segment,
    count: suggestions.filter((s) => s.status === segment.status).length,
  }));

  const upcoming = [...events]
    .filter((e) => new Date(e.event_date).getTime() >= now)
    .sort(
      (a, b) =>
        new Date(a.event_date).getTime() - new Date(b.event_date).getTime(),
    )
    .slice(0, 4);

  const recentSuggestions = [...suggestions]
    .sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    )
    .slice(0, 5);

  return (
    <div className="space-y-8">
      <PageHeader
        title="Overview"
        description="What the club has scheduled, and what students are asking for."
        actions={
          <Link to="/events" className="btn-primary">
            Manage events
          </Link>
        }
      />

      {error ? <ErrorBanner message={getErrorMessage(error)} /> : null}

      {isLoading ? (
        <div className="space-y-6">
          <div className="skeleton h-44" />
          <div className="grid gap-6 lg:grid-cols-12">
            <div className="skeleton h-72 lg:col-span-7" />
            <div className="skeleton h-72 lg:col-span-5" />
          </div>
        </div>
      ) : (
        <>
          {/* High-level KPI metric cards */}
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <Stat
              label="Total Events"
              value={events.length}
              subtext="Scheduled productions"
              icon={
                <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              }
              color="navy"
            />
            <Stat
              label="Published"
              value={publishedCount}
              subtext="Live on student app"
              icon={
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              }
              color="emerald"
            />
            <Stat
              label="Draft Content"
              value={draftCount}
              subtext="In preparation"
              icon={
                <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              }
              color="slate"
            />
            <Stat
              label="Student Ideas"
              value={suggestions.length}
              subtext="Submitted submissions"
              icon={
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              }
              color="amber"
            />
          </div>

          <PipelinePanel segments={pipeline} total={suggestions.length} />

          <div className="grid gap-8 lg:grid-cols-12">
            <section className="min-w-0 lg:col-span-7">
              <SectionHead
                title="Next up"
                caption="Events still ahead of today"
                to="/events"
                linkLabel="All events"
              />
              {upcoming.length === 0 ? (
                <div className="empty-state">
                  <p className="text-sm text-ink-600">
                    Nothing scheduled yet.{" "}
                    <Link to="/events" className="font-semibold text-navy-600 hover:underline">
                      Add the next event
                    </Link>
                    .
                  </p>
                </div>
              ) : (
                <ul className="row-list">
                  {upcoming.map((event) => (
                    <li key={event.id}>
                      <Link
                        to={`/events/${event.id}`}
                        className="flex items-center gap-4 px-4 py-3 transition-colors hover:bg-navy-50 focus-visible:bg-navy-50 focus-visible:outline-none"
                      >
                        <Thumb src={event.cover_image_url} />
                        <span className="min-w-0 flex-1">
                          <span className="block truncate font-semibold text-ink-900">
                            {event.title}
                          </span>
                          <span className="mt-0.5 block truncate text-xs text-ink-500">
                            {dayMonth.format(new Date(event.event_date))} · {event.venue}
                          </span>
                        </span>
                        <span
                          className={
                            event.status === "published" ? "chip-ok" : "chip-neutral"
                          }
                        >
                          {event.status === "published" ? "Published" : "Draft"}
                        </span>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className="min-w-0 lg:col-span-5">
              <SectionHead
                title="Latest suggestions"
                caption="Newest first"
                to="/suggestions"
                linkLabel="Open inbox"
              />
              {recentSuggestions.length === 0 ? (
                <div className="empty-state">
                  <p className="text-sm text-ink-600">
                    No suggestions have come in yet.
                  </p>
                </div>
              ) : (
                <ul className="row-list">
                  {recentSuggestions.map((s) => (
                    <li key={s.id} className="px-4 py-3">
                      <div className="flex items-center justify-between gap-2">
                        <span className="chip-navy">{s.category}</span>
                        <span className="text-xs text-ink-500">
                          {dayMonth.format(new Date(s.created_at))}
                        </span>
                      </div>
                      <p className="mt-2 line-clamp-2 text-sm text-ink-700">{s.body}</p>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </div>
        </>
      )}
    </div>
  );
}

function PipelinePanel({
  segments,
  total,
}: {
  segments: { status: string; label: string; color: string; count: number }[];
  total: number;
}) {
  return (
    <section className="rounded-2xl bg-gradient-to-br from-navy-950 via-navy-900 to-navy-800 p-6 text-white shadow-md sm:p-7 border border-navy-800">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Student Suggestion Pipeline</h2>
          <p className="text-xs text-navy-100/70 mt-0.5">Live idea triage & status distribution</p>
        </div>
        <p className="text-sm text-navy-100/80">
          <span className="text-2xl font-black text-gold-400">{total}</span>{" "}
          {total === 1 ? "suggestion" : "suggestions"} total
        </p>
      </div>

      {total === 0 ? (
        <p className="mt-5 text-sm text-navy-100/70">
          Once students start submitting, their ideas break down here by status.
        </p>
      ) : (
        <>
          <div
            className="mt-5 flex h-3.5 overflow-hidden rounded-full bg-navy-950/60 p-0.5 ring-1 ring-white/10"
            role="img"
            aria-label={segments.map((s) => `${s.label}: ${s.count}`).join(", ")}
          >
            {segments
              .filter((s) => s.count > 0)
              .map((s) => (
                <div
                  key={s.status}
                  className="rounded-full first:rounded-l-full last:rounded-r-full transition-all duration-500"
                  style={{
                    width: `${(s.count / total) * 100}%`,
                    backgroundColor: s.color,
                  }}
                />
              ))}
          </div>

          <ul className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
            {segments.map((s) => {
              const pct = total > 0 ? Math.round((s.count / total) * 100) : 0;
              return (
                <li
                  key={s.status}
                  className="rounded-xl bg-white/5 border border-white/10 p-3.5 backdrop-blur-xs transition hover:bg-white/10"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span
                        aria-hidden="true"
                        className="h-2.5 w-2.5 shrink-0 rounded-full shadow-xs"
                        style={{ backgroundColor: s.color }}
                      />
                      <span className="text-xs font-semibold text-navy-100/80">{s.label}</span>
                    </div>
                    <span className="text-[11px] font-bold text-navy-200/60">{pct}%</span>
                  </div>
                  <p className="mt-1.5 text-2xl font-black text-white">{s.count}</p>
                </li>
              );
            })}
          </ul>
        </>
      )}
    </section>
  );
}

function Stat({
  label,
  value,
  subtext,
  icon,
  color,
}: {
  label: string;
  value: number;
  subtext?: string;
  icon: React.ReactNode;
  color: "navy" | "emerald" | "slate" | "amber";
}) {
  const colorMap = {
    navy: "bg-navy-50 text-navy-700 border-navy-200",
    emerald: "bg-emerald-50 text-emerald-700 border-emerald-200",
    slate: "bg-slate-100 text-slate-700 border-slate-200",
    amber: "bg-amber-50 text-amber-700 border-amber-200",
  };

  return (
    <div className="rounded-xl border border-ink-200 bg-white p-5 shadow-sm transition-all hover:shadow-md">
      <div className="flex items-center justify-between">
        <dt className="text-xs font-bold uppercase tracking-wider text-ink-500">{label}</dt>
        <span className={`inline-flex rounded-lg border p-2 ${colorMap[color]}`}>
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            {icon}
          </svg>
        </span>
      </div>
      <dd className="mt-2 text-3xl font-extrabold tracking-tight text-ink-900">{value}</dd>
      {subtext && <p className="mt-1 text-xs text-ink-400 font-medium">{subtext}</p>}
    </div>
  );
}

function SectionHead({
  title,
  caption,
  to,
  linkLabel,
}: {
  title: string;
  caption: string;
  to: string;
  linkLabel: string;
}) {
  return (
    <div className="mb-3 flex items-end justify-between gap-3">
      <div>
        <h2 className="text-base font-semibold text-ink-900">{title}</h2>
        <p className="text-xs text-ink-500">{caption}</p>
      </div>
      <Link
        to={to}
        className="shrink-0 text-sm font-semibold text-navy-600 hover:text-navy-700 hover:underline"
      >
        {linkLabel}
      </Link>
    </div>
  );
}

function Thumb({ src }: { src: string | null }) {
  if (src) {
    return (
      <img
        src={src}
        alt=""
        loading="lazy"
        className="h-12 w-12 shrink-0 rounded-print object-cover"
      />
    );
  }
  return (
    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-print bg-ink-100">
      <svg
        aria-hidden="true"
        className="h-5 w-5 text-ink-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={1.5}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
        />
      </svg>
    </div>
  );
}
