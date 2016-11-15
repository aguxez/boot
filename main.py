#!/usr/bin/env python
import discord
import asyncio
import logging
import requests
from discord.ext import commands



# https://discordapp.com/oauth2/authorize?client_id=236258854546046977&scope=bot&permissions=0


logging.basicConfig(level=logging.INFO)
client = discord.Client()


# DISCORD AUTH
bot = commands.Bot(command_prefix="-")
bot.remove_command('help')
logging.basicConfig(level=logging.INFO)

startup_ext = ['commands.music']


@bot.async_event
def main():
    yield from bot.login(Your API Key)
    yield from bot.connect()


# All client async events code from here
@bot.async_event
def on_ready():
    yield from bot.change_presence(game=discord.Game(name='games to find'))
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print('-' * 10)


@bot.async_event
def on_message(message):
    if message.content.startswith("find"):
        name_sub = message.content[len("find"):].strip()

        name = name_sub.replace(" ", "")

        r = requests.get("https://lan.api.pvp.net/api/lol/lan/v1.4/summoner"
                         "/by-name/{}?api_key=RGAPI-cfdd3412-0561-4380-a341-53afd1a0881e".format(name)).json()

        summ_id = r[''.replace('', name).lower()]['id']

        r_match = requests.get("https://lan.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo"
                               "/LA1/{}?api_key=Your-Api-KEY"
                               .format(summ_id)).json()
        try:
            num = -1
            ids_seen = set()
            for g in range(0, 10):
                try:
                    num += 1
                    i = r_match['participants'][num]
                    e_name = i['summonerName']
                    e_id = i['summonerId']
                    team_id = i['teamId']
                    champ = i['championId']

                    r_team = requests.get("https://lan.api.pvp.net/api/lol/lan/v2.5/league/by-summoner/{}/"
                                          "entry?api_key=Your-Api-KEY"
                                          .format(e_id)).json()

                    champ_r = requests.get("https://global.api.pvp.net/api/lol/static-data/lan/v1.2/champion?"
                                           "api_key=Your-Api-KEY").json()

                    x = r_team["{}".format(e_id)][0]
                    e_tier = x['tier']
                    e_div = x['entries'][0]['division']

                except KeyError as e:
                    if e not in ids_seen:
                        while True:
                            e_name = i['summonerName']
                            team_id = i['teamId']
                            champ = i['championId']

                            champ_r = requests.get(
                                "https://global.api.pvp.net/api/lol/static-data/lan/v1.2/champion?"
                                "api_key=Your-Api-KEY").json()

                            for key, value in champ_r['data'].items():
                                c_name = value['name']
                                c_id = value['id']

                                chat_say = "{} - **Unranked** - Playing `#{}`".format(e_name, c_name)

                                if champ == c_id:
                                    if team_id == 100:
                                        if team_id not in ids_seen:
                                            yield from bot.send_message(message.channel, "```---Blue team---```")
                                        yield from bot.send_message(message.channel, chat_say)

                                    elif team_id == 200:
                                        if team_id not in ids_seen:
                                            yield from bot.send_message(message.channel, "```--- Red team ---```")
                                        yield from bot.send_message(message.channel, chat_say)
                            ids_seen.add(team_id)
                            break
                        ids_seen.add(e)

                else:
                    for key, value in champ_r['data'].items():
                        c_name = value['name']
                        c_id = value['id']

                        chat_say = "{} - **{} {}** - Playing `#{}`".format(e_name, e_tier, e_div, c_name)

                        if champ == c_id:
                            if team_id == 100:
                                if team_id not in ids_seen:
                                    yield from bot.send_message(message.channel, "```---Blue team---```")
                                yield from bot.send_message(message.channel, chat_say)

                            elif team_id == 200:
                                if team_id not in ids_seen:
                                    yield from bot.send_message(message.channel, "```--- Red team ---```")
                                yield from bot.send_message(message.channel, chat_say)

                    ids_seen.add(team_id)

            yield from asyncio.sleep(1.5)

        except:
            yield from bot.send_message(message.channel, "**No active match found**")

logging.basicConfig(level=logging.INFO)


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
except:
    loop.run_until_complete(client.logout())
finally:
    loop.close()
