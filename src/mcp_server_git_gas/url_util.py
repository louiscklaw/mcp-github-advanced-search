# URL_TO_PROBE = f"https://github.com/search?q={ENCODED_SEARCH_TERMS}&type=code&ref=advsearch"


def getUrlToProbe(ENCODED_SEARCH_TERMS):
    return f"https://github.com/search?q={ENCODED_SEARCH_TERMS}&type=code&ref=advsearch"


def getUrlSearchPageNum(ENCODED_SEARCH_TERMS, page_num=1):
    return f"https://github.com/search?q={ENCODED_SEARCH_TERMS}&type=code&ref=advsearch&p={str(page_num)}"
