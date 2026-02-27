import { expect, test } from "@playwright/test";
import { hasPrimaryToken, E2E_USER_TOKEN } from "../support/env";
import { clearSessionAuth, seedAuthenticatedSession } from "../support/session";

test.describe("Login/logout + session persistence", () => {
  test("renders login screen with Google entry point", async ({ page }) => {
    await page.goto("/login");

    await expect(page.getByRole("heading", { name: "Welcome Back" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Continue with Google" })).toBeVisible();
  });

  test("keeps user authenticated across refresh and blocks dashboard after logout", async ({ page }) => {
    test.skip(!hasPrimaryToken, "Set E2E_USER_TOKEN to run authenticated session tests");

    await seedAuthenticatedSession(page, E2E_USER_TOKEN);
    await page.goto("/dashboard");
    await expect(page.getByText("Projects Dashboard")).toBeVisible();

    await page.reload();
    await expect(page.getByText("Projects Dashboard")).toBeVisible();

    // V2 dashboard has no explicit sign-out button yet; this emulates logout by clearing auth session.
    await clearSessionAuth(page);
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login$/);
  });
});
