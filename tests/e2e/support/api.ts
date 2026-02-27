import { APIRequestContext } from "@playwright/test";
import { E2E_API_BASE_URL } from "./env";

export type CreatedProject = {
  projectId: string;
  raw: unknown;
};

export const createProjectViaApi = async (
  request: APIRequestContext,
  token: string,
  payload?: {
    description?: string;
    location?: string;
    square_footage?: number;
    special_features?: string[];
  }
): Promise<CreatedProject> => {
  const response = await request.post(`${E2E_API_BASE_URL}/api/v2/scope/generate`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    data: {
      description:
        payload?.description ||
        "New 95,000 sf neighborhood shopping center with inline suites in Nashville, TN",
      location: payload?.location || "Nashville, TN",
      square_footage: payload?.square_footage,
      special_features: payload?.special_features || [],
    },
  });

  const body = await response.json();
  if (!response.ok()) {
    throw new Error(
      `scope/generate failed (${response.status()}): ${JSON.stringify(body).slice(0, 500)}`
    );
  }

  const data = body?.data || body;
  const projectId = data?.project_id || data?.id;
  if (!projectId) {
    throw new Error(`scope/generate returned no project id: ${JSON.stringify(body).slice(0, 500)}`);
  }

  return {
    projectId,
    raw: body,
  };
};
