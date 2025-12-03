import { test, expect } from "@playwright/test";

// Utility to generate random emails for registration
function randomEmail() {
    return `user_${Date.now()}@test.com`;
}

test.describe("Authentication E2E Tests", () => {

    // --------------------------
    // Positive Test 1
    // REGISTER with valid data
    // --------------------------
    test("Register with valid data → success message", async ({ page }) => {
        await page.goto("http://127.0.0.1:8000/register");

        const email = randomEmail();

        await page.fill("#email", email);
        await page.fill("#password", "StrongPass123");
        await page.fill("#confirmPassword", "StrongPass123");

        await page.click("#registerBtn");

        // Expect UI success message
        await expect(page.locator("#message")).toContainText("Registration successful");
    });


    // --------------------------
    // Positive Test 2
    // LOGIN with correct credentials
    // --------------------------
    test("Login with valid credentials → success or token stored", async ({ page }) => {
        const email = randomEmail();

        // 1. Register first
        await page.goto("http://127.0.0.1:8000/register");
        await page.fill("#email", email);
        await page.fill("#password", "StrongPass123");
        await page.fill("#confirmPassword", "StrongPass123");
        await page.click("#registerBtn");

        // 2. Login
        await page.goto("http://127.0.0.1:8000/login");
        await page.fill("#email", email);
        await page.fill("#password", "StrongPass123");
        await page.click("#loginBtn");

        // Expect token message in UI
        await expect(page.locator("#message")).toContainText("Login successful");
    });


    // --------------------------
    // Negative Test 1
    // REGISTER with short password
    // --------------------------
    test("Register with short password → front-end or 400 error", async ({ page }) => {
        await page.goto("http://127.0.0.1:8000/register");

        await page.fill("#email", randomEmail());
        await page.fill("#password", "123");
        await page.fill("#confirmPassword", "123");

        await page.click("#registerBtn");

        await expect(page.locator("#message")).toContainText("Password must be at least");
    });


    // --------------------------
    //  Negative Test 2
    // LOGIN with wrong password
    // --------------------------
    test("Login with wrong password → server 401 + error shown", async ({ page }) => {
        const email = randomEmail();

        // First register
        await page.goto("http://127.0.0.1:8000/register");
        await page.fill("#email", email);
        await page.fill("#password", "StrongPass123");
        await page.fill("#confirmPassword", "StrongPass123");
        await page.click("#registerBtn");

        // Now login with wrong password
        await page.goto("http://127.0.0.1:8000/login");
        await page.fill("#email", email);
        await page.fill("#password", "WrongPassword!");
        await page.click("#loginBtn");

        await expect(page.locator("#message")).toContainText("Invalid username or password");
    });
});
