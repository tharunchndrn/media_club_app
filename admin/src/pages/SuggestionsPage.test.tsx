import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SuggestionsPage } from "./SuggestionsPage";
import { renderWithProviders } from "../test/utils";
import * as suggestionsApi from "../api/suggestions";
import type { AdminSuggestion } from "../types";

vi.mock("../api/suggestions");

const sampleSuggestion: AdminSuggestion = {
  id: "s1",
  category: "event-idea",
  body: "Host an inter-batch quiz on photography basics.",
  status: "new",
  theme_id: null,
  theme_label: null,
  sentiment: null,
  is_anonymous: false,
  created_at: "2026-09-01T00:00:00Z",
  author_name: "Kasun Silva",
  author_batch: "2023/2024",
};

const anonymousSuggestion: AdminSuggestion = {
  ...sampleSuggestion,
  id: "s2",
  is_anonymous: true,
  author_name: null,
  author_batch: null,
  body: "Please cover the upcoming hackathon.",
};

describe("SuggestionsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("lists suggestions and respects anonymity", async () => {
    vi.mocked(suggestionsApi.fetchSuggestions).mockResolvedValue([
      sampleSuggestion,
      anonymousSuggestion,
    ]);

    renderWithProviders(<SuggestionsPage />);

    await waitFor(() => {
      expect(screen.getByText(/Kasun Silva/)).toBeInTheDocument();
    });
    expect(screen.getByText(/Anonymous/)).toBeInTheDocument();
  });

  it("updates a suggestion's status", async () => {
    vi.mocked(suggestionsApi.fetchSuggestions).mockResolvedValue([
      sampleSuggestion,
    ]);
    vi.mocked(suggestionsApi.updateSuggestionStatus).mockResolvedValue({
      ...sampleSuggestion,
      status: "reviewing",
    });

    renderWithProviders(<SuggestionsPage />);

    const item = await screen.findByText(sampleSuggestion.body);
    const card = item.closest("li") as HTMLElement;
    const select = within(card).getByRole("combobox");

    await userEvent.selectOptions(select, "reviewing");

    await waitFor(() => {
      expect(suggestionsApi.updateSuggestionStatus).toHaveBeenCalledWith(
        "s1",
        "reviewing",
      );
    });
  });
});
