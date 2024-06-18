import os
import re
import time
import random
import asyncio
from playwright.async_api import async_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/58.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/58.0",
]

CONCURRENCY_LIMIT = 1  # Adjust this based on your system's capabilities - 但是coingecko有反爬虫机制，如果太快了就ban了ip


async def fetch_token_data(token_name, semaphore):
    async with semaphore:
        domain_url = f'https://www.coingecko.com/en/coins/{token_name}'

        async with async_playwright() as p:
            user_agent = random.choice(USER_AGENTS)
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(user_agent=user_agent)
            page = await context.new_page()

            await page.goto(domain_url)

            # --------------- Find Holder Number ---------------
            ranking_selector = '.tw-text-xs.tw-leading-4.tw-text-gray-700.tw-font-medium'

            market_cap_selector = '.tw-text-gray-900.tw-font-semibold.tw-text-sm.tw-leading-5.tw-pl-2.tw-text-right'

            ranking_content = await page.locator(ranking_selector).nth(1).inner_text()
            ranking = ranking_content.replace('#', '')

            # get span content of market_cap_content
            child_span_selector = f"{market_cap_selector} > span"
            market_cap_content = await page.locator(child_span_selector).nth(0).inner_text()
            market_cap_content = market_cap_content.replace('$', '')

            print(f'For token: {token_name}, ranking: {ranking}, market cap: {market_cap_content}')

            await browser.close()


async def main():
    token_names = ['axelar', 'ethereum', 'maga-hat', 'mon-protocol'] * 100
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    tasks = [fetch_token_data(token_name, semaphore) for token_name in token_names]

    start_time = time.time()
    await asyncio.gather(*tasks)
    end_time = time.time()

    print(f"Running time: {end_time - start_time} seconds")


if __name__ == '__main__':
    asyncio.run(main())
