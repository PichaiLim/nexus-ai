import { expect, test } from "@playwright/test";

test("Demo stays offline and Live reports each source independently", async ({ page }) => {
  const requests: string[] = [];
  const pending = { status: "pending", models: [], error: null, synced_at: null };
  const ollama = { id: "ollama", name: "Local Ollama", engine: "ollama", url: "http://127.0.0.1:11434", snapshot: pending };
  const lm = { id: "lm", name: "Local LM Studio", engine: "lm-studio", url: "http://127.0.0.1:1234", snapshot: pending };

  await page.route("**/api/v1/model-sources**", async route => {
    const path = new URL(route.request().url()).pathname;
    requests.push(path);
    if (path.endsWith("/ollama/sync")) {
      await route.fulfill({ json: { ...ollama, snapshot: {
        ...pending, status: "ready",
        models: [{ id: "actual-id", name: "Local model", installed: true, loaded: false, served: null }],
      } } });
    } else if (path.endsWith("/lm/sync")) {
      await route.fulfill({ json: { ...lm, snapshot: { ...pending, status: "unreachable", error: "Source is unreachable" } } });
    } else {
      await route.fulfill({ json: [ollama, lm] });
    }
  });

  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1, name: "Overview" })).toBeVisible();
  await expect(page.getByText("DEMO DATA", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Model Sources" }).click();
  await expect(page.getByRole("heading", { level: 1, name: "Model Sources" })).toBeVisible();
  const demo = page.getByRole("region", { name: "Demo Ollama" });
  await demo.getByRole("button", { name: "Test connection" }).click();
  await expect(demo.getByRole("status")).toHaveText("Simulated connection passed.");
  expect(requests).toEqual([]);

  await page.getByRole("button", { name: "Live" }).click();
  const ollamaCard = page.getByRole("region", { name: "Local Ollama" });
  const lmCard = page.getByRole("region", { name: "Local LM Studio" });
  await lmCard.getByRole("button", { name: "Sync" }).click();
  await expect(lmCard.getByRole("status")).toHaveText("Source is unreachable");
  await ollamaCard.getByRole("button", { name: "Sync" }).click();
  await expect(ollamaCard.getByText("Installed · Not loaded")).toBeVisible();
  await expect(lmCard.getByRole("status")).toHaveText("Source is unreachable");

  await page.getByRole("button", { name: "Toggle theme" }).click();
  await expect(page.locator("body")).toHaveClass("light");
  await expect(ollamaCard.getByText("Installed · Not loaded")).toBeVisible();

  await page.getByRole("button", { name: "Overview" }).click();
  await expect(page.getByRole("heading", { level: 1, name: "Overview" })).toBeVisible();
  await expect(page.getByText("DEMO DATA", { exact: true })).toBeVisible();
});

test("Model Sources opens from the shared mobile navigation", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page.getByRole("button", { name: "Model Sources" }).click();
  await expect(page.getByRole("heading", { name: "Model Sources", level: 1 })).toBeVisible();
  await expect(page.getByRole("button", { name: "Demo", exact: true })).toBeVisible();
  await expect(page.locator("#sidebar")).not.toHaveClass(/\bopen\b/);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(390);
});
