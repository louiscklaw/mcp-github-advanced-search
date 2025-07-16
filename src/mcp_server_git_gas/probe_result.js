() => {
  RESULT_OK = true;

  LOGGED_IN_CHECK = false;
  try {
    document.querySelectorAll(
      'span[data-component="buttonContent"]>span[data-component="text"]'
    )[3].textContent;
    console.log("not logged in");
    RESULT_OK = false;
  } catch (error) {
    LOGGED_IN_CHECK = true;
    console.log("logged in");
  }

  MAX_PAGE_NUM = 0;
  try {
    MAX_PAGE_NUM = document
      .querySelectorAll("nav")[2]
      .textContent.replace("Next", "")
      .replace("Previous", "")
      .slice(-1);
  } catch (error) {
    MAX_PAGE_NUM = -1;
    RESULT_OK = false;
  }

  FILE_FOUND_NUM = 0;
  try {
    FILE_FOUND_NUM = document
      .querySelectorAll('div[data-testid="search-sub-header"] h2')[0]
      .textContent.toLowerCase()
      .replace(" files", "")
      .replace(" file", "")
      .replace("more than ", "")
      .replace("m", "")
      .replace("k", "")
      .trim();
  } catch (error) {
    FILE_FOUND_NUM = -1;
    RESULT_OK = false;
  }

  return JSON.stringify({
    RESULT_OK,
    LOGGED_IN_CHECK,
    MAX_PAGE_NUM,
    FILE_FOUND_NUM,
  });
};
