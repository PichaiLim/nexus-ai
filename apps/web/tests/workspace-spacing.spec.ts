import { expect, test, type Page } from "@playwright/test";

async function readSpacing(page: Page) {
  return page.locator("#content").evaluate(content => {
    const heading = content.querySelector(".pagehead");
    const card = content.querySelector(".card");
    if (!heading || !card) throw new Error("Expected a workspace heading and card");

    const cardStyle = getComputedStyle(card);
    return {
      contentPadding: getComputedStyle(content).padding,
      headingMargin: getComputedStyle(heading).marginBottom,
      cardPadding: cardStyle.padding,
      cardRadius: cardStyle.borderRadius,
    };
  });
}

const viewports = [
  { width: 1440, height: 900, contentPadding: "28px 30px 48px", cardPadding: "18px" },
  { width: 390, height: 844, contentPadding: "17px 12px", cardPadding: "13px" },
];

for (const { width, height, contentPadding, cardPadding } of viewports) {
  test(`workspace and Model Sources match the handoff spacing at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.goto("/demo");
    await expect(page.getByRole("heading", { name: "Overview", exact: true, level: 1 })).toBeVisible();
    const baseline = await readSpacing(page);
    expect(baseline).toEqual({ contentPadding, headingMargin: "24px", cardPadding, cardRadius: "12px" });

    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Overview", exact: true, level: 1 })).toBeVisible();
    expect(await readSpacing(page)).toEqual(baseline);

    const menu = page.getByRole("button", { name: "Open navigation" });
    if (await menu.isVisible()) await menu.click();
    await page.getByRole("button", { name: "Model Sources", exact: true }).click();
    await expect(page.getByRole("heading", { name: "Model Sources", exact: true, level: 1 })).toBeVisible();
    expect(await readSpacing(page)).toEqual(baseline);
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(width);

    const mode = page.getByRole("group", { name: "Data mode" });
    for (const name of ["Demo", "Live"]) {
      const button = mode.getByRole("button", { name, exact: true });
      const box = await button.boundingBox();
      expect(box?.width ?? 0, `${name} button width`).toBeGreaterThanOrEqual(44);
      expect(box?.height ?? 0, `${name} button height`).toBeGreaterThanOrEqual(44);
    }
  });
}
