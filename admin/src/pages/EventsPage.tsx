import { useState, type FormEvent, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  createEvent,
  deleteEvent,
  fetchEvents,
  updateEvent,
} from "../api/events";
import { ErrorBanner } from "../components/ErrorBanner";
import { PageHeader } from "../components/PageHeader";
import { getErrorMessage } from "../api/client";
import type { EventCreateInput, EventStatus, EventSummary } from "../types";

const emptyForm: EventCreateInput = {
  title: "",
  description: "",
  venue: "",
  event_date: "",
  academic_year: "",
  cover_image_url: null,
  status: "draft",
};

const fullDate = new Intl.DateTimeFormat(undefined, {
  year: "numeric",
  month: "short",
  day: "numeric",
});

export function EventsPage() {
  const queryClient = useQueryClient();
  const [yearFilter, setYearFilter] = useState("");
  const [form, setForm] = useState<EventCreateInput>(emptyForm);
  const [formError, setFormError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  // No "all statuses" filter exists on the API (omitting status returns
  // published only), so we merge published + draft results for the admin
  // list view.
  const eventsQuery = useQuery({
    queryKey: ["events", "admin-list", yearFilter],
    queryFn: async () => {
      const params = yearFilter ? { year: yearFilter } : {};
      const [published, draft] = await Promise.all([
        fetchEvents(params),
        fetchEvents({ ...params, status: "draft" }),
      ]);
      return [...published, ...draft].sort(
        (a, b) =>
          new Date(b.event_date).getTime() - new Date(a.event_date).getTime(),
      );
    },
  });

  const createMutation = useMutation({
    mutationFn: (input: EventCreateInput) => createEvent(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["events"] });
      setForm(emptyForm);
      setShowForm(false);
      setFormError(null);
    },
    onError: (err) => setFormError(getErrorMessage(err)),
  });

  const toggleStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: EventStatus }) =>
      updateEvent(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["events"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteEvent(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["events"] });
    },
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setFormError(null);
    createMutation.mutate(form);
  }

  const events = eventsQuery.data ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Events"
        description="Everything the club has run or has coming up. Drafts stay hidden from students until you publish them."
        actions={
          <button
            type="button"
            onClick={() => setShowForm((v) => !v)}
            className={showForm ? "btn-secondary" : "btn-primary"}
          >
            {showForm ? "Cancel" : "New event"}
          </button>
        }
      />

      {showForm ? (
        <form onSubmit={handleSubmit} className="panel space-y-4 p-6">
          <h2 className="text-lg font-semibold text-ink-900">New event</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Title">
              <input
                required
                value={form.title}
                onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                className="input"
                placeholder="Golden Hour Photowalk"
              />
            </Field>
            <Field label="Venue">
              <input
                required
                value={form.venue}
                onChange={(e) => setForm((f) => ({ ...f, venue: e.target.value }))}
                className="input"
                placeholder="KIC Media Complex"
              />
            </Field>
            <Field label="Event date">
              <input
                required
                type="datetime-local"
                value={form.event_date}
                onChange={(e) =>
                  setForm((f) => ({ ...f, event_date: e.target.value }))
                }
                className="input"
              />
            </Field>
            <Field label="Academic year">
              <input
                required
                placeholder="2025/2026"
                value={form.academic_year}
                onChange={(e) =>
                  setForm((f) => ({ ...f, academic_year: e.target.value }))
                }
                className="input"
              />
            </Field>
          </div>
          <Field label="Description">
            <textarea
              required
              rows={3}
              value={form.description}
              onChange={(e) =>
                setForm((f) => ({ ...f, description: e.target.value }))
              }
              className="input"
              placeholder="What happens, who it is for, what to bring."
            />
          </Field>
          <Field label="Cover image URL" hint="Optional. Paste a link from Cloudinary, R2 or Drive.">
            <input
              type="url"
              value={form.cover_image_url ?? ""}
              onChange={(e) =>
                setForm((f) => ({ ...f, cover_image_url: e.target.value || null }))
              }
              className="input"
              placeholder="https://"
            />
          </Field>
          <ErrorBanner message={formError} />
          <button type="submit" disabled={createMutation.isPending} className="btn-primary">
            {createMutation.isPending ? "Creating…" : "Create event"}
          </button>
        </form>
      ) : null}

      <div className="flex items-end gap-3">
        <label className="w-full max-w-xs text-sm">
          <span className="field-label">Filter by year</span>
          <input
            placeholder="All years"
            value={yearFilter}
            onChange={(e) => setYearFilter(e.target.value)}
            className="input"
          />
        </label>
        {yearFilter ? (
          <button type="button" onClick={() => setYearFilter("")} className="btn-secondary">
            Clear
          </button>
        ) : null}
      </div>

      {eventsQuery.error ? (
        <ErrorBanner message={getErrorMessage(eventsQuery.error)} />
      ) : null}

      {eventsQuery.isLoading ? (
        <div className="skeleton h-64" />
      ) : events.length === 0 ? (
        <div className="empty-state">
          <p className="font-semibold text-ink-900">No events here yet</p>
          <p className="mt-1 text-sm text-ink-600">
            {yearFilter
              ? `Nothing recorded for ${yearFilter}.`
              : "Create the first event to get it in front of students."}
          </p>
        </div>
      ) : (
        <ul className="row-list">
          {events.map((event: EventSummary) => (
            <li key={event.id} className="flex flex-wrap items-center gap-4 px-4 py-3.5">
              {event.cover_image_url ? (
                <img
                  src={event.cover_image_url}
                  alt=""
                  loading="lazy"
                  className="h-14 w-14 shrink-0 rounded-print object-cover"
                />
              ) : (
                <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-print bg-ink-100">
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
              )}

              <div className="min-w-0 flex-1">
                <Link
                  to={`/events/${event.id}`}
                  className="font-semibold text-ink-900 hover:text-navy-600 hover:underline"
                >
                  {event.title}
                </Link>
                <p className="mt-0.5 truncate text-xs text-ink-500">
                  {fullDate.format(new Date(event.event_date))} · {event.venue} ·{" "}
                  {event.academic_year}
                </p>
              </div>

              <div className="flex shrink-0 items-center gap-2">
                <span className={event.status === "published" ? "chip-ok" : "chip-neutral"}>
                  {event.status === "published" ? "Published" : "Draft"}
                </span>
                <button
                  type="button"
                  onClick={() =>
                    toggleStatusMutation.mutate({
                      id: event.id,
                      status: event.status === "published" ? "draft" : "published",
                    })
                  }
                  className="btn-quiet"
                >
                  {event.status === "published" ? "Unpublish" : "Publish"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    if (confirm(`Delete "${event.title}"? This cannot be undone.`)) {
                      deleteMutation.mutate(event.id);
                    }
                  }}
                  className="btn-danger"
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <label className="block text-sm">
      <span className="field-label">{label}</span>
      {children}
      {hint ? <span className="mt-1 block text-xs text-ink-500">{hint}</span> : null}
    </label>
  );
}
