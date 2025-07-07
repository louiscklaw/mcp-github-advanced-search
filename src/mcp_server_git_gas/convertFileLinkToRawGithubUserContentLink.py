def convertFileLinkToRawGithubUserContentLink(github_link):
    return github_link.replace(
        "https://github.com/", "https://raw.githubusercontent.com/"
    ).replace("/blob/", "/")
