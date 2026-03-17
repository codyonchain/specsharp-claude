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

    const runLimitResponsePromise = page.waitForResponse((response) => {
      return (
        response.request().method() === "POST" &&
        response.url().includes("/api/v2/scope/generate") &&
        response.status() === 403
      );
    });
    await page.getByRole("button", { name: "Generate Decision Packet" }).click();
    const runLimitResponse = await runLimitResponsePromise;
    expect(runLimitResponse.ok()).toBeFalsy();
    await expect(page).toHaveURL(/\/new$/);
    const runLimitDialog = page.getByRole("dialog", { name: "You've used all included runs" });
    await expect(runLimitDialog).toBeVisible();
    await expect(
      runLimitDialog.getByText(
        "This org has used all included runs for Decision Packet generation. You can still analyze drafts and review existing work."
      )
    ).toBeVisible();
    await expect(runLimitDialog.getByRole("link", { name: "Email Cody to add more runs" })).toHaveAttribute(
      "href",
      /mailto:cody@specsharp\.ai/
    );
  });
});
