// Wire types mirror the backend's snake_case JSON exactly (see docs/api-contract.md).

export type EventStatus = "draft" | "published";

export interface Photo {
  id: string;
  event_id: string;
  image_url: string;
  thumb_url: string | null;
  caption: string | null;
  alt_text: string | null;
  sort_order: number;
}

export interface EventSummary {
  id: string;
  title: string;
  slug: string;
  description: string;
  venue: string;
  event_date: string;
  cover_image_url: string | null;
  status: EventStatus;
  academic_year: string;
  created_at: string;
}

export interface EventDetail extends EventSummary {
  photos: Photo[];
}

export interface EventCreateInput {
  title: string;
  description: string;
  venue: string;
  event_date: string;
  academic_year: string;
  cover_image_url?: string | null;
  status?: EventStatus;
}

export type EventUpdateInput = Partial<EventCreateInput>;

export interface PhotoCreateInput {
  image_url: string;
  thumb_url?: string | null;
  caption?: string | null;
  alt_text?: string | null;
  sort_order?: number | null;
}

export interface CommitteeMember {
  id: string;
  name: string;
  position: string;
  academic_year: string;
  photo_url: string | null;
  linkedin_url: string | null;
  sort_order: number;
}

export type CommitteeMemberCreateInput = Omit<CommitteeMember, "id"> & {
  sort_order?: number;
};

export type SuggestionCategory =
  | "event-idea"
  | "coverage-request"
  | "design-request"
  | "workshop-request"
  | "collaboration"
  | "equipment"
  | "feedback"
  | "complaint"
  | "other";

export type SuggestionStatus = "new" | "reviewing" | "planned" | "declined";

export interface AdminSuggestion {
  id: string;
  category: SuggestionCategory;
  body: string;
  status: SuggestionStatus;
  theme_id: string | null;
  theme_label: string | null;
  sentiment: number | null;
  is_anonymous: boolean;
  created_at: string;
  author_name: string | null;
  author_batch: string | null;
}

export interface ApiErrorBody {
  detail: string | Array<{ msg: string; loc?: (string | number)[] }>;
}
