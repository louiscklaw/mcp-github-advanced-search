import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.example.com")

        await page.screenshot(path="example.png")

        print(await page.title())
        await browser.close()


asyncio.run(main())
