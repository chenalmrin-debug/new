from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
    for i in range(1,5):
        pg.goto(f'file:///home/user/new/stories/s{i}.html'); pg.wait_for_timeout(600)
        pg.screenshot(path=f'/home/user/new/stories/story{i}.png')
    b.close()
