"""
When more than 5 recent articles are needed, login is required.
"""

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


if os.path.exists('linkedin_newsletter_urls.txt'):
    os.remove('linkedin_newsletter_urls.txt')
    print(f"File 'linkedin_newsletter_urls.txt' removed")


# create an empty file
with open('linkedin_newsletter_urls.txt', 'w') as f:
    pass


# noinspection PyShadowingNames
def main(profile_url, url_level_retry_times=5):
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

        # ----------------- Login to LinkedIn first --------------------------------------------------------------------
        button_locator = 'nav__button-secondary'
        # set a waiting time of 4 seconds
        page.wait_for_selector(f'.{button_locator}', timeout=4000)
        if not page.locator(f'.{button_locator}').is_visible():
            raise Exception("Login button not found. Website is blocked or changed, trying again in 10 seconds.")
        page.locator(f'.{button_locator}').click()
        page.wait_for_timeout(random.randint(800, 2000))

        # input id: username
        page.fill('input#username', os.environ.get('LINKEDIN_USERNAME'))
        page.wait_for_timeout(random.randint(1000, 1500))
        page.fill('input#password', os.environ.get('LINKEDIN_PWD'))
        page.wait_for_timeout(random.randint(1000, 1500))
        # click login button: .btn__primary--large
        page.click('.btn__primary--large')

        page.wait_for_timeout(random.randint(3000, 5000))

        # ----------------- Get the links of all the newsletters -------------------------------------------------------
        # judge if there is anything in linkedin_newsletter_urls.txt,
        # if there is, it means the overall retry is
        # happening, so no need to get all urls again
        skip_get_all_urls = False
        with open('linkedin_newsletter_urls.txt', 'r') as f:
            final_linkedin_newsletter_urls = f.readlines()
            if len(final_linkedin_newsletter_urls) > 0:
                print(f"linkedin_newsletter_urls.txt already has urls, no need to get all urls again.")
                skip_get_all_urls = True

        if not skip_get_all_urls:
            # restart the page
            page.goto(f'{profile_url}')
            # class = share-article__content
            contents_newsletter_selector = '.update-components-article__meta'

            # page.wait_for_selector(contents_newsletter_selector)
            page.wait_for_timeout(random.randint(800, 2000))

            linkedin_newsletter_elements = page.locator(contents_newsletter_selector)

            count = linkedin_newsletter_elements.count()
            if count == 0:
                raise Exception("No newsletter links found. Website is blocked or changed, trying again in 10 seconds.")

            # scroll to the bottom of the page
            previous_height = None
            while True:
                # if login popup appears, close it
                login_close_button_selector = '.contextual-sign-in-modal__modal-dismiss-icon > svg:nth-child(1) > path:nth-child(1)'
                if page.locator(login_close_button_selector).is_visible():
                    page.locator(login_close_button_selector).click()

                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(random.randint(1000, 2000))
                current_height = page.evaluate('document.body.scrollHeight')
                if current_height == previous_height:
                    break
                previous_height = current_height

            final_linkedin_newsletter_urls = []
            linkedin_newsletter_elements = page.locator(contents_newsletter_selector)
            count = linkedin_newsletter_elements.count()
            print(f'count: {count}')

            for i in range(count):
                element = linkedin_newsletter_elements.nth(i)
                # get href attribute
                inner_html = element.get_attribute('href')

                final_linkedin_newsletter_urls.append(inner_html)

                # save to file
                with open('linkedin_newsletter_urls.txt', 'a') as f:
                    f.write(inner_html)
                    f.write('\n')

        print(final_linkedin_newsletter_urls)
        print(len(final_linkedin_newsletter_urls))

        page.wait_for_timeout(random.randint(800, 2000))

        # ----------------- Get the content of each newsletter ---------------------------------------------------------
        # Navigate to a URL
        for idx, linkedin_newsletter_url in tqdm(enumerate(final_linkedin_newsletter_urls),
                                                 total=len(final_linkedin_newsletter_urls)):
            # single url level retry n times
            i = 0
            while i < url_level_retry_times:
                try:
                    page.goto(f'{linkedin_newsletter_url}')

                    # sleep random time use page.wait_for_timeout(random.randint(1000, 3000))
                    page.wait_for_timeout(random.randint(800, 2000))

                    # if login popup appears, close it
                    login_close_button_selector = '.contextual-sign-in-modal__modal-dismiss-icon > svg:nth-child(1) > path:nth-child(1)'
                    if page.locator(login_close_button_selector).is_visible():
                        page.locator(login_close_button_selector).click()

                    page.wait_for_timeout(random.randint(800, 2000))

                    # Wait for the element to be visible
                    title_selector = '.reader-article-header__title'

                    try:
                        page.wait_for_selector(title_selector)
                    except:
                        page.wait_for_timeout(random.randint(800, 2000))

                    title_content = page.locator(title_selector).inner_text()
                    print(title_content)

                    page.wait_for_timeout(random.randint(1400, 2000))

                    if page.locator(login_close_button_selector).is_visible():
                        page.locator(login_close_button_selector).click()
                        page.wait_for_timeout(random.randint(400, 1000))

                    article_content_selector = '.reader-article-content--content-blocks'

                    try:
                        page.wait_for_selector(article_content_selector)
                    except:
                        page.wait_for_timeout(random.randint(800, 2000))

                    article_content = page.locator(article_content_selector).inner_text()

                    page.wait_for_timeout(random.randint(1100, 2000))

                    if page.locator(login_close_button_selector).is_visible():
                        page.locator(login_close_button_selector).click()
                        page.wait_for_timeout(random.randint(800, 2000))

                    # save to text
                    with open(os.path.join(os.getcwd(), 'database', f'article_{idx}_{title_content}.txt'), 'w') as f:
                        f.write(title_content)
                        f.write('\n')
                        f.write(article_content)

                    page.wait_for_timeout(random.randint(200, 400))
                    break
                except Exception as e:
                    print(f"An error occurred. Trying again this single url in 2 seconds. Error: {e}")
                    i += 1
                    page.wait_for_timeout(random.randint(800, 2000))

            # remove the corresponding url in linkedin_newsletter_urls.txt
            try:
                with open('linkedin_newsletter_urls.txt', 'r') as f:
                    lines = f.readlines()
                    lines = [line.split('/')[-1] for line in lines]
                    lines = [line for line in lines if line.strip() != linkedin_newsletter_url]

                with open('linkedin_newsletter_urls.txt', 'w') as f:
                    f.writelines(lines)
                    print(f"Removed the corresponding url: {linkedin_newsletter_url}")
            except Exception as e:
                print(f"Error occurred when removing the corresponding url: {linkedin_newsletter_url}. Error: {e}")
                pass

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



