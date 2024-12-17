# getting tokens
import os
from dotenv import load_dotenv

# getting yt audio and searching youtube
import yt_dlp
from youtube_search import YoutubeSearch

# regex
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re


import json

# functional
import asyncio
import random
import typing
from io import BytesIO
from datetime import datetime

# genius client
from lyricsgenius import Genius

# spotify client
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# meme
import requests
import urllib

# Getting tokens
load_dotenv()
TOKEN = os.environ.get('TOKEN')
client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')
genius_token = os.environ.get('genius_token')
flieger_token = os.environ.get('flieger_token')

# discord client imports
import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord import TextChannel
from typing import List
from typing import Optional

# Setting up discord client
intents = discord.Intents.all()
client = discord.Client(intents=intents)
activity = discord.Game(name="Music", type=discord.ActivityType.playing)
bot = commands.Bot(command_prefix='!', intents=intents, activity=activity)
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
# DISCORD

# setting up spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# setting up genius client
genius = Genius(genius_token)
skip = False

logging = {}
ping_info = {}


# run when bot is ready
@bot.event
async def on_ready():
    global most_important
    global logging
    # log to console
    print("Lynx online")
    try:
        # sync application commands
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)
    
    try:
        important = open('mostimportant.txt', 'r')
        most_important = important.readlines()
    except:
        print("copypasta parse failed")


    try:
        with open("logginginfo.json", "r") as read_file:
            global logging
            logging = json.load(read_file)
            for info in logging:
                logging[info]["log"]

                logging[info]["logging_channel"] = int(logging[info]["logging_channel"])
    except Exception as e:
        print("logging file empty", e)
    try:
        with open("pinginfo.json", "r") as read_file:
            global ping_info
            ping_info = json.load(read_file)
        to_delete = []
        for word in ping_info:
            if ping_info[word] == None:
                to_delete.append(word)
        for delete in to_delete:
            del ping_info[delete]
    except Exception as e:
        print("ping file empty", e)


# setting up imgflip for /meme
username = 'MusicLynx'
password = os.environ.get('imgflip')
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \ AppleWebKit/537.36 (KHTML, like Gecko) \ Chrome/120.0.0.0 Safari/537.36"

data = requests.get('https://api.imgflip.com/get_memes').json()['data']['memes']
images = [{'name': image['name'], 'url': image['url'], 'id': image['id']} for image in data]
meme_names = []
for image in images:
    meme_names.append(image['name'])


# get command help
@bot.tree.command(name="lynx_help", description="lists the bot's commands")
async def lynx_help(interaction: discord.Interaction):
    await interaction.response.send_message(f"""
**Disclaimer**: the player disconnects frequently from YT's end, so there's little i can do to fix that. sorry.
`/link [song]` links to a song.
`/join` you have to get the bot to join a voice channel before it can play. if it's having errors, always try to run this first.
`/play [song]` plays the song you enter. ideal format: [artist] [song] [explicit/clean]. queues song if something's already playing.
`/queue [clear/view]` prints or clears the queue.
`/resume` resumes playing song.
`/pause` pauses song.
`/skip` skips song.
`/stop` stops playing and leaves the vc.\n
`!sing` sends the lyrics of the song you enter one-by-one. use carefully, or you might get banned :D
`!shout` SHOUTS the lyrics of the song you enter one-by-one. use carefully, or you might get banned :D
`!stop` stops sending lyrics.
`!time` adjusts the time between each line\n
`!preach` spits straight facts.
`!rickroll` rickrolls.
`!hype` sends GT hype.
`!nerd user` when someone is being far too much of a nerd, nerd them.
`/doggo` summons a random doggo pic.
`/8ball [question]` answers questions by harnessing the peak reasoning abilities of a UGA student.
`/meme [template] [public] [line1] [line2] [line3 (opt.)] [line4 (opt.)]` generates meme\n

if you want to delete a reply i sent to your message, react with 🗑️
pls use me responsibly.
""", ephemeral=True)


