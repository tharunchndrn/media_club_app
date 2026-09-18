import { apiClient } from "./client";
import type {
  AdminSuggestion,
  SuggestionCategory,
  SuggestionStatus,
} from "../types";

export interface SuggestionListParams {
  status?: SuggestionStatus;
  batch?: string;
}

export async function fetchSuggestions(
  params: SuggestionListParams = {},
): Promise<AdminSuggestion[]> {
  const { data } = await apiClient.get<AdminSuggestion[]>("/suggestions", {
    params,
  });
  return data;
}

export async function fetchSuggestionCategories(): Promise<
  SuggestionCategory[]
> {
  const { data } = await apiClient.get<SuggestionCategory[]>(
    "/suggestions/categories",
  );
  return data;
}

export async function updateSuggestionStatus(
  id: string,
  status: SuggestionStatus,
): Promise<AdminSuggestion> {
  const { data } = await apiClient.patch<AdminSuggestion>(
    `/suggestions/${id}`,
    { status },
  );
  return data;
}

// NOTE: POST /suggestions/analyse and GET /suggestions/themes do not exist
// yet (pending the TF-IDF/KMeans clustering engine) — intentionally not
// wired up here. See docs/api-contract.md.
