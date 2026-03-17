import { expect, test } from "@playwright/test";
import { E2E_USER_TOKEN, hasPrimaryToken } from "../support/env";
import { seedAuthenticatedSession } from "../support/session";

test.describe("Launch auth + dashboard", () => {
  test("renders login and protects the dashboard when unauthenticated", async ({ page }) => {
    await page.goto("/login");

    await expect(page.getByRole("heading", { name: "Welcome Back" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Continue with Google" })).toBeVisible();

    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login$/);
  });

  test("loads the dashboard for an authenticated user and supports logout", async ({ page }) => {
    test.skip(!hasPrimaryToken, "Set E2E_USER_TOKEN to run authenticated launch tests");

    await seedAuthenticatedSession(page, E2E_USER_TOKEN);
    await page.goto("/dashboard");

    await expect(page.getByText("Projects Dashboard")).toBeVisible();

    await page.reload();
    await expect(page.getByText("Projects Dashboard")).toBeVisible();

    await page.getByRole("button", { name: "Logout" }).click();
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole("heading", { name: "Welcome Back" })).toBeVisible();

    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login$/);
  });
});
