import asyncio
from playwright import async_api
from playwright.async_api import expect

async def run_test():
    pw = None
    browser = None
    context = None

    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()

        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",         # Set the browser window size
                "--disable-dev-shm-usage",        # Avoid using /dev/shm which can cause issues in containers
                "--ipc=host",                     # Use host-level IPC for better stability
                "--single-process"                # Run the browser in a single process mode
            ],
        )

        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        context.set_default_timeout(5000)

        # Open a new page in the browser context
        page = await context.new_page()

        # Interact with the page elements to simulate user flow
        # -> Navigate to http://localhost:5173/
        await page.goto("http://localhost:5173/")
        
        # -> Load the app with a long, special-character agentId in the URL and check the page text for the exact greeting 'Hello {agentId}' (should render as plain readable text) or the exact error 'Error: Agent ID not found'.
        await page.goto("http://localhost:5173/?agentId=long-special-Agent-%E6%B5%8B%E8%AF%95-%F0%9F%98%80-with%20spaces%20%26%20symbols%20%25%24%23%40%21%3C%3E%2F%5C%7C%5B%5D%7B%7D%28%29")
        
        # --> Assertions to verify final state
        frame = context.pages[-1]
        assert await frame.locator("xpath=//*[contains(., 'Hello long-special-Agent-测试-😀-with spaces & symbols %$#@!<>/\\|[]{}()')]" ).nth(0).is_visible(), "The greeting should display the full agent identifier as plain readable text without breaking the panel layout after loading the page with a long, special-character agentId"
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    