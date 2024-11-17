import asyncio
import logging
import typing
from scrapy.http import Response, HtmlResponse, Request
from scrapy.spiders import CrawlSpider, Rule     # crawlspider crawling multiple pages
from scrapy.linkextractors import LinkExtractor  
from bs4 import BeautifulSoup
import aiofiles
import aiofiles.os
import os
from markdownify import MarkdownConverter
import traceback

# Maximum number of markdown files to save
MAX_MARKDOWN_FILES = 15
saved_files_count = 0

logger = logging.getLogger()  # creating rootlogger for loging messages

#soup to markdown conversion
def md(soup, **options) -> str:
    return MarkdownConverter(**options).convert_soup(soup)

class HsrwSpider(CrawlSpider):
    all_tasks: typing.Set[asyncio.Task[None]] = set()
    name = 'hs-rheinwaal'
    start_urls = ['https://www.hochschule-rhein-waal.de/de']
    rules = [
        Rule(
            LinkExtractor(
              
                allow_domains=['hochschule-rhein-waal.de'],
                deny_domains=[
                    #shop /his
                    'shop.hochschule-rhein-waal.de',
                    'hisinone.hochschule-rhein-waal.de',
                    'hisinone.hochschule-rhein-waal.de/qisserver/pages/cs/sys/portal/hisinoneStartPage.faces?chco=y',
                    #social media and external
                    'instagram.com/hsrheinwaal/',
                    'facebook.com/hochschulerheinwaal',
                    'youtube.com/user/HSRheinWaal',
                    'linkedin.com/edu/rhine-waal-university-155058',
                    'dg-hochn.de/',
                    'hn-nrw.de/nachhaltigkeitsallianz/',
                    'sicherimdienst.nrw',
                
                ],
              
                allow=[
            
                    r'/.*'
                ]
            ),
            process_links='filter_links',
            callback='parse',
            follow=True
        )
    
    ]
    crawled_pdfs: typing.List[str] = []

    def filter_links(self, links): # type: ignore
        for link in links: # type: ignore
            if '?' in link.url: # type: ignore
                continue
            else:
                yield link

    custom_settings = {
        'DEPTH_LIMIT': 20,
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'DOWNLOAD_DELAY': 0.1,
        'DEPTH_STATS_VERBOSE': True,
        'ROBOTSTXT_OBEY': True,
    }

    async def parse(self, response: Response):
        global saved_files_count

        if saved_files_count >= MAX_MARKDOWN_FILES:
            logger.info("Reached the maximum limit of markdown files. Stopping the spider.")
            self.crawler.engine.close_spider(self, 'Max file limit reached')
            return

        if type(response) is not HtmlResponse:
            logger.warning(f"Got non HTML response from url: {response.url}")
            return

        try:
            body = response.xpath('//*[contains(@class, "dialog-off-canvas-main-canvas")]')
            content = body.xpath('.//*[contains(@class, "col-12 col-lg-9 region-content")]').get('')
        except Exception as e:
            logger.error(
                "Encountered error while parsing response body",
                extra={
                    "exception_name": type(e).__name__,
                    "exception": str(e),
                    "traceback": traceback.format_exception(
                        type(e), value=e, tb=e.__traceback__
                    )
                }
            )
            return

        soup = BeautifulSoup(content, "html.parser")
        text = md(soup, strip=['img'])
        filename = f'../data/crawled/{response.url.replace("https://", "").rstrip("/")}.md'
        task = asyncio.create_task(self.write_file(filename, text))
        self.all_tasks.add(task)
        task.add_done_callback(self.all_tasks.discard)
        logger.info(
            "Crawler scraped specific content",
            extra={"type": "crawler_scraped_specific", "url": response.url}
        )

    async def write_file(self, filename: str, text: str):
        global saved_files_count

        # Stop writing if the limit is reached
        if saved_files_count >= MAX_MARKDOWN_FILES:
            logger.info("Reached the maximum limit of markdown files. Stopping the spider.")
            self.crawler.engine.close_spider(self, 'Max file limit reached')
            return

        await aiofiles.os.makedirs(os.path.dirname(filename), exist_ok=True)
        async with aiofiles.open(filename, 'w') as f:
            await f.write(text)

        # Increment the saved files count
        saved_files_count += 1
        logger.info(f"Markdown file saved: {filename} (Total: {saved_files_count})")


    async def write_b_file(self, filename: str, data):
        await aiofiles.os.makedirs(os.path.dirname(filename), exist_ok=True)
        async with aiofiles.open(filename, 'wb') as f:
            await f.write(data)
        
        