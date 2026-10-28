# Chat contract

| Operation | Input | Output |
|---|---|---|
| `post` | channel (by purpose: `review`, `team`), formatted message | message link |
| `my_messages_today` | channel | the user's messages since 00:00 local time, **full text** |
| `find_links` | channel, period | messages from others that contain MR/PR links |

Rules: a nudge about a MR/PR is sent at most once per MR/PR per day, whoever sent the previous one
(the user by hand included). Each sent nudge is also recorded in `state/pilot/nudges.json`. If the
search fails, nothing is sent.
