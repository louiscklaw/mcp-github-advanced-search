async () => {
  response = await fetch(location.href);

  LOGGED_IN_CHECK = false;
  try {
    document.querySelectorAll(
      'span[data-component="buttonContent"]>span[data-component="text"]'
    )[3].textContent;
    console.log("not logged in");
  } catch (error) {
    LOGGED_IN_CHECK = true;
    console.log("logged in");
  }

  REPOSITORY_LINKS_FETCHED = [];
  document
    .querySelectorAll('div.search-title a[aria-keyshortcuts="Alt+ArrowUp"]')
    .forEach(
      (a) => (REPOSITORY_LINKS_FETCHED = [...REPOSITORY_LINKS_FETCHED, a.href])
    );

  FILE_LINKS_FETCHED = [];
  document
    .querySelectorAll(
      'div.search-title a:not([aria-keyshortcuts="Alt+ArrowUp"]'
    )
    .forEach((a) => (FILE_LINKS_FETCHED = [...FILE_LINKS_FETCHED, a.href]));

  return JSON.stringify({
    LOGGED_IN_CHECK,
    REPOSITORY_LINKS_FETCHED,
    FILE_LINKS_FETCHED,
  });
};
