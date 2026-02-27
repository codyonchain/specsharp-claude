export const E2E_API_BASE_URL =
  process.env.E2E_API_BASE_URL || process.env.VITE_API_URL || "http://127.0.0.1:8001";

export const E2E_USER_TOKEN = process.env.E2E_USER_TOKEN || process.env.TOKEN_USER_A || "";

export const E2E_SECONDARY_USER_TOKEN =
  process.env.E2E_SECONDARY_USER_TOKEN || process.env.TOKEN_USER_B || "";

export const hasPrimaryToken = Boolean(E2E_USER_TOKEN);

export const hasSecondaryToken = Boolean(E2E_SECONDARY_USER_TOKEN);