fax = ["CS majors should get free deodorant", "It's not immoral if you make six figures", "To Hell With Georgia",
       "I don't talk to UGA grads often, but when I do, I ask for large fries", "MIT is GT of the North",
       "Touch grass, buddy",
       "mods are nepo smh", "The art and the artist are separate", "Dobby is a free elf", "PJO >>",
       "The laws of physics don't apply to SRK",
       "The 'clay' in 'Mlepclaynos' is silent", "You heard about Pluto? That's messed up right?",
       "You the king, burger king",
       "I have two rules. Rule one: I'm always right. Rule two: If I'm wrong, refer to rule one…",
       "I just love the smell of C4 in the morning.", "It smell like gaaas, I think somebody poo",
       "I take my shirt off and all the hoes stop breathin'",
       "Deutschland > France", "SLATT", "Fuck UGA ong", "Fuck UGA ong", "Fuck UGA ong", "Fuck UGA", "Fuck UGA", "GT>>",
       "GT>>",
       "Pickup trucks are for idiots", "Bhupendra Jogi", "The best racism is Formula 1",
       "Lewis Hamilton is the greatest racist of all time",
       "Messi is the :goat:", "Messi > Ronaldo", "LeBron is my pookie", "LeBron GOAT",
       "Real football is played with the feet", "American Eggball != Football",
       "Lucas Luwa teaches CS1331", "Georgia _ech is _he bes_ ", "OJ is innocent- orange juice can't commit crimes",
       "The Superbowl was scripted",
       "OO is a myth.", "It's pronounced 'Chad' Starner", "you = :nerd:", ":nerd:", "you = :nerd:", ":moyai:",
       ":moyai:",
       "I'm really happy for you, Imma let you finish, but Beyoncé had one of the best videos of all time!",
       "Man U will always be dogshit", "Barca > Madrid",
       "Bayern cheat", "Animal testing is a crime", "Math majors have no life purpose",
       "The existence of Ivan Allen is a myth", "East Campus is better",
       "Willage is overrated", "Coffee is a performance drug\nPerformance drugs are the best!", "Willage is overrated",
       "Everyone secretly wishes they were in CS",
       "Georgia > Florida", "Bigotry is **not** cool",
       "If I get bleach on my t-shirt, Imma feel like an asshole",
       "992 > 991", "Macans are not Porsches", "SUVs are dumb", "SAT > ACT"]


# utility function to get urls from search term
def get_links(query):
    # spotify

    results = sp.search(q=query, type="track", limit=1)
    # basic conditional to handle search failure
    if results["tracks"]["items"]:
        spotify_url = results["tracks"]["items"][0]["external_urls"]["spotify"]
    else:
        raise Exception("Search Failed!")

    # genius
    hits = genius.search_songs(query)
    # if the search is successful, this'll get changed later
    genius_song = "Genius Search Failed"
    hits = hits["hits"]

    # making sure that the two results match closely. genius search can be weird.
    try:
        for hit in hits:
            genius_title = hit['result']['title']
            spotify_title = results['tracks']['items'][0]['name']
            if fuzz.ratio(str(genius_title), str(spotify_title)) > 60:
                genius_song = hit
                break
        genius_url = genius_song['result']['url']
    except Exception as e:
        print(e)
        genius_url = "genius search failed"

    # return the genius url, the spotify url, and the genius song object
    return genius_url, spotify_url, genius_song


# get links to a song query
@bot.tree.command(name="link", description="links to the song given in the query")
@app_commands.describe(song="I'll link to this song!")
async def link(interaction: discord.Interaction, song: str):
    # parsing my janky lil return string
    song = song.split("é")
    song_name = song[1]
    spotify_link = song[0]


    hits = genius.search_songs(song_name)
    # if the search is successful, this'll get changed later
    genius_song = "Genius Search Failed"
    hits = hits["hits"]

    # making sure that the two results match closely. genius search can be weird.
    try:
        for hit in hits:
            genius_title = hit['result']['title']
            spotify_title = song_name
            if fuzz.ratio(str(genius_title), str(spotify_title)) > 60:
                genius_song = hit
                break
        genius_url = genius_song['result']['url']
    except Exception as e:
        print(e)
        genius_url = "Genius search failed"
    
    await interaction.response.send_message(f"Genius: {genius_url}\nSpotify: {spotify_link}")

