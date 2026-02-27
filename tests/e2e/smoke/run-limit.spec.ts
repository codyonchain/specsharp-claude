import { expect, test } from "@playwright/test";
import { E2E_USER_TOKEN, hasPrimaryToken } from "../support/env";
import { seedAuthenticatedSession } from "../support/session";

test.describe("Run-limit reached UI", () => {
  test("shows run-limit message when backend returns run_limit_reached", async ({ page }) => {
    test.skip(!hasPrimaryToken, "Set E2E_USER_TOKEN to run authenticated run-limit UI checks");

    await seedAuthenticatedSession(page, E2E_USER_TOKEN);
    await page.goto("/new");

    await page.getByPlaceholder("Start with: [Size] [Type] in [Location]...").fill(
      "New 80,000 sf neighborhood retail center in Nashville, TN"
    );
    await page.getByPlaceholder("City, ST (e.g., Dallas, TX)").fill("Nashville, TN");
    await page.getByRole("button", { name: "Generate Draft Packet" }).click();

    await expect(page.getByText("Draft Ready - Confirm Decision Inputs")).toBeVisible();

    const confirmationCheckbox = page.locator('label:has-text("I confirm these inputs reflect the basis of this decision.") input[type="checkbox"]');
    await confirmationCheckbox.check();

    await page.route("**/api/v2/scope/generate", async (route) => {
      await route.fulfill({
        status: 403,
        contentType: "application/json",
        body: JSON.stringify({
          detail: {
            message: "Run limit reached. Call Cody to add more runs.",
            code: "run_limit_reached",
          },
        }),
      });
    });

    await page.getByRole("button", { name: "Generate Decision Packet" }).click();
    await expect(page.getByText("Run limit reached. Call Cody to add more runs.")).toBeVisible();
  });
});
