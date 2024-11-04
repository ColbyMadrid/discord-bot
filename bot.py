import discord
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
import os

# Load the token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Create an instance of Intents
intents = Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True

# Initialize the bot with a command prefix and the intents
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hello! I'm your bot, ready to assist.")

@bot.command(name="joke")
async def joke(ctx):
    await ctx.send("Why did the scarecrow win an award? Because he was outstanding in his field!")

@bot.command(name="commands")  # Renamed from help to commands
async def commands_command(ctx):
    help_text = """
    Here are the available commands:
    - `!hello`: Greets you.
    - `!joke`: Tells a joke.
    - `!commands`: Shows this help message.
    """
    await ctx.send(help_text)

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')  # Change 'general' to your channel name
    await channel.send(f"Welcome to the server, {member.mention}!")

# Run the bot
bot.run(TOKEN)
