import { expect, test } from "@playwright/test";

test.describe("Footer/legal links + basic nav sanity", () => {
  test("homepage nav routes to coverage and login", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("link", { name: "Coverage" }).first().click();
    await expect(page).toHaveURL(/\/coverage$/);
    await expect(page.getByRole("heading", { name: /Coverage: Supported Building Types/i })).toBeVisible();

    await page.goto("/");
    await page.getByRole("link", { name: "Login" }).first().click();
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole("button", { name: "Continue with Google" })).toBeVisible();
  });

  test("footer legal links route to intended pages", async ({ page }) => {
    const footerChecks: Array<{ link: string; url: RegExp; heading: RegExp }> = [
      { link: "Terms of Service", url: /\/terms$/, heading: /Terms of Service/i },
      { link: "Privacy Policy", url: /\/privacy$/, heading: /Privacy Policy/i },
      { link: "Cookie Notice", url: /\/cookies$/, heading: /Cookie Notice/i },
      { link: "Security & Trust", url: /\/security$/, heading: /Security & Trust/i },
      { link: "Data Processing Addendum", url: /\/dpa$/, heading: /Data Processing Addendum/i },
      { link: "Subprocessor List", url: /\/subprocessors$/, heading: /Subprocessor List/i },
      { link: "FAQ", url: /\/faq$/, heading: /SpecSharp FAQ/i },
    ];

    for (const check of footerChecks) {
      await page.goto("/");
      const footer = page.locator("footer");
      await footer.scrollIntoViewIfNeeded();
      await footer.getByRole("link", { name: check.link }).click();
      await expect(page).toHaveURL(check.url);
      await expect(page.getByRole("heading", { name: check.heading })).toBeVisible();
    }
  });
});
