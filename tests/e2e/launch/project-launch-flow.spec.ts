import type { Page } from "@playwright/test";
import { expect, test } from "@playwright/test";
import { createDraftPacket, confirmDecisionInputs } from "../support/new-project";
import { seedAuthenticatedSession } from "../support/session";

const escapeRegExp = (value: string): string => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const RECENT_DASHBOARD_PROJECT_TEXT = /^Updated (just now|1 minute ago)$/;

const clickNewestDashboardProject = async (page: Page) => {
  const newestProject = page.getByText(RECENT_DASHBOARD_PROJECT_TEXT).first();
  await expect(newestProject).toBeVisible({ timeout: 20_000 });
  await newestProject.click();
};

const openScenarioSettings = async (page: Page) => {
  const scenarioSettingsButton = page.getByRole("button", { name: /Scenario Settings/i });
  await expect(scenarioSettingsButton).toBeVisible();

  if ((await scenarioSettingsButton.getAttribute("aria-expanded")) !== "true") {
    await scenarioSettingsButton.click();
  }

  const stressBandSelect = page.getByLabel("Downside Stress Level");
  await expect(stressBandSelect).toBeVisible();
  return stressBandSelect;
};

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

    const stressBandSelect = await openScenarioSettings(page);
    const currentStressBand = await stressBandSelect.inputValue();
    const nextStressBand = currentStressBand === "7" ? "5" : "7";
    const dealShieldControlsUpdateResponsePromise = page.waitForResponse((response) => {
      return (
        response.request().method() === "POST" &&
        response.url().includes(`/api/v2/scope/projects/${projectId}/dealshield/controls`)
      );
    });
    const dealShieldRefreshResponsePromise = page.waitForResponse((response) => {
      return (
        response.request().method() === "GET" &&
        response.url().includes(`/api/v2/scope/projects/${projectId}/dealshield`) &&
        !response.url().includes("/pdf")
      );
    });
    const [dealShieldControlsUpdateResponse, dealShieldRefreshResponse] = await Promise.all([
      dealShieldControlsUpdateResponsePromise,
      dealShieldRefreshResponsePromise,
      stressBandSelect.selectOption(nextStressBand),
    ]);
    await expect(stressBandSelect).toHaveValue(nextStressBand);
    expect(dealShieldControlsUpdateResponse.ok()).toBeTruthy();
    expect(dealShieldRefreshResponse.ok()).toBeTruthy();

    const dealShieldControlsUpdatePayload = await dealShieldControlsUpdateResponse.json();
    expect(dealShieldControlsUpdatePayload?.success).toBeTruthy();
    expect(dealShieldControlsUpdatePayload?.data?.dealshield_controls?.stress_band_pct).toBe(
      Number(nextStressBand)
    );

    await page.reload();
    await expect(page.getByRole("heading", { name: "DealShield" })).toBeVisible();
    await expect(await openScenarioSettings(page)).toHaveValue(nextStressBand);

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

    const [executiveDownload] = await Promise.all([
      page.waitForEvent("download"),
      page.getByRole("button", { name: "Export PDF" }).click(),
    ]);
    expect(executiveDownload.suggestedFilename().toLowerCase()).toMatch(/^report_.*\.pdf$/);
    expect(await executiveDownload.failure()).toBeNull();

    await page.goto("/dashboard");
    await expect(page.getByText("Projects Dashboard")).toBeVisible();

    await clickNewestDashboardProject(page);

    await expect(page).toHaveURL(new RegExp(`/project/${escapeRegExp(projectId)}$`));
    await expect(page.getByRole("heading", { name: "DealShield" })).toBeVisible();
  });
});
