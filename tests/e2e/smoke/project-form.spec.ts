import { expect, test } from "@playwright/test";
import { E2E_USER_TOKEN, hasPrimaryToken } from "../support/env";
import { seedAuthenticatedSession } from "../support/session";

test.describe("Create project + key form interactions", () => {
  test("fills key inputs, confirms assumptions, and enables packet generation", async ({ page }) => {
    test.skip(!hasPrimaryToken, "Set E2E_USER_TOKEN to run authenticated project flow");

    await seedAuthenticatedSession(page, E2E_USER_TOKEN);
    await page.goto("/new");

    await page.getByPlaceholder("Start with: [Size] [Type] in [Location]...").fill(
      "New 120,000 sf medical office building with imaging suite and structured parking in Nashville, TN"
    );
    await page.getByPlaceholder("e.g. 50,000").fill("120000");
    await page.getByPlaceholder("City, ST (e.g., Dallas, TX)").fill("Nashville, TN");

    await page.getByRole("button", { name: "Generate Draft Packet" }).click();

    await expect(page.getByText("Draft Ready - Confirm Decision Inputs")).toBeVisible();
    await expect(page.getByText("Decision Inputs (Stamped)")).toBeVisible();

    await page.getByRole("button", { name: "Renovation" }).click();
    await page.getByRole("button", { name: "Premium" }).click();

    const firstFeatureCheckbox = page.locator('input[type="checkbox"]').nth(1);
    if (await firstFeatureCheckbox.isVisible()) {
      await firstFeatureCheckbox.check();
      await expect(firstFeatureCheckbox).toBeChecked();
    }

    const confirmationCheckbox = page.locator('label:has-text("I confirm these inputs reflect the basis of this decision.") input[type="checkbox"]');
    await confirmationCheckbox.check();
    await expect(confirmationCheckbox).toBeChecked();

    await expect(page.getByRole("button", { name: "Generate Decision Packet" })).toBeEnabled();
  });
});
