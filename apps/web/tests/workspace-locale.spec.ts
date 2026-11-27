import { expect, test } from "@playwright/test";

test("Thai workspace navigation, search, and Model Sources survive a mobile reload", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  await page.getByRole("combobox", { name: "Language" }).selectOption("th");
  await expect(page.locator("html")).toHaveAttribute("lang", "th");
  await expect(page.getByRole("heading", { name: "ภาพรวม", exact: true, level: 1 })).toBeVisible();
  await expect(page.getByRole("heading", { name: "กิจกรรมการประมวลผล" })).toBeVisible();
  await page.setViewportSize({ width: 320, height: 800 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(320);
  await page.setViewportSize({ width: 1440, height: 900 });

  await page.getByRole("button", { name: /ค้นหาเมนู/ }).click();
  await page.getByPlaceholder("ค้นหาหน้า…").fill("แหล่งโมเดล");
  await page.getByRole("dialog").getByRole("button", { name: "แหล่งโมเดล", exact: true }).click();
  await expect(page.getByRole("heading", { name: "แหล่งโมเดล", exact: true, level: 1 })).toBeVisible();

  await page.setViewportSize({ width: 320, height: 800 });
  await page.reload();
  const language = page.getByRole("combobox", { name: "ภาษา" });
  await expect(language).toHaveValue("th");
  const demo = page.getByRole("region", { name: "Ollama ตัวอย่าง" });
  await demo.getByRole("button", { name: "ทดสอบการเชื่อมต่อ" }).click();
  await expect(demo.getByRole("status")).toHaveText("การทดสอบการเชื่อมต่อจำลองผ่าน");
  await page.route("**/api/v1/model-sources", route => route.fulfill({ json: [{
    id: "ollama", name: "Ollama", engine: "ollama", url: "http://ollama:11434/",
    snapshot: {
      status: "ready", synced_at: null, error: null,
      models: [{ id: "thai:latest", name: "โมเดลทดสอบภาษาไทย", installed: true, loaded: false, served: null }],
    },
  }] }));
  await page.getByRole("button", { name: "ข้อมูลจริง", exact: true }).click();
  await expect(page.getByText("โมเดลทดสอบภาษาไทย", { exact: true })).toBeVisible();
  await expect(page.getByText("ติดตั้งแล้ว · ยังไม่ได้โหลด", { exact: true })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(320);

  await language.selectOption("en");
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  await expect(page.getByRole("heading", { name: "Model Sources", exact: true, level: 1 })).toBeVisible();
  await expect(page.getByRole("button", { name: "Live", exact: true })).toHaveAttribute("aria-pressed", "true");
});
