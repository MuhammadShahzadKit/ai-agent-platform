from playwright.sync_api import sync_playwright

p = sync_playwright().start()

c = p.chromium.launch_persistent_context(
    user_data_dir=".browser_profile",
    headless=False,
)

page = c.pages[0] if c.pages else c.new_page()

page.goto(
    "https://studio.youtube.com/channel/UCOx-GH4ZDiFnJSKXwZKltIw/videos/upload",
    wait_until="domcontentloaded",
    timeout=60000,
)

page.wait_for_timeout(5000)

edit = page.get_by_text("Edit draft", exact=True)

print("EDIT_DRAFT:", edit.count())

if edit.count():
    edit.first.click()
    page.wait_for_timeout(4000)

title_box = page.locator(
    '[contenteditable="true"][aria-label*="title that describes your video"]'
).first

description_box = page.locator(
    '[contenteditable="true"][aria-label*="Tell viewers about your video"]'
).first

print("TITLE_BOX:", title_box.count())
print("DESCRIPTION_BOX:", description_box.count())

if title_box.count():
    title_box.fill("AI Agent Production Selector Test")

if description_box.count():
    description_box.fill(
        "Production selector test completed successfully."
    )

page.wait_for_timeout(2000)

print("TITLE_VALUE:", title_box.inner_text())
print("DESCRIPTION_VALUE:", description_box.inner_text())

input("Press ENTER to close...")

c.close()
p.stop()
