from .convertFileLinkToRawGithubUserContentLink import (
    convertFileLinkToRawGithubUserContentLink,
)
from .fetchFileContent import fetchFileContent
from .server import DEBUG_PNG_PATH, MCP_HOME_DIR
from playwright.async_api import async_playwright


import json
import logging
import urllib.parse


async def git_dump_screen(dict_input) -> str:
    logger = logging.getLogger(__name__)

    sleep_delay_s = dict_input["sleep_delay_s"]

    async with async_playwright() as p:

        RESULTS_JSON = {}
        REPOSITORY_LINKS = []
        FILE_LINKS = []
        RAW_UESR_CONTENT_LINKS = []
        FILE_CONTENTS = []
        output_meta = []

        from datetime import datetime, timedelta
        import urllib.parse

        ONE_YEAR_AGO = (datetime.now() - timedelta(days=360)).strftime("%Y-%m-%d")

        SEARCH_FILE_NAME = ".clinerules"
        SEARCH_FILE_PATH = None
        # ".clinerules"
        SEARCH_LANGUAGE = None
        # "typescript"

        SEARCH_TERMS = []
        if SEARCH_FILE_NAME:
            SEARCH_TERMS = [
                *SEARCH_TERMS,
                urllib.parse.quote(f"path:{SEARCH_FILE_NAME}"),
            ]

        if SEARCH_FILE_PATH:
            SEARCH_TERMS = [
                *SEARCH_TERMS,
                urllib.parse.quote("path:")
                + "**"
                + urllib.parse.quote(SEARCH_FILE_NAME),
            ]

        if SEARCH_LANGUAGE:
            SEARCH_TERMS = [
                *SEARCH_TERMS,
                urllib.parse.quote("language:" + SEARCH_LANGUAGE),
            ]

        # SEARCH_TERMS = [
        #     *SEARCH_TERMS,
        #     urllib.parse.quote("updated:") + "<" + urllib.parse.quote(ONE_YEAR_AGO),
        # ]

        ENCODED_SEARCH_TERMS = "+".join(map(lambda x: (x), SEARCH_TERMS))

        browser = await p.chromium.launch_persistent_context(
            user_data_dir=f"{MCP_HOME_DIR}/_user_data_dir",
            headless=True,
        )
        page = await browser.new_page()

        URL_TO_PROBE = f"https://github.com/search?q={ENCODED_SEARCH_TERMS}&type=code&ref=advsearch"

        await page.goto(URL_TO_PROBE)

        # probe max page
        RESULTS_STR = await page.evaluate(
            """async () => {
                  STATUS_OK = true;

                  LOGGED_IN_CHECK = false
                  try {
                    document.querySelectorAll('span[data-component="buttonContent"]>span[data-component="text"]')[3].textContent;
                    console.log("not logged in");
                    STATUS_OK = false;
                  } catch (error){
                    LOGGED_IN_CHECK = true;
                    console.log("logged in");
                  }

                  MAX_PAGE_NUM = 0
                  try {
                    MAX_PAGE_NUM = document.querySelectorAll('nav')[2].textContent.replace('Next','').replace('Previous','').slice(-1);
                  } catch (error){
                    MAX_PAGE_NUM = -1;
                    STATUS_OK = false;
                  }

                  FILE_FOUND_NUM = 0
                  try {
                    FILE_FOUND_NUM = document.querySelectorAll('div[data-testid="search-sub-header"] h2')[0].textContent
                      .replace(' files','')
                      .replace('More than ','')
                      .trim();
                  } catch (error){
                    FILE_FOUND_NUM = -1;
                    STATUS_OK = false;
                  }

                  return JSON.stringify({STATUS_OK, LOGGED_IN_CHECK, MAX_PAGE_NUM, FILE_FOUND_NUM})
                }"""
        )

        RESULT_JSON = json.loads(RESULTS_STR)
        STATUS_OK = RESULT_JSON["STATUS_OK"]
        FILE_FOUND_NUM = RESULT_JSON["FILE_FOUND_NUM"]

        if not (STATUS_OK):
            return json.dumps(
                {
                    "result": "the page return is not ok",
                    "debug": RESULT_JSON,
                }
            )

        if int(FILE_FOUND_NUM) <= 0:
            return json.dumps(
                {
                    "result": "no result found",
                    "debug": RESULT_JSON,
                }
            )

        MAX_PAGE_NUM = RESULT_JSON["MAX_PAGE_NUM"]
        if int(MAX_PAGE_NUM) <= 0:
            return json.dumps(
                {
                    "result": "no result found",
                    "debug": RESULT_JSON,
                }
            )
        MAX_PAGE_NUM = int(MAX_PAGE_NUM)
        # should be no-error after this line

        for i in range(1, MAX_PAGE_NUM + 1):
            logger.info("scaping page " + str(i))

            await page.goto(
                f"https://github.com/search?q={ENCODED_SEARCH_TERMS}&type=code&ref=advsearch&p={str(i)}"
            )

            await page.screenshot(path=DEBUG_PNG_PATH)

            # TODO: wait for navigation ready instead
            await page.wait_for_timeout(sleep_delay_s * 1000)

            RESULTS_STR = await page.evaluate(
                """async () => {
                  response = await fetch(location.href)

                  LOGGED_IN_CHECK = false
                  try {
                    document.querySelectorAll('span[data-component="buttonContent"]>span[data-component="text"]')[3].textContent
                    console.log("not logged in")
                  } catch (error){
                    LOGGED_IN_CHECK = true
                    console.log("logged in")
                  }

                  REPOSITORY_LINKS_FETCHED = []
                  document.querySelectorAll('div.search-title a[aria-keyshortcuts="Alt+ArrowUp"]')
                    .forEach(a => REPOSITORY_LINKS_FETCHED = [...REPOSITORY_LINKS_FETCHED, a.href]);

                  FILE_LINKS_FETCHED = []
                  document.querySelectorAll('div.search-title a:not([aria-keyshortcuts="Alt+ArrowUp"]')
                    .forEach(a => FILE_LINKS_FETCHED = [...FILE_LINKS_FETCHED, a.href]);

                  return JSON.stringify({LOGGED_IN_CHECK,REPOSITORY_LINKS_FETCHED, FILE_LINKS_FETCHED})
                }"""
            )

            RESULTS_JSON = json.loads(RESULTS_STR)
            LOGGED_IN_CHECK = RESULTS_JSON["LOGGED_IN_CHECK"]

            if LOGGED_IN_CHECK:
                REPOSITORY_LINKS = [
                    *REPOSITORY_LINKS,
                    *RESULTS_JSON["REPOSITORY_LINKS_FETCHED"],
                ]
                FILE_LINKS = [
                    *FILE_LINKS,
                    *RESULTS_JSON["FILE_LINKS_FETCHED"],
                ]

            else:
                print("not loggin, break")
                break

        # await page.wait_for_timeout(sleep_delay_s * 1000)
        # await page.goto("https://www.github.com")
        # await page.screenshot(path=DEBUG_PNG_PATH)
        # page_title = await page.title()

        await browser.close()

        if len(FILE_LINKS) > 0:
            print("converting links")
            RAW_UESR_CONTENT_LINKS = list(
                map(lambda x: convertFileLinkToRawGithubUserContentLink(x), FILE_LINKS)
            )

        if len(RAW_UESR_CONTENT_LINKS) > 0:
            FILE_CONTENTS = list(
                map(lambda x: fetchFileContent(x), RAW_UESR_CONTENT_LINKS)
            )

        for i in range(0, len(FILE_LINKS)):
            output_meta.append(
                {
                    "REPOSITORY_LINK": REPOSITORY_LINKS[i],
                    "FILE_LINK": FILE_LINKS[i],
                    "RAW_UESR_CONTENT_LINK": RAW_UESR_CONTENT_LINKS[i],
                    "FILE_CONTENT": FILE_CONTENTS[i],
                }
            )

    return json.dumps(output_meta)
