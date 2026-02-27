import { Page } from "@playwright/test";

const ACCESS_TOKEN_KEY = "specsharp_access_token";
const EXPIRES_AT_KEY = "specsharp_token_expires_at";
const USER_KEY = "specsharp_user";

type SeededSession = {
  accessToken: string;
  expiresAt: number;
  user: {
    id: string;
    email: string;
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

export const seedAuthenticatedSession = async (page: Page, accessToken: string): Promise<void> => {
  const session = buildSessionFromJwt(accessToken);

  await page.addInitScript((seed: SeededSession) => {
    sessionStorage.setItem("specsharp_access_token", seed.accessToken);
    sessionStorage.setItem("specsharp_token_expires_at", String(seed.expiresAt));
    sessionStorage.setItem("specsharp_user", JSON.stringify(seed.user));
  }, session);
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
