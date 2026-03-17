import { expect, test } from "@playwright/test";
import { createDraftPacket, confirmDecisionInputs } from "../support/new-project";
import { seedAuthenticatedSession } from "../support/session";

const escapeRegExp = (value: string): string => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

test.describe("Launch project flow", () => {
  test("creates a project from /new, reopens it from the dashboard, and exports launch packets", async ({ page }) => {
    test.setTimeout(120_000);

    const projectMarker = `LaunchFlow ${Date.now()}`;
    const description = `${projectMarker} 140,000 SF warehouse with 24 dock doors in Nashville, TN`;

    await seedAuthenticatedSession(page);
    await createDraftPacket(page, {
      description,
      squareFootage: 140000,
      location: "Nashville, TN",
    });
    await confirmDecisionInputs(page);

    const generateButton = page.getByRole("button", { name: "Generate Decision Packet" });
    await expect(generateButton).toBeEnabled();

    await Promise.all([
      page.waitForURL(/\/project\/[^/]+$/, { timeout: 60_000 }),
      generateButton.click(),
    ]);

    const projectId = page.url().split("/project/")[1];
    await expect(page.getByRole("heading", { name: "DealShield" })).toBeVisible();

    const stressBandSelect = page.getByLabel("Downside Stress Level");
    const currentStressBand = await stressBandSelect.inputValue();
    const nextStressBand = currentStressBand === "7" ? "5" : "7";
    await stressBandSelect.selectOption(nextStressBand);
    await expect(stressBandSelect).toHaveValue(nextStressBand);
    await expect(page.getByText("Updating DealShield scenarios...")).toBeVisible();
    await expect(page.getByText("Updating DealShield scenarios...")).not.toBeVisible({ timeout: 20_000 });

    await page.reload();
    await expect(page.getByRole("heading", { name: "DealShield" })).toBeVisible();
    await expect(page.getByLabel("Downside Stress Level")).toHaveValue(nextStressBand);

    const dealShieldExportResponsePromise = page.waitForResponse((response) => {
      return (
        response.request().method() === "GET" &&
        response.url().includes(`/api/v2/pdf/project/${projectId}/pdf`)
      );
    });
    await page.getByRole("button", { name: "Export PDF" }).click();
    const dealShieldExportResponse = await dealShieldExportResponsePromise;
    expect(dealShieldExportResponse.ok()).toBeTruthy();
    expect(dealShieldExportResponse.headers()["content-type"] || "").toContain("application/pdf");

    await page.getByRole("button", { name: "Executive View" }).click();
    await expect(page.getByRole("button", { name: "Export PDF" })).toBeVisible();

    const executiveExportResponsePromise = page.waitForResponse((response) => {
      return (
        response.request().method() === "GET" &&
        response.url().includes(`/api/v2/pdf/project/${projectId}/pdf`)
      );
    });
    await page.getByRole("button", { name: "Export PDF" }).click();
    const executiveExportResponse = await executiveExportResponsePromise;
    expect(executiveExportResponse.ok()).toBeTruthy();
    expect(executiveExportResponse.headers()["content-type"] || "").toContain("application/pdf");

    await page.goto("/dashboard");
    await expect(page.getByText("Projects Dashboard")).toBeVisible();

    const projectHeading = page.getByRole("heading", {
      name: new RegExp(escapeRegExp(projectMarker)),
    }).first();
    await expect(projectHeading).toBeVisible({ timeout: 20_000 });
    await projectHeading.click();

    await expect(page).toHaveURL(new RegExp(`/project/${escapeRegExp(projectId)}$`));
    await expect(page.getByRole("heading", { name: "DealShield" })).toBeVisible();
  });
});
