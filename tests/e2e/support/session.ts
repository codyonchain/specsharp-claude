import { Page } from "@playwright/test";
import { E2E_API_BASE_URL } from "./env";

const ACCESS_TOKEN_KEY = "specsharp_access_token";
const EXPIRES_AT_KEY = "specsharp_token_expires_at";
const USER_KEY = "specsharp_user";
const E2E_SESSION_SEEDED_KEY = "__specsharp_e2e_session_seeded";

type SeededSession = {
  accessToken: string;
  expiresAt: number;
  user: {
    id: string;
    email: string;
  };
};

type TestingSessionResponse = {
  success?: boolean;
  data?: {
    access_token?: string;
    expires_at?: number;
    expires_in?: number;
    user?: {
      id?: string;
      email?: string;
    };
  };
};

const base64UrlDecode = (input: string): string => {
  const normalized = input.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");
  return Buffer.from(padded, "base64").toString("utf8");
};

export const buildSessionFromJwt = (accessToken: string): SeededSession => {
  const parts = accessToken.split(".");
  if (parts.length < 2) {
    throw new Error("Invalid JWT format for E2E token");
  }

  const payload = JSON.parse(base64UrlDecode(parts[1])) as {
    sub?: string;
    email?: string;
    exp?: number;
  };

  const now = Math.floor(Date.now() / 1000);
  const expiresAt = typeof payload.exp === "number" ? payload.exp : now + 3600;

  return {
    accessToken,
    expiresAt,
    user: {
      id: payload.sub || "e2e-user",
      email: payload.email || "e2e-user@specsharp.ai",
    },
  };
};

const fetchTestingSession = async (): Promise<SeededSession> => {
  const response = await fetch(`${E2E_API_BASE_URL}/api/v2/auth/testing/session`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error(`E2E test session bootstrap failed (${response.status})`);
  }

  const payload = (await response.json()) as TestingSessionResponse;
  const data = payload?.data;
  if (!data?.access_token || !data?.user?.id || !data?.user?.email) {
    throw new Error("E2E test session bootstrap returned an invalid payload");
  }

  const now = Math.floor(Date.now() / 1000);
  const expiresAt =
    typeof data.expires_at === "number"
      ? data.expires_at
      : now + (typeof data.expires_in === "number" ? data.expires_in : 3600);

  return {
    accessToken: data.access_token,
    expiresAt,
    user: {
      id: data.user.id,
      email: data.user.email,
    },
  };
};

export const seedAuthenticatedSession = async (page: Page, accessToken?: string): Promise<void> => {
  const session =
    accessToken && accessToken.trim().length > 0
      ? buildSessionFromJwt(accessToken)
      : await fetchTestingSession();

  await page.addInitScript(
    ({ seed, seedKey }: { seed: SeededSession; seedKey: string }) => {
      try {
        if (localStorage.getItem(seedKey) === "1") {
          return;
        }
      } catch {
        // Ignore storage access failures and attempt the normal session seed.
      }

      sessionStorage.setItem("specsharp_access_token", seed.accessToken);
      sessionStorage.setItem("specsharp_token_expires_at", String(seed.expiresAt));
      sessionStorage.setItem("specsharp_user", JSON.stringify(seed.user));

      try {
        localStorage.setItem(seedKey, "1");
      } catch {
        // Ignore storage access failures; the auth seed is still valid for this document.
      }
    },
    { seed: session, seedKey: E2E_SESSION_SEEDED_KEY }
  );
};

export const clearSessionAuth = async (page: Page): Promise<void> => {
  await page.evaluate(() => {
    sessionStorage.removeItem("specsharp_access_token");
    sessionStorage.removeItem("specsharp_token_expires_at");
    sessionStorage.removeItem("specsharp_user");
    localStorage.removeItem("specsharp_access_token");
    localStorage.removeItem("specsharp_token_expires_at");
    localStorage.removeItem("specsharp_user");
    localStorage.removeItem("token");
    localStorage.removeItem("isAuthenticated");
  });
};
