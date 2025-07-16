from typing import Annotated

import logging
from pathlib import Path

# from typing import Sequence, Optional
from mcp.server import Server

# from mcp.server.session import ServerSession
from mcp.server.stdio import stdio_server
from mcp.types import (
    # ClientCapabilities,
    TextContent,
    Tool,
    # ListRootsResult,
    # RootsCapability,
)
from enum import Enum
import git
import json
from pydantic import BaseModel, Field

from .CONST import USER_HOME_DIR, MCP_HOME_DIR, DEBUG_PNG_PATH

import aiohttp
import asyncio

from .fetch_data import fetch_data

from .fetchFileContent import fetchFileContent
from .convertFileLinkToRawGithubUserContentLink import (
    convertFileLinkToRawGithubUserContentLink,
)

from .url_util import getUrlToProbe, getUrlSearchPageNum

# from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

# from .git_dump_screen import git_dump_screen


# Default number of context lines to show in diff output
DEFAULT_CONTEXT_LINES = 3
ITEM_PER_BATCH = 3

PROBE_RESULT_JS = "".join(open("./probe_result.js", "r").readlines())
PARSE_RESULT_JS = "".join(open("./parse_result.js", "r").readlines())


SEARCH_CODE_EXPLAIN_MD = "".join(open("./SEARCH_CODE_EXPLAIN.md").readlines())
GET_REMAINING_RESULT_MD = "".join(open("./GET_REMAINING_RESULT.md").readlines())


class GitHelloworld(BaseModel):
    test_input: str


class GitEntrypoint(BaseModel):
    pass


class GitDumpScreen(BaseModel):
    keyword: Annotated[
        str,
        Field(
            default="helloworld", description="the keyword user interested, default('')"
        ),
    ]


class GasSearchCode(BaseModel):
    keyword: Annotated[
        str,
        Field(
            default="",
            description="the keyword user interested,\n"
            "e.g. `helloworld()`\n"
            "* Please limit the keyword to one single word only (e.g. `helloworld` and not `hello word`)\n"
            "default('')\n",
        ),
    ]
    file_name: Annotated[
        str,
        Field(
            default="",
            description="the file name user interested\n"
            "e.g. `.clinerules`\n"
            "default('')\n",
        ),
    ]
    # file_path: Annotated[
    #     str,
    #     Field(
    #         default="",
    #         description="the file path user interested,\n"
    #         "e.g. `**/.clinerules`\n"
    #         "default('')\n",
    #     ),
    # ]
    # language: Annotated[
    #     str,
    #     Field(
    #         default="",
    #         description="the programming/script language user interested,\n"
    #         "e.g. `javascript`\n"
    #         "default('')\n",
    #     ),
    # ]


class GetRemainingResult(BaseModel):
    start_id: Annotated[
        int,
        Field(
            default="0",
            description="start pointer for return the remaining result default('0')",
        ),
    ]


class GitTools(str, Enum):
    ENTRYPOINT = "gas_entrypoint"
    HELLOWORLD = "git_helloworld"
    DUMP_SCREEN = "git_dump_screen"
    SEARCH_CODE = "gas_search_code"
    GET_REMAINING_RESULT = "get_remaining_result"


async def git_helloworld(dict_input) -> str:
    test_input = dict_input["test_input"]

    if test_input == "1":
        return json.dumps(
            {
                "data": "world",
                "instructions": "that's all the data",
            }
        )

    return json.dumps(
        {
            "data": "hello",
            "instructions": "please use the `git_helloworld` tool with test_input='1' to get the remaining data",
        }
    )


async def gas_entrypoint() -> str:
    temp = ""
    with open("./gas_entrypoint.md", "r") as f_md:
        temp = "".join(f_md.readlines())

    return json.dumps(
        {
            "reply_md": temp,
            "next_instructions_md": "please ask user to provide `keyword` and `file_name` to start search",
        }
    )


async def get_remaining_result(dict_input) -> str:
    START_ID = dict_input["start_id"] or START_ID
    START_ID = int(START_ID)

    output_meta = []

    with open("/tmp/result.json", "r") as f:
        output_meta = json.load(f)

    if len(output_meta) > START_ID + 5:

        return json.dumps(
            [
                *output_meta[START_ID : START_ID + 5],
                {
                    "next_instruction_md": f"result truncated, please use `get_remaining_result` with start_id={START_ID+5} to get the remaining result."
                },
            ]
        )
    else:
        return json.dumps(
            [
                *output_meta[START_ID : START_ID + 5],
                {"next_instruction_md": "all result returned, show to user 'all result returned'"},
            ]
        )


