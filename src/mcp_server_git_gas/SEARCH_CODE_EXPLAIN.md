# SEARCH_CODE_EXPLAIN

## INTRODUCTION

This is a utilities that search github with advanced filters
(e.g. keyword)

the result is in json format with below fields"

```json
[
    {
        "REPOSITORY_LINK": "<repository-found>",
        "FILE_LINK": "<file-found>",
        "RAW_USER_CONTENT_LINK": "<download-link-to-the-file>",
        "FILE_CONTENT": "<downloaded-content>"
    },
    {...},
    {...},
    {...},
    {"next_instructions_md": "<contains-the-instruction-to-get-the-remaining-result>"}
]
```

when you receive this,
please ensure you follow the `next_instructions_md` to collect all results.

You can use `memory`, `sequential-thinking`, `structured-argumentation` to help solving problems.
