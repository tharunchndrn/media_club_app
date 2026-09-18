import { useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { addPhoto, deletePhoto, fetchEvent, updateEvent } from "../api/events";
import { ErrorBanner } from "../components/ErrorBanner";
import { getErrorMessage } from "../api/client";
import type { PhotoCreateInput } from "../types";

const emptyPhotoForm: PhotoCreateInput = {
  image_url: "",
  thumb_url: null,
  caption: null,
  alt_text: null,
};

const fullDateTime = new Intl.DateTimeFormat(undefined, {
  dateStyle: "medium",
  timeStyle: "short",
});

export function EventDetailPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [photoForm, setPhotoForm] = useState<PhotoCreateInput>(emptyPhotoForm);
  const [photoError, setPhotoError] = useState<string | null>(null);

  const eventQuery = useQuery({
    queryKey: ["events", id],
    queryFn: () => fetchEvent(id as string),
    enabled: Boolean(id),
  });

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["events", id] });

  const addPhotoMutation = useMutation({
    mutationFn: (input: PhotoCreateInput) => addPhoto(id as string, input),
    onSuccess: () => {
      invalidate();
      setPhotoForm(emptyPhotoForm);
      setPhotoError(null);
    },
    onError: (err) => setPhotoError(getErrorMessage(err)),
  });

  const deletePhotoMutation = useMutation({
    mutationFn: (photoId: string) => deletePhoto(id as string, photoId),
    onSuccess: invalidate,
  });

  const setCoverMutation = useMutation({
    mutationFn: (imageUrl: string) =>
      updateEvent(id as string, { cover_image_url: imageUrl }),
    onSuccess: invalidate,
  });

  function handlePhotoSubmit(event: FormEvent) {
    event.preventDefault();
    setPhotoError(null);
    addPhotoMutation.mutate(photoForm);
  }

  if (eventQuery.isLoading) {
    return (
      <div className="space-y-6">
        <div className="skeleton h-10 w-64" />
        <div className="skeleton h-64" />
      </div>
    );
  }

  if (eventQuery.error || !eventQuery.data) {
    return <ErrorBanner message={getErrorMessage(eventQuery.error)} />;
  }

  const event = eventQuery.data;

  return (
    <div className="space-y-8">
      <div>
        <Link
          to="/events"
          className="text-sm font-semibold text-navy-600 hover:underline"
        >
          ← All events
        </Link>

        <div className="mt-3 flex flex-wrap items-start justify-between gap-4 border-b border-ink-200 pb-5">
          <div className="min-w-0">
            <h1 className="text-2xl font-bold text-ink-900 sm:text-3xl">
              {event.title}
            </h1>
            <p className="mt-1 text-sm text-ink-600">
              {fullDateTime.format(new Date(event.event_date))} · {event.venue} ·{" "}
              {event.academic_year}
            </p>
          </div>
          <span className={event.status === "published" ? "chip-ok" : "chip-neutral"}>
            {event.status === "published" ? "Published" : "Draft"}
          </span>
        </div>

        {event.description ? (
          <p className="mt-5 max-w-[70ch] text-ink-700">{event.description}</p>
        ) : null}
      </div>

      <section>
        <div className="mb-3 flex items-end justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-ink-900">Gallery</h2>
            <p className="text-xs text-ink-500">
              {event.photos.length} {event.photos.length === 1 ? "photo" : "photos"}
            </p>
          </div>
        </div>

        {/* Photos are shown in a fixed order by sort_order. There is no
            reorder endpoint on the backend (POST only appends, DELETE only
            removes), so drag-to-reorder is intentionally not implemented. */}
        {event.photos.length === 0 ? (
          <div className="empty-state">
            <p className="font-semibold text-ink-900">No photos yet</p>
            <p className="mt-1 text-sm text-ink-600">
              Add an image URL below to start the gallery.
            </p>
          </div>
        ) : (
          <ul className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            {event.photos.map((photo) => {
              const isCover = event.cover_image_url === photo.image_url;
              return (
                <li key={photo.id} className="panel flex flex-col overflow-hidden">
                  <div className="relative">
                    <img
                      src={photo.thumb_url ?? photo.image_url}
                      alt={photo.alt_text ?? ""}
                      loading="lazy"
                      className="h-32 w-full object-cover"
                    />
                    {isCover && (
                      <span className="absolute top-2 left-2 rounded-full bg-gold-500 px-2 py-0.5 text-xs font-bold text-navy-950">
                        Cover
                      </span>
                    )}
                  </div>
                  <div className="flex flex-1 flex-col gap-2 p-3">
                    {photo.caption ? (
                      <p className="truncate text-xs text-ink-600">{photo.caption}</p>
                    ) : null}
                    <div className="mt-auto flex items-center justify-between gap-2">
                      {isCover ? (
                        <span className="text-xs text-ink-400">Cover image</span>
                      ) : (
                        <button
                          type="button"
                          onClick={() => setCoverMutation.mutate(photo.image_url)}
                          disabled={setCoverMutation.isPending}
                          className="btn-quiet"
                        >
                          Set as cover
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => {
                          if (confirm("Delete this photo?")) {
                            deletePhotoMutation.mutate(photo.id);
                          }
                        }}
                        className="btn-danger"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}

        <form onSubmit={handlePhotoSubmit} className="panel mt-6 p-5">
          <h3 className="text-base font-semibold text-ink-900">Add a photo</h3>
          <p className="mt-0.5 text-xs text-ink-500">
            Paste a hosted image URL. Use a web-sized image, not the original.
          </p>
          <div className="mt-4 flex flex-wrap items-end gap-3">
            <label className="min-w-[220px] flex-[2] text-sm">
              <span className="field-label">Image URL</span>
              <input
                required
                type="url"
                value={photoForm.image_url}
                onChange={(e) =>
                  setPhotoForm((f) => ({ ...f, image_url: e.target.value }))
                }
                className="input"
                placeholder="https://"
              />
            </label>
            <label className="min-w-[160px] flex-1 text-sm">
              <span className="field-label">Caption</span>
              <input
                value={photoForm.caption ?? ""}
                onChange={(e) =>
                  setPhotoForm((f) => ({ ...f, caption: e.target.value || null }))
                }
                className="input"
                placeholder="Optional"
              />
            </label>
            <button
              type="submit"
              disabled={addPhotoMutation.isPending}
              className="btn-primary"
            >
              {addPhotoMutation.isPending ? "Adding…" : "Add photo"}
            </button>
          </div>
          <div className="mt-3">
            <ErrorBanner message={photoError} />
          </div>
        </form>
      </section>
    </div>
  );
}
