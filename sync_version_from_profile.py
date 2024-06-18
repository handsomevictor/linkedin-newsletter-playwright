import os
import re
import time
import random
from tqdm import tqdm
from playwright.sync_api import sync_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/58.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/58.0",
]


# noinspection PyShadowingNames
def main(profile_url):
    """
    First get to the profile, and get the links of all the newsletters, and then get the content of each newsletter
    """
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()

        # Set a random user agent
        user_agent = random.choice(USER_AGENTS)
        context.set_extra_http_headers({"User-Agent": user_agent})

        page = context.new_page()
        page.goto(f'{profile_url}')

        # class = share-article__content
        contents_newsletter_selector = '.share-article__content .share-article__title-link'

        # page.wait_for_selector(contents_newsletter_selector)
        page.wait_for_timeout(random.randint(800, 2000))

        linkedin_newsletter_elements = page.locator(contents_newsletter_selector)

        count = linkedin_newsletter_elements.count()
        if count == 0:
            raise Exception("No newsletter links found. Website is blocked or changed, trying again in 10 seconds.")

        final_linkedin_newsletter_urls = []
        for i in range(count):
            element = linkedin_newsletter_elements.nth(i)
            # get href attribute
            inner_html = element.get_attribute('href')

            final_linkedin_newsletter_urls.append(inner_html)

        print(final_linkedin_newsletter_urls)
        print(len(final_linkedin_newsletter_urls))

        page.wait_for_timeout(random.randint(800, 2000))

        # Navigate to a URL
        for idx, linkedin_newsletter_url in tqdm(enumerate(final_linkedin_newsletter_urls),
                                                 total=len(final_linkedin_newsletter_urls)):
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

            page.wait_for_timeout(random.randint(800, 2000))

            if page.locator(login_close_button_selector).is_visible():
                page.locator(login_close_button_selector).click()
                page.wait_for_timeout(random.randint(400, 1000))

            article_content_selector = '[data-test-id="article-content-blocks"]'
            page.wait_for_selector(article_content_selector)
            article_content = page.locator(article_content_selector).inner_text()

            page.wait_for_timeout(random.randint(800, 2000))

            if page.locator(login_close_button_selector).is_visible():
                page.locator(login_close_button_selector).click()
                page.wait_for_timeout(random.randint(800, 2000))

            # save to text
            with open(os.path.join(os.getcwd(), 'database', f'article_{idx}.txt'), 'w') as f:
                f.write(title_content)
                f.write('\n')
                f.write(article_content)

        input('Press any key to close the browser')
        browser.close()


if __name__ == '__main__':
    profile_url = 'https://www.linkedin.com/newsletters/brazil-crypto-report-6921453107637862400/'

    try_count = 0
    while try_count < 3:
        try:
            main(profile_url)
            break
        except Exception as e:
            print(e)
            print("An error occurred. Very possibly linkedin has detected the bot. Trying again in 10 seconds.")
            time.sleep(10)



