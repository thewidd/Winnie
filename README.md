# Winnie
Discord bot to notify server members that someone has started playing a game

## Python setup
- Required version: Python 3.8
- Dependent pip3 libs: (install with `pip3 install -U {name}`
  - [discord.py](https://pypi.org/project/discord.py/)
  - [ddt](https://ddt.readthedocs.io/en/latest/)
  - [load_dotenv](https://pypi.org/project/python-dotenv/)

## Steps for setup:
**1.** Visit https://discord.com/developers/applications and select "Winnie" in the applications section. If you are not a member of the development team, request access from the owner of this repo.

**2.** Select "Bot" in the left-hand column.

**3.** In the "Build-A-Bot" section, click "Copy" to get the token (next to the bot icon and name)

**4**. On your local checkout of the repo, create a local file named `.env` in the repo root directory.

**5.** Add the following lines:
```
BOT_NAME=Winnie
DISCORD_TOKEN={token}
```
where `{token}` is the token you just copied from step 3

**6.** From your terminal, run `python3 bot.py` or `python bot.py` depending on your python env setup for python 3 usage.
