# Discord

**Status**: draft.

## Detect

A Discord MCP server or bot token reference. Ask for the review channel.

## Profile config

`{"channels": {"review": [{"name": "#reviews", "id": "<snowflake>"}]}, "token_ref": "env:DISCORD_BOT_TOKEN"}`

## Operations

- `post`, `my_messages_today`, `find_links`: through the configured MCP server's message tools.
