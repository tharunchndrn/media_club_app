import { useState, type FormEvent, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createCommitteeMember,
  deleteCommitteeMember,
  fetchCommitteeMembers,
  fetchCommitteeYears,
} from "../api/committee";
import { ErrorBanner } from "../components/ErrorBanner";
import { PageHeader } from "../components/PageHeader";
import { getErrorMessage } from "../api/client";
import type { CommitteeMemberCreateInput } from "../types";

const emptyForm: CommitteeMemberCreateInput = {
  name: "",
  position: "",
  academic_year: "",
  photo_url: null,
  linkedin_url: null,
  sort_order: 0,
};

export function CommitteePage() {
  const queryClient = useQueryClient();
  const [selectedYear, setSelectedYear] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<CommitteeMemberCreateInput>(emptyForm);
  const [formError, setFormError] = useState<string | null>(null);

  const yearsQuery = useQuery({
    queryKey: ["committee-years"],
    queryFn: fetchCommitteeYears,
  });

  const activeYear = selectedYear ?? yearsQuery.data?.[0] ?? null;

  const membersQuery = useQuery({
    queryKey: ["committee-members", activeYear],
    queryFn: () => fetchCommitteeMembers(activeYear ?? undefined),
    enabled: Boolean(activeYear),
  });

  const createMutation = useMutation({
    mutationFn: (input: CommitteeMemberCreateInput) => createCommitteeMember(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["committee-members"] });
      queryClient.invalidateQueries({ queryKey: ["committee-years"] });
      setForm(emptyForm);
      setShowForm(false);
      setFormError(null);
    },
    onError: (err) => setFormError(getErrorMessage(err)),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteCommitteeMember(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["committee-members"] });
    },
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setFormError(null);
    createMutation.mutate(form);
  }

  const years = yearsQuery.data ?? [];
  const members = membersQuery.data ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Committee"
        description="The people running the club, grouped by academic year. Students see this list in the app."
        actions={
          <button
            type="button"
            onClick={() => setShowForm((v) => !v)}
            className={showForm ? "btn-secondary" : "btn-primary"}
          >
            {showForm ? "Cancel" : "Add member"}
          </button>
        }
      />

      {showForm ? (
        <form onSubmit={handleSubmit} className="panel space-y-4 p-6">
          <h2 className="text-lg font-semibold text-ink-900">Add a member</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Name">
              <input
                required
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                className="input"
                placeholder="Full name"
              />
            </Field>
            <Field label="Position">
              <input
                required
                value={form.position}
                onChange={(e) => setForm((f) => ({ ...f, position: e.target.value }))}
                className="input"
                placeholder="President"
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
            <Field label="LinkedIn URL" hint="Optional.">
              <input
                type="url"
                value={form.linkedin_url ?? ""}
                onChange={(e) =>
                  setForm((f) => ({ ...f, linkedin_url: e.target.value || null }))
                }
                className="input"
                placeholder="https://linkedin.com/in/"
              />
            </Field>
            <div className="sm:col-span-2">
              <Field label="Photo URL" hint="Optional. Paste a link from Cloudinary, R2 or Drive.">
                <input
                  type="url"
                  value={form.photo_url ?? ""}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, photo_url: e.target.value || null }))
                  }
                  className="input"
                  placeholder="https://"
                />
              </Field>
            </div>
          </div>
          <ErrorBanner message={formError} />
          <button type="submit" disabled={createMutation.isPending} className="btn-primary">
            {createMutation.isPending ? "Adding…" : "Add member"}
          </button>
        </form>
      ) : null}

      {years.length > 0 ? (
        <div>
          <p className="field-label">Academic year</p>
          <div className="flex flex-wrap gap-2">
            {years.map((year) => {
              const isActive = year === activeYear;
              return (
                <button
                  key={year}
                  type="button"
                  aria-pressed={isActive}
                  onClick={() => setSelectedYear(year)}
                  className={`rounded-control border px-3.5 py-1.5 text-sm font-semibold transition-colors
                    focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-navy-600 ${
                      isActive
                        ? "border-navy-600 bg-navy-600 text-white"
                        : "border-ink-200 bg-white text-ink-600 hover:border-ink-300 hover:text-navy-700"
                    }`}
                >
                  {year}
                </button>
              );
            })}
          </div>
        </div>
      ) : null}

      {membersQuery.error ? (
        <ErrorBanner message={getErrorMessage(membersQuery.error)} />
      ) : null}

      {/* No PATCH /committee/{id} endpoint exists yet, so members cannot be
          edited from this UI — only added and removed. */}

      {membersQuery.isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="skeleton h-[104px]" />
          ))}
        </div>
      ) : members.length === 0 ? (
        <div className="empty-state">
          <p className="font-semibold text-ink-900">No members listed</p>
          <p className="mt-1 text-sm text-ink-600">
            {activeYear
              ? `Nobody is recorded for ${activeYear} yet.`
              : "Add the first committee member to start the roster."}
          </p>
        </div>
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {members.map((member) => (
            <li key={member.id} className="panel group flex flex-col gap-4 p-4">
              <div className="flex items-center gap-3">
                {member.photo_url ? (
                  <img
                    src={member.photo_url}
                    alt=""
                    loading="lazy"
                    className="h-12 w-12 shrink-0 rounded-full object-cover"
                  />
                ) : (
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-navy-100 font-display text-base font-bold text-navy-700">
                    {member.name.trim().charAt(0).toUpperCase()}
                  </div>
                )}
                <div className="min-w-0">
                  <p className="truncate font-semibold text-ink-900">{member.name}</p>
                  <p className="truncate text-sm text-ink-600">{member.position}</p>
                </div>
              </div>
              <div className="mt-auto flex items-center justify-between border-t border-ink-100 pt-3">
                {member.linkedin_url ? (
                  <a
                    href={member.linkedin_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-sm font-semibold text-navy-600 hover:underline"
                  >
                    LinkedIn
                  </a>
                ) : (
                  <span className="text-sm text-ink-400">No LinkedIn</span>
                )}
                <button
                  type="button"
                  onClick={() => {
                    if (confirm(`Remove ${member.name} from the committee?`)) {
                      deleteMutation.mutate(member.id);
                    }
                  }}
                  className="btn-danger"
                >
                  Remove
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
