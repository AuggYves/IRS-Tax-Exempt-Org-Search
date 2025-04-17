import pandas as pd
import asyncio
from playwright.async_api import async_playwright

# Main scraper function
async def run_scraper():
    org_names = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the IRS EoS page
        await page.goto("https://apps.irs.gov/app/eos/")
        await page.wait_for_selector("#city", timeout=15000)

        # Fill in City and State
        await page.fill("#city", "Omaha")
        await page.select_option("#state", "NE")

        # Click Search
        await page.click("#search-button")
        await page.wait_for_timeout(3000)

        # Loop through all result pages
        while True:
            print("Scraping page...")
            await page.wait_for_selector('a[aria-label]', timeout=10000)
            links = await page.locator('a[aria-label]').all()

            for link in links:
                label = await link.get_attribute('aria-label')
                if label:
                    org_names.append(label.strip())

            # Try clicking the Next button
            try:
                next_button = page.locator("text=Next")
                if await next_button.is_visible():
                    await next_button.click()
                    await page.wait_for_timeout(2000)
                else:
                    break
            except:
                break

        await browser.close()

    # Save to Excel
    df = pd.DataFrame(org_names, columns=["Organization Name"])
    df.to_excel("omaha_ne_orgs.xlsx", index=False)
    print("Scraping complete. Saved to omaha_ne_orgs.xlsx")

# Run the scraper if executed directly
if __name__ == "__main__":
    asyncio.run(run_scraper())
