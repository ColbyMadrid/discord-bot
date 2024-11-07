import discord
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
import os
import yt_dlp
import random
import asyncio
import re
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


intents = Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)


yt_dlp.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'opus',
        'preferredquality': '192',
    }],
    'restrictfilenames': True,
    'noplaylist': True,
}
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)
volume_level = 0.5
last_played = None
song_queue = []

@bot.event
async def on_ready():
    logging.info(f"{bot.user} has connected to Discord!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!commands"))

@bot.command()
async def commands(ctx):
    command_list = """
    **Available Commands:**
    !join - Join your voice channel.
    !leave - Leave the voice channel.
    !play <url> or <name> - Play audio from a YouTube link or search.
    !replay - Replay the last played song.
    !pause - Pause the currently playing song.
    !resume - Resume the currently paused song.
    !volume <0-100> - Set the volume level (default is 50%).
    !queue - View the current song queue.
    !skip - Skip the currently playing song.
    !clear - Clear the song queue.
    !remove <index> - Remove a song from the queue by its index.
    !shuffle - Shuffle the song queue.
    !commands - List all available commands.
    """
    await ctx.send(command_list)

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = ctx.guild.voice_client

        if voice_client is None or not voice_client.is_connected():
            await channel.connect()
            await ctx.send(f'Joined {channel}!')
        else:
            await ctx.send("I'm already connected to a voice channel.")
    else:
        await ctx.send('You need to be in a voice channel to use this command.')

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('Disconnected from the voice channel.')
    else:
        await ctx.send('I am not connected to a voice channel.')

@bot.command()
async def play(ctx, *, query: str = None, send_message: bool = True):
    """Play a song from a YouTube URL or search term."""
    if query is None or query.strip() == "":
        await ctx.send("Please provide a URL or search term. Usage: !play <URL or song name>")
        return

    playlist_pattern = re.compile(r'(playlist\?list=|youtu\.be/.*\?list=)', re.IGNORECASE)
    if playlist_pattern.search(query):
        await ctx.send("Sorry, this bot doesn't currently support playlists.")
        return

    global volume_level, last_played, song_queue

    voice_client = ctx.guild.voice_client
    if voice_client is None or not voice_client.is_connected():
        await ctx.send("I'm not connected to a voice channel. Use !join to bring me in first.")
        return

    async with ctx.typing():
        try:
            url_pattern = re.compile(r'https?://(?:www\.)?.+')
            if not url_pattern.match(query):
                await ctx.send(f"Searching for '{query}' on YouTube...")
                search_results = ytdl.extract_info(f"ytsearch:{query}", download=False)
                if search_results and 'entries' in search_results:
                    video = search_results['entries'][0]
                    audio_url = video['url']
                    title = video['title']
                    url = video['webpage_url']
                else:
                    await ctx.send("No results found on YouTube.")
                    return
            else:
                info = ytdl.extract_info(query, download=False)
                audio_url = info['url']
                title = info['title']

            last_played = (audio_url, title)
            queue_was_empty = len(song_queue) == 0
            song_queue.append((audio_url, title))

            if queue_was_empty and not voice_client.is_playing():
                await play_next(ctx, send_message=send_message)
            else:
                if send_message:
                    await ctx.send(f"Added to queue: {title} ({url})")
        except Exception as e:
            await ctx.send("There was an error processing your request. Please check the URL or search term and try again.")
            print(f"Error in play command: {e}")

async def play_next(ctx, send_message: bool = True):
    global song_queue
    voice_client = ctx.guild.voice_client

    if not voice_client or not voice_client.is_connected():
        return

    if len(song_queue) > 0:
        audio_url, title = song_queue.pop(0)

        try:
            audio_source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
            voice_client.play(
                discord.PCMVolumeTransformer(audio_source, volume=volume_level),
                after=lambda e: bot.loop.create_task(play_next(ctx, send_message))
            )
            if send_message:
                await ctx.send(f"Now playing: {title}")
        except Exception as e:
            print(f"Error playing {title}: {e}")
            await ctx.send(f"Unable to play '{title}'. Skipping to the next song.")
            await play_next(ctx, send_message)
    else:
        await ctx.send("The queue is empty!")


@bot.command()
async def replay(ctx):
    """Replay the last played song."""
    global last_played  

    if last_played is None:
        await ctx.send("No song has been played yet.")
        return

    url, title = last_played
    play_command = bot.get_command('play')
    await play_command(ctx, query=url, send_message=False)
    await ctx.send(f"Now replaying: {title}")

@bot.command()
async def skip(ctx):
    voice_client = ctx.voice_client
    
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Skipped the current song.")
        
        if song_queue:
            await play_next(ctx)
    else:
        await ctx.send("There are no songs currently playing.")

@bot.command()
async def volume(ctx, volume: int):
    global volume_level
    voice_client = ctx.voice_client

    if not (0 <= volume <= 100):
        await ctx.send("Please provide a volume between 0 and 100.")
        return

    volume_level = volume / 100.0
    if voice_client and voice_client.source:
        voice_client.source.volume = volume_level

    await ctx.send(f"Volume set to {volume} %.")

@bot.command()
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send('Paused the song.')
    else:
        await ctx.send('There is no song currently playing.')

@bot.command()
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send('Resumed the song.')
    elif voice_client and not voice_client.is_playing():
        await ctx.send('There is no song currently playing.')
    else:
        await ctx.send('The song is not paused.')

@bot.command()
async def queue(ctx):
    if song_queue:
        queue_list = '\n'.join(f"{index+1}. {title}" for index, (_, title) in enumerate(song_queue))
        await ctx.send(f"Current queue:\n{queue_list}")
    else:
        await ctx.send("The queue is empty.")

@bot.command()
async def clear(ctx):
    global song_queue

    if not song_queue:
        await ctx.send("The queue is currently empty.")
    else:
        song_queue.clear()
        await ctx.send("Cleared the song queue.")

@bot.command()
async def remove(ctx, index: int):
    global song_queue
    try:
        song_queue.pop(index - 1)  
        await ctx.send(f"Removed song at position {index}.")
    except IndexError:
        await ctx.send("Invalid index. Please try again.")

@bot.command()
async def shuffle(ctx):
    """Shuffle the song queue."""
    global song_queue
    if len(song_queue) == 0:
        await ctx.send("There are currently no songs to shuffle in the queue.")
    else:
        random.shuffle(song_queue)
        await ctx.send("Shuffled the song queue.")

bot.run(TOKEN)