async def gas_search_code(dict_input) -> str:
    """
    NOTE: T.B.A.

    Check if the URL can be fetched by the user agent according to the robots.txt file.
    Raises a McpError if not.
    """
    from datetime import datetime, timedelta
    import urllib.parse

    logger = logging.getLogger(__name__)

    SEARCH_KEYWORD = ""
    SEARCH_FILE_NAME = ""
    SEARCH_FILE_PATH = ""  # ".clinerules"
    SEARCH_LANGUAGE = ""  # "typescript"

    SEARCH_KEYWORD = dict_input["keyword"] or SEARCH_KEYWORD
    SEARCH_FILE_NAME = dict_input["file_name"] or SEARCH_FILE_NAME
    # SEARCH_FILE_PATH = dict_input["file_path"] or SEARCH_FILE_PATH
    # SEARCH_LANGUAGE = dict_input["language"] or SEARCH_LANGUAGE
    max_record_return = 10

    SEARCH_KEYWORD = SEARCH_KEYWORD.strip()
    SEARCH_FILE_NAME = SEARCH_FILE_NAME.strip()
    # SEARCH_FILE_PATH = SEARCH_FILE_PATH.strip()
    # SEARCH_LANGUAGE = SEARCH_LANGUAGE.strip()

    RESULTS_JSON = {}
    REPOSITORY_LINKS = []
    FILE_LINKS = []
    RAW_USER_CONTENT_LINKS = []
    FILE_CONTENTS = []
    output_meta = []

    SEARCH_TERMS = []

    if SEARCH_KEYWORD != "":
        SEARCH_TERMS = [
            *SEARCH_TERMS,
            urllib.parse.quote(f"{SEARCH_KEYWORD}"),
        ]

    if SEARCH_FILE_NAME != "":
        SEARCH_TERMS = [
            *SEARCH_TERMS,
            urllib.parse.quote(f"path:{SEARCH_FILE_NAME}"),
        ]

    # if SEARCH_FILE_PATH != "":
    #     SEARCH_TERMS = [
    #         *SEARCH_TERMS,
    #         urllib.parse.quote("path:") + "**" + urllib.parse.quote(SEARCH_FILE_PATH),
    #     ]

    # if SEARCH_LANGUAGE != "":
    #     SEARCH_TERMS = [
    #         *SEARCH_TERMS,
    #         urllib.parse.quote("language:" + SEARCH_LANGUAGE),
    #     ]

    # SEARCH_TERMS = [
    #     *SEARCH_TERMS,
    #     urllib.parse.quote("updated:") + "<" + urllib.parse.quote(ONE_YEAR_AGO),
    # ]

    ENCODED_SEARCH_TERMS = "+".join(map(lambda x: (x), SEARCH_TERMS))

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=f"{MCP_HOME_DIR}/_user_data_dir",
            headless=True,
        )

        page = await browser.new_page()

        await page.goto(getUrlToProbe(ENCODED_SEARCH_TERMS))
        await page.screenshot(path=DEBUG_PNG_PATH)

        # probe max page
        RESULTS_STR = await page.evaluate(PROBE_RESULT_JS)

        RESULT_JSON = json.loads(RESULTS_STR)
        RESULT_OK = RESULT_JSON["RESULT_OK"]
        FILE_FOUND_NUM = RESULT_JSON["FILE_FOUND_NUM"]

        if not (RESULT_OK):
            result_msg = "the page return is not ok"

            if float(FILE_FOUND_NUM) <= 0:
                result_msg = "no file found"

            return json.dumps(
                {
                    "probed_url": getUrlToProbe(ENCODED_SEARCH_TERMS),
                    "result": result_msg,
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

        MAX_PAGE_NUM = min(int(MAX_PAGE_NUM), 2)

        # should be no-error after this line
        pages = []
        for i in range(1, MAX_PAGE_NUM + 1):
            page = await browser.new_page()
            # await page.goto(getUrlSearchPageNum(ENCODED_SEARCH_TERMS, i))
            pages.append(page)

        await asyncio.gather(
            *[
                pages[i - 1].goto(getUrlSearchPageNum(ENCODED_SEARCH_TERMS, i))
                for i in range(1, MAX_PAGE_NUM + 1)
            ]
        )

        for i in range(1, MAX_PAGE_NUM + 1):
            logger.info("scaping page " + str(i))
            page = pages[i - 1]

            await page.wait_for_load_state("load", timeout=0)

            RESULTS_STR = await page.evaluate(PARSE_RESULT_JS)

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
                print("not logged in, break")
                break

        await browser.close()

        if len(FILE_LINKS) > 0:
            print("converting links")
            RAW_USER_CONTENT_LINKS = list(
                map(lambda x: convertFileLinkToRawGithubUserContentLink(x), FILE_LINKS)
            )

            async with aiohttp.ClientSession() as session:
                tasks = [fetch_data(session, url) for url in RAW_USER_CONTENT_LINKS]
                results = await asyncio.gather(*tasks)
                FILE_CONTENTS = results

        for i in range(0, min(len(FILE_LINKS), max_record_return)):
            output_meta.append(
                {
                    "REPOSITORY_LINK": REPOSITORY_LINKS[i],
                    "FILE_LINK": FILE_LINKS[i],
                    "RAW_USER_CONTENT_LINK": RAW_USER_CONTENT_LINKS[i],
                    "FILE_CONTENT": FILE_CONTENTS[i],
                }
            )

    with open("/tmp/result.json", "w") as f:
        json.dump(output_meta, f)

    if len(output_meta) > ITEM_PER_BATCH:
        return json.dumps(
            [
                *output_meta[0:ITEM_PER_BATCH],
                {
                    "next_instruction_md": f"result truncated, please use `get_remaining_result` with start_id={ITEM_PER_BATCH} to get the remaining result."
                },
            ]
        )
    else:
        return json.dumps(
            [*output_meta[0:ITEM_PER_BATCH], {"instructions": "all result returned."}]
        )


async def serve(repository: Path | None) -> None:
    logger = logging.getLogger(__name__)

    # if repository is not None:
    #     try:
    #         git.Repo(repository)
    #         logger.info(f"Using repository at {repository}")
    #     except git.InvalidGitRepositoryError:
    #         logger.error(f"{repository} is not a valid Git repository")
    #         return

    logger.info("starting")

    server = Server("mcp-git-gas")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=GitTools.HELLOWORLD,
                description="my helloworld call",
                inputSchema=GitHelloworld.model_json_schema(),
            ),
            Tool(
                name=GitTools.ENTRYPOINT,
                description="initialize git-gas, no parameters required",
                inputSchema=GitEntrypoint.model_json_schema(),
            ),
            # Tool(
            #     name=GitTools.DUMP_SCREEN,
            #     description="my dump screen call",
            #     inputSchema=GitDumpScreen.model_json_schema(),
            # ),
            Tool(
                name=GitTools.SEARCH_CODE,
                description=SEARCH_CODE_EXPLAIN_MD,
                inputSchema=GasSearchCode.model_json_schema(),
            ),
            Tool(
                name=GitTools.GET_REMAINING_RESULT,
                description=GET_REMAINING_RESULT_MD,
                inputSchema=GetRemainingResult.model_json_schema(),
            ),
        ]

    # async def list_repos() -> Sequence[str]:
    #     async def by_roots() -> Sequence[str]:
    #         if not isinstance(server.request_context.session, ServerSession):
    #             raise TypeError(
    #                 "server.request_context.session must be a ServerSession"
    #             )

    #         if not server.request_context.session.check_client_capability(
    #             ClientCapabilities(roots=RootsCapability())
    #         ):
    #             return []

    #         roots_result: ListRootsResult = (
    #             await server.request_context.session.list_roots()
    #         )
    #         logger.debug(f"Roots result: {roots_result}")
    #         repo_paths = []
    #         for root in roots_result.roots:
    #             path = root.uri.path
    #             try:
    #                 git.Repo(path)
    #                 repo_paths.append(str(path))
    #             except git.InvalidGitRepositoryError:
    #                 pass
    #         return repo_paths

    #     def by_commandline() -> Sequence[str]:
    #         return [str(repository)] if repository is not None else []

    #     cmd_repos = by_commandline()
    #     root_repos = await by_roots()
    #     return [*root_repos, *cmd_repos]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        from .git_dump_screen import git_dump_screen

        match name:
            case GitTools.SEARCH_CODE:
                result = await gas_search_code(arguments)
                return [TextContent(type="text", text=result)]

            case GitTools.GET_REMAINING_RESULT:
                result = await get_remaining_result(arguments)
                return [TextContent(type="text", text=result)]

            case GitTools.ENTRYPOINT:
                result = await gas_entrypoint()
                return [TextContent(type="text", text=result)]

            case GitTools.DUMP_SCREEN:
                result = await git_dump_screen(arguments)
                return [TextContent(type="text", text=result)]

            case GitTools.HELLOWORLD:
                result = await git_helloworld(arguments)
                return [TextContent(type="text", text=result)]

            case _:
                raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