@link.autocomplete("song")
async def template_autocomplete(interaction: discord.Interaction, current: str) -> typing.List[
    app_commands.Choice[str]]:
    data = []
    # getting results from spotify client
    results = sp.search(q=current, type="track", limit=8)
    for song in results['tracks']['items']:
        if current.lower() in song["name"].lower():
            data.append(app_commands.Choice(name = f'{song["name"]}- {song["artists"][0]["name"]}', value = f'{song["external_urls"]["spotify"]}é{song["name"]}'))
    return data

# get top url for a query in YT
def get_top_result_url(query):
    results = YoutubeSearch((query + " audio"), max_results=10).to_dict()
    top_result_url = 'https://music.youtube.com' + results[0]['url_suffix']
    return {'url': top_result_url, 'title': results[0]['title'], 'thumbnail': results[0]['thumbnails'][0]}


# command for bot to join the channel of the user, if the bot has already joined and is in a different channel, it will move to the channel the user is in
@bot.tree.command(name="join", description="joins the user's vc")
async def join(interaction: discord.Interaction):
    try:
        channel = interaction.user.voice.channel
        voice = get(bot.voice_clients, guild=interaction.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
        await interaction.response.send_message("joined channel.")
    except:
        await interaction.response.send_message("you might have to join a vc first.")


queue = {}
queue_info = {}
nerded = {}


# command to play sound from a youtube URL
@bot.tree.command(name="play", description="plays the song in the query")
@app_commands.describe(song="I'll play this song")
async def play(interaction: discord.Interaction, song: str):
    global queue
    global user_id
    # the search takes a while, so the response is deferred to make sure the interaction doesn't time out
    await interaction.response.defer()

    # setting options
    YDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    # getting the vc object
    voice = get(bot.voice_clients, guild=interaction.guild)

    # kinda useless code
    if interaction.guild.id not in queue:
        queue[interaction.guild.id] = []
        queue_info[interaction.guild.id] = []
    if song == "skip":
        if len(queue[interaction.guild.id]) == 0:
            await interaction.followup.send("queue complete")
    queue[interaction.guild.id].append((song, interaction.user.id))
    queue_info[interaction.guild.id].append(interaction.user.id)

    # try-catch to handle vc errors and whatnot
    try:
        yt = get_top_result_url(song)
        song_url = yt["url"]
        embed = discord.Embed(title=yt['title'], url=song_url, description='Song added to queue')
        embed.set_author(name=f"queued by {interaction.user.display_name}", icon_url=interaction.user.display_avatar)
        embed.set_image(url=yt['thumbnail'])
        # making sure the bot isn't already playing
        if (not voice.is_playing()) or (len(queue[interaction.guild.id]) < 1):
            user_id = queue[interaction.guild.id][0][1]
            song = (queue[interaction.guild.id].pop(0))[0]
            yt = get_top_result_url(song)
            song_url = yt["url"]
            embed = discord.Embed(title=yt['title'], url=song_url, description='Song playing now')
            embed.set_author(name=f"played by {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar)
            embed.set_image(url=yt['thumbnail'])
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(song_url, download=False)
                url2 = info['url']
            # Play the audio stream
            voice.is_playing()
            id = interaction.guild.id
            voice.play(discord.FFmpegPCMAudio(url2, before_options=FFMPEG_OPTIONS),
                       after=lambda e: play_recur(voice, (queue[id].pop(0)), id))
            await interaction.followup.send(f"playing now", embed=embed)
            # check if the bot is already playing
        else:
            # a little message to the user
            await interaction.followup.send(f"added to queue", embed=embed)
            return
    except Exception as e:
        # doesn't work great without this block for some reason
        print(e)
        try:
            await interaction.followup.send(
                "there might have been an error. wait for a couple of secs and try again.\nmake sure you ran /join.",
                ephemeral=True)
        except:
            await interaction.followup.send(f"playing now\n{song_url}")


@bot.tree.command(name="queue", description="clears or prints the queue")
@app_commands.choices(action=[
    app_commands.Choice(name="View", value="view"),
    app_commands.Choice(name="Clear", value="clear"),
])
async def get_queue(interaction: discord.Interaction, action: app_commands.Choice[str]):
    global queue
    global queue_info
    global user_id
    await interaction.response.defer()
    try:
        if action == "clear":
            queue[interaction.guild.id] = []
            await interaction.followup.send("queue cleared!")
        else:
            song_titles = []
            for i, song in enumerate(queue[interaction.guild.id]):
                results = YoutubeSearch((song[0] + " audio"), max_results=10).to_dict()
                title = results[0]['title']
                user_id = queue_info[interaction.guild.id][i][1]
                song_titles.append(f"{i + 1}) **{title}**- added by <@{user_id}>")
            song_titles = "\n".join(song_titles)
            await interaction.followup.send(song_titles)
    except:
        await interaction.followup.send("u fucked something up lol.")


# recurring command to play from queue
def play_recur(voice, song, id):
    global user_id
    print(song)
    user_id = song[1]
    song = song[0]
    url = get_top_result_url(song)["url"]
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
    # Play the audio stream
    voice.is_playing()
    try:
        voice.play(discord.FFmpegPCMAudio(url2, before_options=FFMPEG_OPTIONS),
                   after=lambda e: play_recur(voice, (queue[id].pop(0)), id))
    except:
        pass


# command to resume voice if it is paused
@bot.tree.command(name="resume", description="resumes playing music")
async def resume(interaction: discord.Interaction):
    voice = get(bot.voice_clients, guild=interaction.guild)
    try:
        if not voice.is_playing():
            await voice.resume()
            await interaction.response.send_message("cool, i'll resume")
    except:
        await interaction.response.send_message("cool, i'll resume")


# command to pause voice if it is playing
@bot.tree.command(name="pause", description="pauses the music")
async def pause(interaction: discord.Interaction):
    voice = get(bot.voice_clients, guild=interaction.guild)
    try:
        if voice.is_playing():
            await voice.pause()
            await interaction.response.send_message('aight, paused')
    except:
        await interaction.response.send_message("aight, paused")


# command to stop voice
@bot.tree.command(name="stop", description="stops playing music and disconnects from vc")
async def stop(interaction: discord.Interaction):
    voice = get(bot.voice_clients, guild=interaction.guild)
    try:
        await voice.disconnect()
        await interaction.response.send_message("stopping and disconnecting...")
    except:
        await interaction.response.send_message("error. the bot might not be in a vc")


# command to skip song
# yet to implement voteskip
@bot.tree.command(name="skip", description="skips a song")
async def skip(interaction: discord.Interaction):
    global queue
    voice = get(bot.voice_clients, guild=interaction.guild)
    if user_id == interaction.user.id:
        try:
            await voice.stop()
            play_recur(voice, queue[interaction.guild.id].pop(0))
            await interaction.response.send_message("skipped")
        except:
            await interaction.response.send_message("skipped")
    else:
        await interaction.response.send_message("only the person who added the song can skip")


# fun
@bot.tree.command(name="8ball", description="answers a question using a UGA-tier decision tree")
@app_commands.describe(question="I'll answer this question")
async def eight_ball(interaction: discord.Interaction, question: str):
    await interaction.response.defer()

    answer = random.choice(
        ["It is certain", "Reply hazy, try again", "Don’t count on it", "It is decidedly so", "Ask again later",
         "My reply is no", "Without a doubt", "Better not tell you now", "My sources say no", "Yes definitely",
         "Cannot predict now", "Outlook not so good", "You may rely on it", "Concentrate and ask again",
         "Very doubtful", "As I see it, yes", "Most likely", "Outlook good", "Yes", "Signs point to yes"])
    await asyncio.sleep(3)

    if ("uga" in question.lower()) or ("university of georgia" in question.lower()):
        answer = "Man fuck UGA"

    await interaction.followup.send(f"**Magic 8-ball**\nQuestion: {question}\nMagic 8-ball's Answer: `{answer}`")



@bot.tree.command(name="meme", description="generates a meme that is visible to only you, or the entire server")
@app_commands.choices(public=[
    app_commands.Choice(name="Public", value="False"),
    app_commands.Choice(name="Private", value="True"),
])
@app_commands.describe(template="Template to use", public="Whether or not you want everyone to see what you generate",
                       line1="First line of meme", line2="Second line of meme", line3="Optional third line",
                       line4="Optional fourth line")
async def meme(interaction: discord.Interaction, template: str, public: app_commands.Choice[str], line1: str,
               line2: str, line3: str = None, line4: str = None):
    public_bool = eval(public.value)
    await interaction.response.defer(ephemeral=public_bool)
    URL = 'https://api.imgflip.com/caption_image'
    id = meme_names.index(template)
    boxes = [{"text": line1}, {"text": line2}, {"text": line3}, {"text": line4}]
    params = {
        'username': username,
        'password': password,
        'template_id': images[id]['id'],
        "boxes[0][text]": line1,
        "boxes[1][text]": line2,
        "boxes[2][text]": line3,
        "boxes[3][text]": line4,
    }
    response = requests.request('POST', URL, params=params).json()
    opener = urllib.request.URLopener()
    opener.addheader('User-Agent', user_agent)
    try:
        filename, headers = opener.retrieve(response['data']['url'], 'meme.jpg')
    except Exception as e:
        print(e)
    with open('meme.jpg', 'rb') as img:
        picture = discord.File(img)
        await interaction.followup.send(f"made by <@{interaction.user.id}>", file=picture, ephemeral=public_bool)


@meme.autocomplete("template")
async def template_autocomplete(interaction: discord.Interaction, current: str) -> typing.List[
    app_commands.Choice[str]]:
    data = []
    for template_choice in meme_names:
        if current.lower() in template_choice.lower():
            data.append(app_commands.Choice(name=template_choice, value=template_choice))
    return data


# show meme
@bot.tree.command(name="meme_templates", description="lists meme templates")
async def list_templates(interaction: discord.Interaction):
    as_bytes = map(str.encode, meme_names)
    content = b"\n".join(as_bytes)
    await interaction.response.send_message("Meme Templates", file=discord.File(BytesIO(content), "templates.txt"),
                                            ephemeral=True)


# send a random photo of a dog
lastdog = 0
doggo_credits = [("Meru", 799447829856780289), ("Meru", 799447829856780289), ("Meru", 799447829856780289),
                 ("Kira", 190611013232492544), ("Annie", 191576992682868738), ("Annie", 191576992682868738)]


@bot.tree.command(name="doggo", description="sends a random pic of a dog")
async def skip(interaction: discord.Interaction):
    global lastdog
    rand = random.randint(1, 6)
    while rand == lastdog:
        rand = random.randint(1, 6)
    lastdog = rand
    with open(f'dog{rand}.png', 'rb') as img:
        picture = discord.File(img)
        await interaction.response.send_message(
            f"{doggo_credits[rand - 1][0]}, <@{doggo_credits[rand - 1][1]}>'s doggo.", file=picture, silent=True)


lastcat = 0
cat_credits = [109895389544484864, 491364750106558464, 445257802198417408, 121700801612742656, 748540576651280454, 694358844897492994]


@bot.tree.command(name="car", description="sends a random pic of a car")
async def skip(interaction: discord.Interaction):
    global lastcat
    rand = random.randint(1, 6)
    while rand == lastcat:
        rand = random.randint(1, 6)
    lastcat = rand
    with open(f'cat{rand}.png', 'rb') as img:
        picture = discord.File(img)
        await interaction.response.send_message(f"<@{cat_credits[rand - 1]}>'s car.", file=picture, silent=True)


@bot.tree.command(name="game_night", description="sends an embed to schedule a game night")
@app_commands.describe(heading="Heading", month="Month", day="Day", hour="Hour", minute="Minute", duration="Duration")
async def schedule_game_night(interaction: discord.Interaction, heading: str, month: int, day: int, hour: int,
                              minute: int, duration: int):
    if interaction.user.id in (
            [286225309773070336, 799447829856780289, 651632296440365087, 694310264295915560, 549393343583485962,
             946196592074031165]):
        try:
            event_date = datetime(year=2024, month=month, day=day, hour=hour, minute=minute)
            embed = discord.Embed(title="Game Night", description="It's Game Night, y'all :tada:!", color=0xB3A369)
            embed.set_author(name=f"Scheduled by {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar)
            embed.set_image(url="https://i.imgur.com/rN1jSHJ.png")
            embed.add_field(name="Duration:", value=f"{duration} hours")
            embed.add_field(name="Date:", value=f"<t:{int(event_date.timestamp())}>")
            await interaction.response.send_message(f"# {heading.strip()}", embed=embed)
        except Exception as e:
            print(e)
            await interaction.response.send_message("invalid input", ephemeral=True)
    else:
        await interaction.response.send_message("you don't have the perms for that buddy", ephemeral=True)


@bot.tree.command(name="ping",
                  description="allows you to set keywords/phrases so that you can be pinged everytime they're mentioned")
@app_commands.choices(action=[
    app_commands.Choice(name="Enable", value="enable"),
    app_commands.Choice(name="Disable", value="disable"),
    app_commands.Choice(name="View", value="view")
])
@app_commands.describe(keyword="Word or phrase to ping you for", action="what action to take")
async def ping_watch_setup(interaction: discord.Interaction, action: app_commands.Choice[str], keyword: str = None):
    action = action.value
    to_delete = []
    try:
        for word in ping_info:
            print(word, ping_info[word])
            if ping_info[word] == None:
                # print(word, ping_info[word])
                to_delete.append(word)
        for delete in to_delete:
            del ping_info[delete]
    except:
        pass
    if action == "view":
        keywords = ""
        try:
            for word in ping_info:
                if interaction.user.id in ping_info[word]:
                    keywords += f"- '{word}'\n"
            if keywords != "":
                await interaction.response.send_message(
                    f"{keywords}You have pings enabled for the above words/phrases.")
            else:
                await interaction.response.send_message("you don't have any pings set up")
        except:
            await interaction.response.send_message("you don't have any pings set up")
        return
    if action == "enable" and keyword != ".*":
        if keyword in ping_info and (keyword != None):
            if interaction.user.id in ping_info[keyword]:
                await interaction.response.send_message(f"you're already in the ping list for mentions of '{keyword}'.")
            else:
                await interaction.response.send_message(
                    f"you've been added to the ping list for mentions of '{keyword}'!")
                ping_info[keyword].append(interaction.user.id)
        elif keyword != None:
            ping_info[keyword] = [interaction.user.id]
            await interaction.response.send_message(f"ping for mentions of '{keyword}' set up!")
        else:
            await interaction.response.send_message(f"you must provide a keyword")
    if action == "disable":
        if keyword in ping_info and (keyword != None):
            ping_info[keyword] = ping_info[keyword].remove(interaction.user.id)
            await interaction.response.send_message(f"pinging disabled for mentions of '{keyword}'")
        elif (keyword != None):
            await interaction.response.send_message("you have not enabled pinging for this keyword")
        else:
            for word in ping_info:
                try:
                    ping_info[word] = ping_info[word].remove(interaction.user.id)
                except:
                    pass
            await interaction.response.send_message("all pings disabled for you.")
    else:
        await interaction.response.send_message("That ping is illegal :moyai:")

    with open("pinginfo.json", "w") as write_file:
        json.dump(ping_info, write_file)

# bot reply delete functionality. doesn't work with slash commands as of now.
@bot.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    if (message.reference is not None) and (message.author.id == 1196931379129241600):
        print("step 1")
        replied_to = await message.channel.fetch_message(message.reference.message_id)
        if replied_to.author.id == user.id:
            print("step 2")
            if reaction.emoji == "🗑️":
                await message.delete()

@bot.event
async def on_message(message):
    if not message.author.bot:
        # amuhak's checker 🎉🎉🎉
        if (message.guild.id == 1182890708265357392) and (not message.flags.silent):
            to_ping = []
            why_ping = []
            for word in ping_info:
                if regex_match(word.lower(), message.content.lower()):
                    if type(ping_info[word]) is list:
                        for id in ping_info[word]:
                            # print(ping_info[word], message.author.id)
                            why_ping.append(word)
                            to_ping.append(id)
                            try:
                                to_ping.remove(message.author.id)
                            except:
                                pass
                    elif ping_info[word] is int:
                        if message.author.id != ping_info[word]:
                            print(ping_info[word], message.author.id)
                            why_ping.append(word)
                            to_ping.append(ping_info[word])
                    else:
                        print(f"Error: ping_info[word] is neither a list nor a int it is {type(ping_info[word])}")
            if to_ping:
                ask_boomers = discord.utils.get(message.guild.channels, name="bot-commands")
                string_to_send = f"<@{message.author.id}> mentioned:\n"
                if len(why_ping) != len(to_ping):
                    print(f"Error: why_ping, {why_ping} and to_ping, {to_ping} are not the same length. This should "
                          f"not happen.")
                for why, to in zip(why_ping, to_ping):
                    string_to_send += f"- {why}, pinging <@{to}>\n"
                await ask_boomers.send(string_to_send + f"{message.jump_url}", silent=True)

    # checking if the sender of a message has been "nerded"

    if message.author.id in nerded:
        # incrementing number of messages sent while nerded
        nerded[message.author.id] += 1
        # adding reaction
        await message.add_reaction("🤓")
        await message.add_reaction("☝️")
        # removing from nerd directory if the 2 messages have already been reacted to
        if nerded[message.author.id] >= 2:
            del nerded[message.author.id]

    await bot.process_commands(message)

@bot.command(name="preach", help="spits straight facts")
async def preach(ctx):
    global fax
    await ctx.send(random.choice(fax))
    await ctx.message.delete()

# send reaction when bean
@bot.command(name="bean")
async def bean_lynx(ctx):
    await ctx.send(random.choice(["bruh why bean", "get beaned lol"]))


# send reaction when ban
@bot.command(name="ban")
async def ban_lynx(ctx):
    await ctx.send("🙀")

# command to nerd someone
@bot.command(name="nerd", help="nerds someone")
async def nerd(ctx, member: discord.Member):
    # global dictionary of people who have been "nerded"
    global nerded
    # initializing how many messages they have sent while nerded
    if (member.id == 799447829856780289):
        nerded[ctx.author.id] = 0
        await ctx.send(f"# <@{ctx.author.id}> = :nerd:\nlmao get nerded noob")
    elif (member.id == 1196931379129241600):
        await ctx.send("you dare use my own spells against me?")
    else:
        nerded[member.id] = 0
        await ctx.send(f"# <@{member.id}> = :nerd:")

last_aarush = 0
@bot.command(name="aarush", help="pings a random aarush")
async def aarush(ctx):
    global last_aarush
    server_members = ctx.guild.members
    tags = []
    for member in server_members:
        if "aarush" in (member.display_name.strip()).lower():
            tags.append(member.id)
    chosen_aarush = random.choice(tags)
    while chosen_aarush == last_aarush:
        chosen_aarush = random.choice(tags)
    last_aarush = chosen_aarush
    await ctx.send(f"an aarush -> <@{chosen_aarush}>")
    await ctx.message.delete()

aaron_id = "<@324657044647051266>"
aaronn9981glaze = [f"{aaron_id} is so rich, Jeff Bezos asked him for a loan", f"{aaron_id} is so good at poker, Phil Ivey tried to sign up for his bootcamp", f"{aaron_id} is so smart, he interviewed Jane Street for a job", f"{aaron_id} has such a high GPA, he needs to use scientific notation", f"{aaron_id} is so good at Fortnite, he taught Epic Games how to play it"]

@bot.command(name="aaron", help="aaron9981")
async def aaron9981(ctx):
    glaze = random.choice(aaronn9981glaze)
    await ctx.send(glaze)
    await ctx.message.delete()
    

@bot.command(name="hype", help="hypes up gt")
async def gt_hype(ctx):
    hype_word = random.choice(["THWG", "GO JACKETS", "LET'S GO TECH", "TECH SUPERIORITY", "NERDS ON TOP"])
    emoji = random.choice(["buzz.png", "gatech.png"])
    with open(emoji, "rb") as img:
        picture = discord.File(img)
        await ctx.send(file=picture)
    await ctx.send("**RAAAAAHHHHHHHH**")
    await ctx.send(f"# __**{hype_word}!!!**__")

@bot.command(name="quant", help="QUANT")
async def quant(ctx):
    await ctx.send(f"# QUANT QUANT QUANT QUANT QUANT QUANT\n"
                    "QUANT QUANT QUANT QUANT QUANT QUANTQUANT QUANT QUANT QUANT QUANT QUANTQUANT"
                    "QUANT QUANT QUANT QUANT QUANTQUANT QUANT QUANT QUANT QUANT QUANTQUANT QUANT"
                    "QUANT QUANT QUANT QUANTQUANT QUANT QUANT QUANT QUANT QUANTQUANT QUANT QUANT" 
                    "QUANT QUANT QUANTQUANT QUANT QUANT QUANT QUANT QUANTQUANT QUANT QUANT QUANT QUANT QUANTQUANT QUANT QUANT QUANT QUANT QUANT")

@bot.command(name="money", help="money")
async def money(ctx):
    await ctx.send("I don't get the way you guys think. I want MONEY. 6 figures right out of college. 200k a year entry level. I'm in this for MONEY. I don't care about whether I'm 'fufilled' I want MONEY. Whatever gets me the most MONEY. What technology gets me PAID THE BEST. All I care about in this major is MONEY. That's why I'm in college, I don't wanna laugh and play with y'all. I don't wanna be buddy buddy with y'all. I'm here for MONEY.")

@bot.command(name="yeti", help="Alrighty, guys...")
async def yeti(ctx):
    await ctx.send(f"Alrighty, guys, it's been fun, but we all need to tone it down. Remember, this is the official Georgia Tech '28 server. "
                    "We've allowed you to have your fun for a while, but we really need to maintain a degree of professionalism. "
                    "Most of the rules in ⁠rules can be summed up in one rule: If you wouldn't want your professor or boss to see whatever you're thinking of posting, it's NOT appropriate to post it here either.  "
                    "We'd like to see more professionalism in the way you conduct yourself in this server. Keep in mind that this decision comes from our entire team.")

panda_hate = [":clown:", ":panda:", "what a bozo"]
@bot.command(name="panda", help="what a bozo")
async def panda(ctx, *, new_remark = None):
    global panda_hate
    if new_remark:
        panda_hate.append(new_remark)
        await ctx.message.reply(f"got it. :panda: {new_remark}")
    else:
        remark = random.choice(panda_hate)
        await ctx.message.reply(remark, mention_author = False)

@bot.command(name="important")
async def important(ctx):
    global most_important
    await ctx.send(random.choice(most_important))


bot.run(TOKEN)