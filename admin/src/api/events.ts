import { apiClient } from "./client";
import type {
  EventCreateInput,
  EventDetail,
  EventSummary,
  EventUpdateInput,
  Photo,
  PhotoCreateInput,
} from "../types";

export interface EventListParams {
  year?: string;
  status?: string;
}

export async function fetchEvents(
  params: EventListParams = {},
): Promise<EventSummary[]> {
  const { data } = await apiClient.get<EventSummary[]>("/events", { params });
  return data;
}

export async function fetchEvent(id: string): Promise<EventDetail> {
  const { data } = await apiClient.get<EventDetail>(`/events/${id}`);
  return data;
}

export async function createEvent(
  input: EventCreateInput,
): Promise<EventSummary> {
  const { data } = await apiClient.post<EventSummary>("/events", input);
  return data;
}

export async function updateEvent(
  id: string,
  input: EventUpdateInput,
): Promise<EventSummary> {
  const { data } = await apiClient.patch<EventSummary>(
    `/events/${id}`,
    input,
  );
  return data;
}

export async function deleteEvent(id: string): Promise<void> {
  await apiClient.delete(`/events/${id}`);
}

export async function addPhoto(
  eventId: string,
  input: PhotoCreateInput,
): Promise<Photo> {
  const { data } = await apiClient.post<Photo>(
    `/events/${eventId}/photos`,
    input,
  );
  return data;
}

export async function deletePhoto(
  eventId: string,
  photoId: string,
): Promise<void> {
  await apiClient.delete(`/events/${eventId}/photos/${photoId}`);
}
