import { expect, test } from "@playwright/test";
import { createDraftPacket, confirmDecisionInputs } from "../support/new-project";
import { seedAuthenticatedSession } from "../support/session";

test.describe("Launch run-limit gating", () => {
  test("shows the run-limit blocker when save returns run_limit_reached", async ({ page }) => {
    test.setTimeout(90_000);

    await seedAuthenticatedSession(page);
    await createDraftPacket(page, {
      description: "Launch run limit 80,000 sf neighborhood retail center in Nashville, TN",
      squareFootage: 80000,
      location: "Nashville, TN",
    });
    await confirmDecisionInputs(page);

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
