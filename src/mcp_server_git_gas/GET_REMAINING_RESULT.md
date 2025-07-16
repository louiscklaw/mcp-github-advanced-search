# GET_REMAINING_RESULT

## INTRODUCTION

This is a tools to get the remaining data searched by `gas_search_code`.
the result is in json format with below fields.

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

When you receive this,
please ensure you follow the `next_instructions_md` to collect all results.

You can also use `memory`, `sequential-thinking`, `structured-argumentation` to help solving problems.
