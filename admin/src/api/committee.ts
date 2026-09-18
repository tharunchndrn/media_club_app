import { apiClient } from "./client";
import type { CommitteeMember, CommitteeMemberCreateInput } from "../types";

export async function fetchCommitteeYears(): Promise<string[]> {
  const { data } = await apiClient.get<string[]>("/committee/years");
  return data;
}

export async function fetchCommitteeMembers(
  year?: string,
): Promise<CommitteeMember[]> {
  const { data } = await apiClient.get<CommitteeMember[]>("/committee", {
    params: year ? { year } : undefined,
  });
  return data;
}

export async function createCommitteeMember(
  input: CommitteeMemberCreateInput,
): Promise<CommitteeMember> {
  const { data } = await apiClient.post<CommitteeMember>(
    "/committee",
    input,
  );
  return data;
}

export async function deleteCommitteeMember(id: string): Promise<void> {
  await apiClient.delete(`/committee/${id}`);
}

// NOTE: there is no PATCH /committee/{id} endpoint on the backend yet, so
// editing an existing member is not possible from this admin UI. Flagged as
// a contract gap; do not invent an update call that doesn't exist.
