import discord
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
import os
import yt_dlp
import random


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


intents = Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True


bot = commands.Bot(command_prefix="!", intents=intents)


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
    print(f"{bot.user} has connected to Discord!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!commands"))

@bot.command()
async def commands(ctx):
    """List all available commands."""
    command_list = """
    **Available Commands:**
    `!join` - Join your voice channel.
    `!leave` - Leave the voice channel.
    `!play <url>` - Play audio from a YouTube link.
    `!replay` - Replay the last played song.
    `!pause` - Pause the currently playing song.
    `!resume` - Resume the currently paused song.
    `!volume <0-100>` - Set the volume level (default is 50%).
    `!queue` - View the current song queue.
    `!skip` - Skip the currently playing song.
    `!clear` - Clear the song queue.
    `!remove <index>` - Remove a song from the queue by its index.
    `!shuffle` - Shuffle the song queue.
    `!commands` - List all available commands.
    """
    await ctx.send(command_list)

@bot.command()
async def join(ctx):
    """Join a voice channel."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = ctx.guild.voice_client

        if voice_client is None or not voice_client.is_connected():
            await channel.connect()
            await ctx.send(f'Joined {channel}')
        else:
            await ctx.send("I'm already connected to a voice channel.")
    else:
        await ctx.send('You need to be in a voice channel to use this command.')

@bot.command()
async def leave(ctx):
    """Leave the voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('Disconnected from the voice channel.')
    else:
        await ctx.send('I am not connected to a voice channel.')

@bot.command()
async def play(ctx, url: str):
    """Play a song from a YouTube URL."""
    global volume_level, last_played, song_queue  

    voice_client = ctx.guild.voice_client
    if voice_client is None or not voice_client.is_connected():
        await ctx.send("I'm not connected to a voice channel. Use `!join` to bring me in first.")
        return

    
    async with ctx.typing():
        info = ytdl.extract_info(url, download=False)
        audio_url = info['url']
        last_played = (audio_url, info['title'])  
        song_queue.append((audio_url, info['title']))  

    
    if not voice_client.is_playing():
        await play_next(ctx)

    await ctx.send(f"Added to queue: {info['title']}")

async def play_next(ctx):
    """Play the next song in the queue."""
    global song_queue
    voice_client = ctx.guild.voice_client

    if len(song_queue) > 0:
        audio_url, title = song_queue.pop(0)  
        audio_source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
        voice_client.play(discord.PCMVolumeTransformer(audio_source, volume=volume_level), after=lambda e: bot.loop.create_task(play_next(ctx)))
        await ctx.send(f"Now playing: {title}")
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
    await play(ctx, url)

@bot.command()
async def skip(ctx):
    """Skip the currently playing song."""
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()  
        await ctx.send("Skipped the current song.")
        await play_next(ctx)  
    else:
        await ctx.send("There is no song currently playing.")

@bot.command()
async def volume(ctx, volume: int):
    """Adjust the volume of the bot (0-100)."""
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
    """Pause the currently playing song."""
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send('Paused the song.')
    else:
        await ctx.send('There is no song currently playing.')

@bot.command()
async def resume(ctx):
    """Resume the currently paused song."""
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send('Resumed the song.')
    else:
        await ctx.send('The song is not paused.')

@bot.command()
async def queue(ctx):
    """View the current song queue."""
    if len(song_queue) == 0:
        await ctx.send("The queue is empty.")
    else:
        queue_list = "\n".join([f"{i + 1}: {title}" for i, (_, title) in enumerate(song_queue)])
        await ctx.send(f"Current queue:\n{queue_list}")

@bot.command()
async def clear(ctx):
    """Clear the song queue."""
    global song_queue
    if len(song_queue) == 0:
        await ctx.send("There are no songs in the queue to clear.")
    else:
        song_queue.clear()
        await ctx.send("Cleared the song queue.")

@bot.command()
async def remove(ctx, index: int):
    """Remove a song from the queue by its index (1-based)."""
    global song_queue
    if 0 < index <= len(song_queue):
        removed_song = song_queue.pop(index - 1)  
        await ctx.send(f"Removed from queue: {removed_song[1]}")
    else:
        await ctx.send("Invalid index. Please provide a valid index.")

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
