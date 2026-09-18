import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchSuggestions, updateSuggestionStatus } from "../api/suggestions";
import { ErrorBanner } from "../components/ErrorBanner";
import { PageHeader } from "../components/PageHeader";
import { getErrorMessage } from "../api/client";
import type { SuggestionStatus } from "../types";

const STATUSES: SuggestionStatus[] = ["new", "reviewing", "planned", "declined"];

const STATUS_LABEL: Record<SuggestionStatus, string> = {
  new: "New",
  reviewing: "Reviewing",
  planned: "Planned",
  declined: "Declined",
};

// Same colours as the dashboard pipeline, so a status reads identically in
// both places. The status word is always present in the select beside it.
const STATUS_COLOR: Record<SuggestionStatus, string> = {
  new: "#e4a830",
  reviewing: "#5b7fd4",
  planned: "#3fa37a",
  declined: "#b6bac8",
};

const fullDate = new Intl.DateTimeFormat(undefined, {
  year: "numeric",
  month: "short",
  day: "numeric",
});

export function SuggestionsPage() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<SuggestionStatus | "">("");
  const [batchFilter, setBatchFilter] = useState("");
  const [mutationError, setMutationError] = useState<string | null>(null);

  const suggestionsQuery = useQuery({
    queryKey: ["suggestions", statusFilter, batchFilter],
    queryFn: () =>
      fetchSuggestions({
        status: statusFilter || undefined,
        batch: batchFilter || undefined,
      }),
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: SuggestionStatus }) =>
      updateSuggestionStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["suggestions"] });
      setMutationError(null);
    },
    onError: (err) => setMutationError(getErrorMessage(err)),
  });

  const suggestions = suggestionsQuery.data ?? [];
  const isFiltered = Boolean(statusFilter || batchFilter);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Suggestions"
        description="What students have asked the club to do. Move each one along as you work through it."
      />

      <div className="panel flex flex-wrap items-end gap-4 p-4">
        <label className="min-w-[160px] flex-1 text-sm">
          <span className="field-label">Status</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as SuggestionStatus | "")}
            className="input"
          >
            <option value="">All statuses</option>
            {STATUSES.map((status) => (
              <option key={status} value={status}>
                {STATUS_LABEL[status]}
              </option>
            ))}
          </select>
        </label>
        <label className="min-w-[160px] flex-1 text-sm">
          <span className="field-label">Batch</span>
          <input
            value={batchFilter}
            onChange={(e) => setBatchFilter(e.target.value)}
            placeholder="All batches"
            className="input"
          />
        </label>
        {isFiltered ? (
          <button
            type="button"
            onClick={() => {
              setStatusFilter("");
              setBatchFilter("");
            }}
            className="btn-secondary"
          >
            Clear filters
          </button>
        ) : null}
      </div>

      <ErrorBanner message={mutationError} />

      {suggestionsQuery.error ? (
        <ErrorBanner message={getErrorMessage(suggestionsQuery.error)} />
      ) : null}

      {suggestionsQuery.isLoading ? (
        <div className="skeleton h-64" />
      ) : suggestions.length === 0 ? (
        <div className="empty-state">
          <p className="font-semibold text-ink-900">Nothing to review</p>
          <p className="mt-1 text-sm text-ink-600">
            {isFiltered
              ? "No suggestions match these filters."
              : "Suggestions submitted in the student app land here."}
          </p>
        </div>
      ) : (
        <ul className="row-list">
          {suggestions.map((suggestion) => (
            <li key={suggestion.id} className="relative py-4 pr-4 pl-5">
              <span
                aria-hidden="true"
                className="absolute top-0 left-0 h-full w-[3px]"
                style={{ backgroundColor: STATUS_COLOR[suggestion.status] }}
              />
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="chip-navy">{suggestion.category}</span>
                  <span className="text-xs text-ink-500">
                    {suggestion.is_anonymous
                      ? "Anonymous"
                      : `${suggestion.author_name ?? "Unknown"}${
                          suggestion.author_batch ? ` · ${suggestion.author_batch}` : ""
                        }`}
                  </span>
                  <span aria-hidden="true" className="text-ink-300">
                    /
                  </span>
                  <span className="text-xs text-ink-500">
                    {fullDate.format(new Date(suggestion.created_at))}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <label className="sr-only" htmlFor={`status-${suggestion.id}`}>
                    Change status
                  </label>
                  <select
                    id={`status-${suggestion.id}`}
                    value={suggestion.status}
                    disabled={statusMutation.isPending}
                    onChange={(e) =>
                      statusMutation.mutate({
                        id: suggestion.id,
                        status: e.target.value as SuggestionStatus,
                      })
                    }
                    className="input w-auto py-1.5 text-xs font-semibold"
                  >
                    {STATUSES.map((status) => (
                      <option key={status} value={status}>
                        {STATUS_LABEL[status]}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <p className="mt-3 max-w-[75ch] text-sm text-ink-700">{suggestion.body}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
