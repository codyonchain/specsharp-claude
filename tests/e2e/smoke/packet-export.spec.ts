import { expect, test } from "@playwright/test";
import { createProjectViaApi } from "../support/api";
import { E2E_USER_TOKEN, hasPrimaryToken } from "../support/env";
import { seedAuthenticatedSession } from "../support/session";

test.describe("Generate packet + export/download", () => {
  test("opens DealShield and exports PDF artifacts", async ({ page, request }) => {
    test.skip(!hasPrimaryToken, "Set E2E_USER_TOKEN to run authenticated export flow");

    const { projectId } = await createProjectViaApi(request, E2E_USER_TOKEN);

    await seedAuthenticatedSession(page, E2E_USER_TOKEN);
    await page.goto(`/project/${projectId}`);

    await expect(page.getByRole("button", { name: "DealShield" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Export DealShield PDF" })).toBeVisible();

    const [dealShieldDownload] = await Promise.all([
      page.waitForEvent("download"),
      page.getByRole("button", { name: "Export DealShield PDF" }).click(),
    ]);
    expect(dealShieldDownload.suggestedFilename().toLowerCase()).toContain("dealshield");

    await page.getByRole("button", { name: "Executive View" }).click();
    await expect(page.getByRole("button", { name: "Export PDF" })).toBeVisible();

    const [executiveDownload] = await Promise.all([
      page.waitForEvent("download"),
      page.getByRole("button", { name: "Export PDF" }).click(),
    ]);
    expect(executiveDownload.suggestedFilename().toLowerCase()).toContain(".pdf");
  });
});
