import { test, expect } from "@playwright/test";

test.describe("Minimal Login Tests ", () => {

    test("Register page loads", async ({ page }) => {
        await page.goto("http://127.0.0.1:8000/register");
        await expect(page.locator("h1")).toContainText("Create an Account");
    });

    test("Login page loads", async ({ page }) => {
        await page.goto("http://127.0.0.1:8000/login");
        await expect(page.locator("h1")).toContainText("Login");
    });

    test("Register button updates message box", async ({ page }) => {
        await page.goto("http://127.0.0.1:8000/register");

        await page.click("#registerBtn");

        const msg = page.locator("#message");
        await expect(msg).toBeVisible();
    });

    test("Login button updates message box", async ({ page }) => {
        await page.goto("http://127.0.0.1:8000/login");

        await page.click("#loginBtn");

        const msg = page.locator("#message");
        await expect(msg).toBeVisible();
    });

});
