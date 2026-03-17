import { expect, Page } from "@playwright/test";

type DraftProjectInput = {
  description: string;
  squareFootage: number;
  location: string;
};

export const createDraftPacket = async (
  page: Page,
  { description, squareFootage, location }: DraftProjectInput
): Promise<void> => {
  await page.goto("/new");

  await page.getByPlaceholder("Start with: [Size] [Type] in [Location]...").fill(description);
  await page.getByPlaceholder("e.g. 50,000").fill(String(squareFootage));
  await page.getByPlaceholder("City, ST (e.g., Dallas, TX)").fill(location);

  await page.getByRole("button", { name: "Generate Draft Packet" }).click();

  await expect(page.getByRole("heading", { name: "Draft Ready - Confirm Decision Inputs" })).toBeVisible({
    timeout: 20_000,
  });
  await expect(page.getByRole("heading", { name: "Decision Inputs (Stamped)" })).toBeVisible();
  await expect(page.locator("p", { hasText: /^Project Type$/ })).toBeVisible();
  await expect(page.locator("p", { hasText: /^Finish Level$/ })).toBeVisible();
  await expect(page.locator("p", { hasText: /^Special Features$/ })).toBeVisible();
  await expect(page.locator("p", { hasText: /^Total Project Cost$/ })).toBeVisible();
};

export const confirmDecisionInputs = async (page: Page): Promise<void> => {
  await page.getByRole("button", { name: "Renovation" }).click();
  await page.getByRole("button", { name: "Premium" }).click();

  const confirmationCheckbox = page.locator(
    'label:has-text("I confirm these inputs reflect the basis of this decision.") input[type="checkbox"]'
  );
  await confirmationCheckbox.check();
  await expect(confirmationCheckbox).toBeChecked();
};
