import streamlit as st
import discord
from discord.ext import commands
from python_aternos import Client
import threading
import asyncio
import re

# 1. Dashboard UI
st.set_page_config(page_title="Ghost Agent", page_icon="👻")
st.title("🕵️ Ghost Agent Dashboard")

# 2. Load Secrets (Setup these in Streamlit Settings)
try:
    AT_USER = st.secrets["ATERNOS_USER"]
    AT_PASS = st.secrets["ATERNOS_PASS"]
    DC_TOKEN = st.secrets["DISCORD_TOKEN"]
    # Add GEMINI_KEY here if using AI features
except KeyError:
    st.error("Please set your Secrets in Streamlit Settings first!")
    st.stop()

# 3. Discord Bot Logic
def run_discord_bot():
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    # Aternos Login
    aternos = Client.from_credentials(AT_USER, AT_PASS)
    server = aternos.list_servers()[0]

    async def ghost_execute(cmd_text):
        """Silently executes a command and wipes traces"""
        server.send_command("gamerule sendCommandFeedback false")
        server.send_command("gamerule logAdminCommands false")
        server.send_command("gamerule broadcastConsoleToOps false")
        server.send_command(cmd_text)
        # Smoke Screen: Push console logs up
        for _ in range(30):
            server.send_command("tellraw @a {'text':''}")

    @bot.command()
    async def find_tp(ctx, structure: str):
        if ctx.author.name != "unknown8805": return
        server.send_command(f"locate structure minecraft:{structure}")
        await asyncio.sleep(2)
        log = server.get_log().content
        match = re.search(r"is at \[(-?\d+), (~|-?\d+), (-?\d+)\]", log)
        if match:
            coords = f"{match.group(1)} 100 {match.group(3)}"
            await ghost_execute(f"tp Unknown_boy8805 {coords}")
            await ctx.send(f"🌌 **Ghost Warp:** {structure} reached. Logs wiped.")

    @bot.command()
    async def spy(ctx):
        """Reads the last 10 commands from logs"""
        log = server.get_log().content
        cmds = re.findall(r"(\w+) issued server command: (/.+)", log)
        report = "\n".join([f"👤 `{p}`: `{c}`" for p, c in cmds[-10:]])
        await ctx.send(f"🕵️ **Recent Activity:**\n{report or 'No logs found.'}")

    bot.run(DC_TOKEN)

# 4. Streamlit Control
if st.button("🚀 Activate Ghost Agent"):
    if "running" not in st.session_state:
        threading.Thread(target=run_discord_bot, daemon=True).start()
        st.session_state.running = True
    st.success("Bot is live! Control it via Discord DMs.")

# Create intents object
intents = discord.Intents.default()
intents.message_content = True  # <--- THIS IS THE MISSING KEY
intents.guilds = True
intents.messages = True

# Pass intents into the bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! I can hear you, {ctx.author.name}!")