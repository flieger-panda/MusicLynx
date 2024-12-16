#getting tokens
import os
from dotenv import load_dotenv

#getting yt audio and searching youtube
import yt_dlp
from youtube_search import YoutubeSearch

#regex
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#functional
import asyncio
import random

#genius client
from lyricsgenius import Genius

#spotify client
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#SSSHHHH
logs = open('logs.txt', 'a')
#SSSHHHH

#Getting tokens
load_dotenv()
TOKEN = os.environ.get('TOKEN')
client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')
genius_token = os.environ.get('genius_token')

#discord client imports
import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord import TextChannel

#Setting up discord client
intents = discord.Intents.all()
client = discord.Client(intents = intents)
activity = discord.Game(name="Music", type=discord.ActivityType.playing)
bot = commands.Bot(command_prefix='!', intents = intents, activity=activity)
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
#DISCORD

#setting up spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#setting up genius client
genius = Genius(genius_token)
skip = False

#run when bot is ready
@bot.event
async def on_ready():
    #log to console
    print("Lynx online")
    try:
        #sync application commands
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command")
    except Exception as e:
        print(e)

#get command help
@bot.tree.command(name = "lynx_help")
async def help(interaction: discord.Interaction):
     await interaction.response.send_message(f"""`/link` links to a song.\n
`/join` you have to get the bot to join a voice channel before it can play. if it's having errors, always try to run this first.\n
`/play song` plays the song you enter. ideal format: [artist] [song] [explicit/clean].\n
`/resume` resumes playing song.\n
`/pause` pauses song.\n
`/stop` stops playing and leaves the vc.\n
`!sing` sends the lyrics of the song you enter one-by-one. use carefully, or you might get banned :D\n
`!shout` SHOUTS the lyrics of the song you enter one-by-one. use carefully, or you might get banned :D\n 
`!stop_lyrics` stops sending lyrics.\n
`!time` adjusts the time between each line\n\n
`!preach` spits straight facts.\n
`!nerd user` when someone is being far too much of a nerd, nerd them.\n
pls use responsibly.
""")

#utility function to get urls from search term
def get_links(query):
     #spotify

     results = sp.search(q=query, type="track", limit=1)
     #basic conditional to handle search failure
     if results["tracks"]["items"]:
          spotify_url = results["tracks"]["items"][0]["external_urls"]["spotify"]
     else:
          raise Exception("Search Failed!")

     #genius
     hits = genius.search_songs(query)
     #if the search is successful, this'll get changed later
     genius_song = "Genius Search Failed"
     hits = hits["hits"]

     #making sure that the two results match closely. genius search can be weird.
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
          genius_url = "genius search failed, sry"
     
     #return the genius url, the spotify url, and the genius song object
     return genius_url, spotify_url, genius_song

#get links to a song query
@bot.tree.command(name = "link")
@app_commands.describe(song = "I'll link to this song!")
async def link(interaction: discord.Interaction, song: str):
    genius_link, spotify_link, _ignore = get_links(song)
    await interaction.response.send_message(f"Genius: {genius_link}\nSpotify: {spotify_link}")

#idk what this is for ngl
players = {}

#get top url for a query in YT
def get_top_result_url(query):
     results = YoutubeSearch((query + " audio"), max_results=10).to_dict()
     top_result_url = 'https://music.youtube.com' + results[0]['url_suffix']
     return top_result_url

# command for bot to join the channel of the user, if the bot has already joined and is in a different channel, it will move to the channel the user is in
@bot.tree.command(name = "join")
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
nerded = {}

