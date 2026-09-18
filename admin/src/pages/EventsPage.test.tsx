import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { EventsPage } from "./EventsPage";
import { renderWithProviders } from "../test/utils";
import * as eventsApi from "../api/events";
import type { EventSummary } from "../types";

vi.mock("../api/events");

const sampleEvent: EventSummary = {
  id: "e1",
  title: "Inter-Batch Photowalk",
  slug: "inter-batch-photowalk",
  description: "A walk around campus",
  venue: "Main lawn",
  event_date: "2026-10-15T09:00:00Z",
  cover_image_url: null,
  status: "published",
  academic_year: "2025/2026",
  created_at: "2026-09-01T00:00:00Z",
};

describe("EventsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("lists events fetched from the API", async () => {
    vi.mocked(eventsApi.fetchEvents).mockImplementation(async (params) => {
      if (params?.status === "draft") return [];
      return [sampleEvent];
    });

    renderWithProviders(<EventsPage />);

    await waitFor(() => {
      expect(screen.getByText("Inter-Batch Photowalk")).toBeInTheDocument();
    });
  });

  it("creates a new event via the form", async () => {
    vi.mocked(eventsApi.fetchEvents).mockResolvedValue([]);
    vi.mocked(eventsApi.createEvent).mockResolvedValue({
      ...sampleEvent,
      id: "e2",
      title: "New Event",
    });

    renderWithProviders(<EventsPage />);

    await userEvent.click(
      screen.getByRole("button", { name: /new event/i }),
    );

    await userEvent.type(screen.getByLabelText(/title/i), "New Event");
    await userEvent.type(screen.getByLabelText(/venue/i), "Auditorium");
    await userEvent.type(
      screen.getByLabelText(/^academic year$/i),
      "2025/2026",
    );
    await userEvent.type(
      screen.getByLabelText(/description/i),
      "Details about the event",
    );

    const dateInput = screen.getByLabelText(/event date/i);
    await userEvent.type(dateInput, "2026-11-01T10:00");

    await userEvent.click(
      screen.getByRole("button", { name: /create event/i }),
    );

    await waitFor(() => {
      expect(eventsApi.createEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          title: "New Event",
          venue: "Auditorium",
          academic_year: "2025/2026",
        }),
      );
    });
  });
});
