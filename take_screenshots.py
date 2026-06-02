import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 800})
        print("Navigating to localhost:8501...")
        await page.goto("http://localhost:8501")
        # Wait for Streamlit to render
        await page.wait_for_timeout(5000)
        
        print("Taking Stres Analizi screenshot...")
        await page.screenshot(path="screenshot_stress_analizi.png")
        
        print("Clicking Satıcı İstihbaratı...")
        await page.get_by_text("Satıcı İstihbaratı", exact=True).click()
        await page.wait_for_timeout(2000)
        await page.screenshot(path="screenshot_satici_istihbarati.png")
        
        print("Clicking Teknik Sözlük...")
        await page.get_by_text("Teknik Sözlük", exact=True).click()
        await page.wait_for_timeout(2000)
        await page.screenshot(path="screenshot_teknik_sozluk.png")
        
        print("Clicking Tarihsel Arşiv...")
        await page.get_by_text("Tarihsel Arşiv", exact=True).click()
        await page.wait_for_timeout(2000)
        await page.screenshot(path="screenshot_tarihsel_arsiv.png")
        
        await browser.close()
        print("Screenshots captured successfully.")

asyncio.run(main())