# command to play sound from a youtube URL
@bot.tree.command(name = "play")
@app_commands.describe(song = "I'll play this song")
async def play(interaction: discord.Interaction, song: str):
     global queue
     #the search takes a while, so the response is deferred to make sure the interaction doesn't time out
     await interaction.response.defer()

     #setting options
     YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
     FFMPEG_OPTIONS = {
          'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

     #getting the vc object
     voice = get(bot.voice_clients, guild=interaction.guild)
     voice.is_playing()
     
     #try-catch to handle vc errors and whatnot
     try:
          url = get_top_result_url(song)
          song_url = url
          #making sure the bot isn't already playing
          if (not voice.is_playing()) or (len(queue[interaction.guild.id])<1):
               song = queue[interaction.guild.id].pop(0)
               url = get_top_result_url(song)
               song_url = url
               ydl_opts = {'format': 'bestaudio'}
               with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(url, download=False)
                    url2 = info['url']
               # Play the audio stream
               voice.is_playing()
               id = interaction.guild.id
               voice.play(discord.FFmpegPCMAudio(url2,before_options=FFMPEG_OPTIONS))
               await interaction.followup.send(f"playing now\n{song_url}")
               # check if the bot is already playing
          else:
               #a little message to the user
               await interaction.followup.send(f"already playing bruh")
               return
     except Exception as e:
          #doesn't work great without this block for some reason
          print(e)
          try:
               await interaction.followup.send("there might have been an error. wait for a couple of secs and try again.\nmake sure you ran /join.")
          except:
               await interaction.followup.send(f"playing now\n{song_url}")

#recurring command to play from queue
def play_recur(voice, song, id):
     print(song)
     url = get_top_result_url(song)
     YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
     FFMPEG_OPTIONS = {
          'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}
     song_url = url
     with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
          info = ydl.extract_info(url, download=False)
          url2 = info['url']
     # Play the audio stream
     voice.is_playing()
     try:
          voice.play(discord.FFmpegPCMAudio(url2,before_options=FFMPEG_OPTIONS), after = lambda e: play_recur(voice, queue[id].pop(0), id))
     except:
          pass



# command to resume voice if it is paused
@bot.tree.command(name = "resume")
async def resume(interaction: discord.Interaction):
     voice = get(bot.voice_clients, guild=interaction.guild)
     try:
          if not voice.is_playing():
               await voice.resume()
               await interaction.response.send_message("cool, i'll resume")
     except:
          await interaction.response.send_message("cool, i'll resume")


# command to pause voice if it is playing
@bot.tree.command(name = "pause")
async def pause(interaction: discord.Interaction):
     voice = get(bot.voice_clients, guild=interaction.guild)
     try:
          if voice.is_playing():
               await voice.pause()
               await interaction.response.send_message('aight, paused')
     except:
          await interaction.response.send_message("aight, paused")


# command to stop voice
@bot.tree.command(name = "stop")
async def stop(interaction: discord.Interaction):
     voice = get(bot.voice_clients, guild=interaction.guild)
     try:
          await voice.disconnect()
          await interaction.response.send_message("stopping and disconnecting...")
     except:
          await interaction.response.send_message("error. the bot might not be in a vc")


#SINGING FUNCTIONALITY#
 
#Setting default varables
singing = False
current_line = ""
time = float(8)
skipped = False

#Find a song's lyrics
def find_song(song_in):
     #using the get_links to simplify code
     url = get_links(song_in)[0]
     #retrieving the genius song object
     genius_song = get_links(song_in)[2]

     #handling a search failure from get_links
     if genius_song == "Genius Search Failed":
          lines, title = ["search failed"], "sorry"
          return(lines, title)
     else:
          #getting the lyrics
          song_lyrics = genius.lyrics(song_url=url)
          #cleaning the lyrics
          lines = clean(song_lyrics)
          #getting the title
          title = genius_song['result']['title']
          return(lines, title)

#Clean a song
def clean(lyrics):
     #getting line breaks when there are ad-libs
     lyrics = lyrics.replace("(","\n(")
     lyrics = lyrics.replace(")",")\n")

     #splitting lines
     lyrics = lyrics.split("\n")

     #creating a new list to save lyrics over to
     return_lyrics = []
     for line in lyrics:
          #if it has a square bracket, it's not actually a lyrics
          if "[" not in line:
               #getting rid of the bits that aren't lyrics
               if "Embed" in line:
                    line = line.replace("Embed","")
                    ine = ''.join((x for x in line if not x.isdigit()))
               if "contributor" in line.lower():
                    continue
               #i don't have an n-word pass
               if "nigga" in line.lower():
                    line = line.replace("Nigga", "Ni**a")
                    line = line.replace("nigga", "ni**ga")
               return_lyrics.append(line)
        
     return return_lyrics

#checking if the next line should skipping
@bot.event
async def on_message(message):
     global current_line
     global skip
     if not message.author.bot:
          if fuzz.ratio(message.content, current_line) > 50:
               skip = True
               #logging the skip to console
               print(f"Skipping!: '{message.content}' as '{current_line}'")
     #checking if the sender of a message has been "nerded"
     if message.author.id in nerded:
          #incrementing number of messages sent while nerded
          nerded[message.author.id] += 1
          #adding reaction
          await message.add_reaction("🤓")
          #rremoving from nerd directory if the 4 messages have already been reacted to
          if nerded[message.author.id] >= 2:
               del nerded[message.author.id]
     await bot.process_commands(message)

#SSSHHHHH#SSSHHHHH#SSSHHHHH
#SSSHHHHH#SSSHHHHH
#SSSHHHHH
@bot.event
async def on_message_delete(message):
     if not message.author.bot:
          logs = open(f'Logs {message.guild}.txt', 'a')
          logs.write(f"Deleted by [{message.author}] at [{message.created_at}] in [{message.channel}]: {message.content.strip()}\n")
          logs.close()
@bot.event
async def on_message_edit(before, after):
     if not before.author.bot:
          logs = open(f'Logs {before.guild}.txt', 'a')
          logs.write(f"Edited by [{before.author}] at [{after.created_at}] in [{before.channel}]: Before: {before.content.strip()} After: {after.content.strip()}\n")
          logs.close()
#SSSHHHHH
#SSSHHHHH#SSSHHHHH
#SSSHHHHH#SSSHHHHH#SSSHHHHH

@bot.command(name = "sing", help = "Sings songs!")
async def sing(ctx, *, song_name):
     global singing
     global current_line
     global skip
     global skipped
     global time

     if singing:
          await ctx.send("i'm alr singing smh. you haven't even told me to stop yet")

     singing = True
    
     #"""
     print("singing now")
     try:
          lines, title = find_song(song_name)
     except:
          await ctx.send("sorry, I had trouble pulling that up. pls try again")

     await ctx.send(title+":")
     for line in lines:

          #Updating current line
          current_line = line

          #Waiting for 8 seconds while typing if a line hasn't already been skipped
          if (not skipped) and singing:
               async with ctx.typing():
                    await asyncio.sleep(time)
          skipped = False

          if (not skip) and singing:
               skip = False
               if line != "":
                    await ctx.send(f"🗣️{line}")
               if not singing:
                    break
          elif skip:
               print("Skipped!")
               skipped = True
               skip = False
               continue
          else:
               break
     singing = False
     #"""

@bot.command(name = "shout", help = "SHOUTS songs!")
async def shout(ctx, *, song_name):
     global singing
     global current_line
     global skip
     global skipped
     global time

     if singing:
          await ctx.send("i'm alr singing smh. you haven't even told me to stop yet")

     singing = True
    
     #"""
     print("singing now")
     while True:
          try:
               lines, title = find_song(song_name)
               break
          except:
               await ctx.send("sorry, I had trouble pulling that up. lemme try again")
               continue

     await ctx.send(title+":")
     for line in lines:

          #Updating current line
          current_line = line

          #Waiting for 8 seconds while typing if a line hasn't already been skipped
          if (not skipped) and singing:
               async with ctx.typing():
                    await asyncio.sleep(time)
          skipped = False

          if (not skip) and singing:
               skip = False
               if line != "":
                    await ctx.send(f"🗣️{line}")
               if not singing:
                    break
          elif skip:
               print("Skipped!")
               skipped = True
               skip = False
               continue
          else:
               break
     singing = False
     #"""

@bot.command(name = "time")
async def time_set(ctx, time_in):
     global time
     try:
          time = float(time_in.strip())
          await ctx.send(f"ok. time interval set to {time}s")
     except:
          await ctx.send(f"bruh idk what you mean by '{time_in}'.")

@bot.command(name = "stop_lyrics")
async def stop_lyrics(ctx):
     global singing
     singing = False
     await ctx.send("ok. I'll stop 😕")

fax = ["CS majors should get free deodorant", "It's not immoral if you make six figures", "Bradley is a loser", "Bradley is a loser",
       "Bradley is a loser", "Bradley is a loser", "To Hell With Georgia",
       "I don't talk to UGA grads often, but when I do, I ask for large fries", "MIT is GT of the North", "Touch grass, buddy", 
       ":moyai:", "mods are nepo smh", "The art and the artist are separate", "Dobby is a free elf", "PJO >>", "The laws of physics don't apply to Legolas", 
       "The 'clay' in 'Mlepclaynos' is silent", "You heard about Pluto? That's messed up right?", "You the king, burger king", 
       "I have two rules. Rule one: I'm always right. Rule two: If I'm wrong, refer to rule one…",
       "I just love the smell of C4 in the morning.", "It smell like gaaas, I think somebody poo", "I take my shirt off and all the hoes stop breathin'",
       "Deutschland > France", "SLATT", "Fuck UGA ong", "Fuck UGA ong", "Fuck UGA ong", "Fuck UGA", "Fuck UGA", "ong, 21", "GT>>", "GT>>",
       "Pickup trucks are for idiots", "Bhupendra Jogi",
       "Lucas Luwa teaches CS1331", "Georgia  ech is  he best ", "OJ is innocent- orange juice can't commit crimes",
       "you = :nerd:", ":nerd:", ":nerd:", "you = :nerd:", ":nerd:", "you = :nerd:", ":moyai:", ":moyai:", ":moyai:", ":moyai:", ":moyai:"]
@bot.command(name = "preach")
async def preach(ctx):
     await ctx.send(random.choice(fax))

#send reaction when bean
@bot.command(name = "bean")
async def bean_lynx(ctx):
     await ctx.send(random.choice(["bruh why bean","get beaned lol"]))

#send reaction when ben
@bot.command(name = "ban")
async def ban_lynx(ctx):
     await ctx.send("🙀")

#command to nerd someone
@bot.command(name = "nerd")
async def nerd(ctx, member: discord.Member):
     #global dictionary of people who have been "nerded"
     global nerded
     #initializing how many messages they have sent while nerded
     nerded[member.id] = 0
     await ctx.send(f"# <@{member.id}> = :nerd:")
     
bot.run(TOKEN)