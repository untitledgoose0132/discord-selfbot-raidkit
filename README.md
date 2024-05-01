# Discord self-bot Raid-kit

Educational purposes only!
By using this program, you agree that I am not resposible for your usage of this program and you acknowledge that usage of this program violates Discord's ToS on self-bots!

## Foreword
Bot accounts excels at handling lots of requests while user accounts have much less capability, especially for raiding which can take thousands of requests. Therefore I recommend you use a bot account instead through the link below to Discord Raidkit

Discord self-bot Raid-kit is based on [Discord Raidkit](https://github.com/the-cult-of-integral/discord-raidkit/) made by [the-cult-of-integral](https://github.com/the-cult-of-integral/), rewritten to run with user tokens and a user-friendly GUI interface instead of bot commands

Most actions are self-explanatory through the prompts so you should be able to use this with ease

## How to obtain your own token (if none is found)
Read this [guide](https://gist.github.com/MarvNC/e601f3603df22f36ebd3102c501116c6) by [MarvNC](https://github.com/MarvNC)

## Features:
- **Automatic token extraction** removes the hassle of finding your own tokens by scanning for them on your local computer and providing a username preview next to each of them while still providing an option for entering your own tokens
Note: because of this, many antivirus softwares mark this program as malicious, this is a false positive. If you don't feel comfortable using the pre-compiled binary, you can build it from source or run directly (read Notes first)
- **Secure, user-friendly CLI**: This project uses [InquirerPy](https://github.com/kazhala/InquirerPy) to prompt for user input therefore removing the chance of being caught in an attempted raid
- **In-built interactive Python intepreter** allows the user to inspect and edit variables directly in the console
- **Commandless bot instance**: The bot instance in the code does not have any commands, meaning no one can control the bot aside from the script runner
- **Preemtive ratelimit warning**: Warns you if the current action you're about to do could cause 429s

## Note: fix the IndexError in discord.py-self
By default, discord.py-self has a guaranteed IndexError exception in .venv/Lib/site-packages/discord/utils.py at line 1469, all you need to do is simply replace that function with this
```
async def _get_build_number(session: ClientSession) -> int:
    return 289703  # last updated 2:21 AM May 1st 2024
```
This should fix the problem, the build number should not affect the program but you can periodically update it by checking the build number at the bottom of Discord's settings