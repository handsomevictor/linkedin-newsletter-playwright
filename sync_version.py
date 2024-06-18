import os
import re
import time
import random
from playwright.sync_api import sync_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/58.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/58.0",
]


def main(linkedin_newsletter_urls):
    with sync_playwright() as p:
        # browser = p.chromium.launch(headless=False)
        # use firefox
        browser = p.firefox.launch(headless=True)
        context = browser.new_context()

        # 设置随机用户代理
        user_agent = random.choice(USER_AGENTS)
        context.set_extra_http_headers({"User-Agent": user_agent})

        # Open a new page
        page = context.new_page()

        # Navigate to a URL
        for idx, linkedin_newsletter_url in enumerate(linkedin_newsletter_urls):
            page.goto(f'{linkedin_newsletter_url}')

            # sleep random time use page.wait_for_timeout(random.randint(1000, 3000))
            page.wait_for_timeout(random.randint(800, 2000))

            # if login popup appears, close it
            login_close_button_selector = '.contextual-sign-in-modal__modal-dismiss-icon > svg:nth-child(1) > path:nth-child(1)'
            if page.locator(login_close_button_selector).is_visible():
                page.locator(login_close_button_selector).click()

            page.wait_for_timeout(random.randint(800, 2000))

            # Wait for the element to be visible
            title_selector = '.pulse-title'
            page.wait_for_selector(title_selector)
            title_content = page.locator(title_selector).inner_text()
            print(title_content)

            page.wait_for_timeout(random.randint(800, 2000))

            if page.locator(login_close_button_selector).is_visible():
                page.locator(login_close_button_selector).click()
                page.wait_for_timeout(random.randint(400, 1000))

            article_content_selector = '[data-test-id="article-content-blocks"]'
            page.wait_for_selector(article_content_selector)
            article_content = page.locator(article_content_selector).inner_text()
            print(article_content)

            page.wait_for_timeout(random.randint(800, 2000))

            if page.locator(login_close_button_selector).is_visible():
                page.locator(login_close_button_selector).click()
                page.wait_for_timeout(random.randint(800, 2000))

            # save to text
            with open(f'article_{idx}.txt', 'w') as f:
                f.write(title_content)
                f.write(article_content)

        input('Press any key to close the browser')
        browser.close()


if __name__ == '__main__':
    linkedin_newsletter_urls = ['https://www.linkedin.com/pulse/144-ita%25C3%25BA-opens-bitcoin-trading-platform-all-users-aaron-stanley-mqmzf/?trackingId=LZKGzDSSTpeL880pvhTRmw%3D%3D',
        'https://www.linkedin.com/pulse/143-crypto-regulations-come-early-2025-says-bc-aaron-stanley-8ag2f/?trackingId=vEwXZg0xRbeeS0QTalUFeQ%3D%3D',
        'https://www.linkedin.com/pulse/143-crypto-regulations-come-early-2025-says-bc-aaron-stanley-8ag2f/?trackingId=vEwXZg0xRbeeS0QTalUFeQ%3D%3D',
        'https://www.linkedin.com/pulse/latam-crypto-report-14-bancolombia-launches-wenia-exchange-stanley-nce0e/?trackingId=y6uTU8F%2FR5ytwlzboqUNfA%3D%3D']
    main(linkedin_newsletter_urls)
