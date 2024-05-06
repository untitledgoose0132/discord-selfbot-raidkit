import asyncio
import sys
import traceback
from code import compile_command
from logging import Logger, getLogger
from threading import Thread
from types import CodeType
from typing import Union

import discord
from discord.ext import commands
from InquirerPy.inquirer import confirm, secret, select  # type: ignore

from raid_ui import Raidkit
from tokengrabber import get_token

bot = commands.Bot(command_prefix=commands.when_mentioned)
log: Logger = getLogger("discord")
@bot.event
async def on_ready() -> None:
  assert bot.user is not None
  log.info(f"Logged in as {bot.user.name} ({bot.user.id})")
  Thread(target=menu).start()
def console() -> None:
  print(f"Python {sys.version}\nUse quit(), exit(), Ctrl-C or raise EOFError() to return to menu")
  while True:
    try:
      i: str = input(">>> ")
      if i in ["quit()", "exit()"]:
        return
      o: Union[CodeType, None] = compile_command(i)
      while o is None:
        try:
          i += "\n" + input("... ")
        except EOFError:
          i = ""
          break
        o = compile_command(i)
      if o is not None:
        exec(o)
    except EOFError:
      print("\n")
      return
    except Exception as e:
      traceback.print_exception(e, limit=10)
def menu() -> None:
  while True:
    sel = int(select("What do you want to do?", [
        "1. Open Raid-kit menu",
        "2. Open Python intepreter",
        "3. Exit self-bot"
      ],
      raise_keyboard_interrupt=False,
      mandatory=True,
      mandatory_message="Please select exit from the menu instead of using Ctrl-C!"
    ).execute().split(".")[0])
    if sel == 1:
      Raidkit(bot).raidkit_menu()
    elif sel == 2:
      console()
    elif sel == 3:
      sys.exit()
def main() -> None:
  tokens: dict[str, str] = get_token()
  tokens.update({"Input my own token": "undefined-username"})
  try:
    re: str = select("Select a token:", [f"{i+1}. {k[:18] + "*"*(len(k)-50)} ({v})" for i, (k, v) in enumerate((tokens).items())]).execute()
    if not re.endswith("Input my own token"):
      token: str = list(tokens.keys())[int(re.split(".")[0])-1]
    else:
      token = secret("Input your own token:", transformer=lambda t: t[:18] + "*"*(len(t)-18)).execute()
  except KeyboardInterrupt:
    sys.exit()
  try:
    bot.run(token)
  except asyncio.CancelledError:
    return
  except discord.LoginFailure:
    if confirm("Input token is invalid! Do you want to reveal input token?", raise_keyboard_interrupt=False, default=False).execute():
      print(f"The input token was {token}")
if __name__ == "__main__":
  main()