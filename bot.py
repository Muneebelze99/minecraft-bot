import streamlit as st
import discord
from discord.ext import commands
from python_aternos import Client
from google import genai
import threading
import asyncio
import re

# --- 1. CONFIG & INTENTS ---
st.set_page_config(page_title="Ghost Agent 2026", page_icon="👻")
st.title("🕵️ Ghost Agent: Unknown_boy8805 Edition")

# Required to read commands and send messages in servers
intents = discord.Intents.default()
intents.message_content = True 
intents.guilds = True

# --- 2. SETTINGS & SECRETS ---
# PASTE YOUR CHANNEL ID HERE (e.g., 123456789012345678)
GHOST_CHANNEL_ID = 123456789012345678 

try:
    AT_USER = st.secrets["ATERNOS_USER"]
    AT_PASS = st.secrets["ATERNOS_PASS"]
    DC_TOKEN = st.secrets["DISCORD_TOKEN"]
    GEM_KEY = st.secrets["GEMINI_KEY"]
except Exception as e:
    st.error("❌ Secrets missing! Check Streamlit Settings > Secrets.")
    st.stop()

# --- 3. THE GHOST ENGINE ---
# We use st.session_state to keep the bot alive during refreshes
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False

# Fixed Aternos Login logic
@st.cache_resource
def connect_aternos():
    try:
        at = Client(user=AT_USER, password=AT_PASS)
        return at.list_servers()[0]
    except Exception as e:
        st.error(f"Aternos Login Failed: {e}")
        return None

at_server = connect_aternos()
ai_client = genai.Client(api_key=GEM_KEY)
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 4. GHOST MESSAGE & EVENTS ---
@bot.event
async def on_ready():
    print(f"✅ Ghost Agent Online: {bot.user}")
    # Automatic Ghost Message on startup
    channel = bot.get_channel(GHOST_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🕵️ Ghost Agent Activated",
            description="Status: **Online**\nStealth Mode: **Enabled**\n\n*Awaiting commands from Unknown_boy8805...*",
            color=0x2f3136
        )
        await channel.send(embed=embed)

# --- 5. STEALTH COMMANDS ---
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! I see you, {ctx.author.name}!")

@bot.command()
async def track(ctx, target: str):
    """Ghost Tracker: Finds coordinates without alerts"""
    at_server.send_command(f"data get entity {target} Pos")
    await asyncio.sleep(1.5)
    log = at_server.get_log().content
    match = re.findall(rf"{target} has the following entity data: \[(-?\d+\.\d+)d, (-?\d+\.\d+)d, (-?\d+\.\d+)d\]", log)
    if match:
        x, y, z = match[-1]
        await ctx.send(f"📍 **Radar:** `{target}` is at **X: {float(x):.1f}, Y: {float(y):.1f}, Z: {float(z):.1f}**")
    else:
        await ctx.send(f"❌ Could not track `{target}`. Are they online?")

@bot.command()
async def ask(ctx, *, q):
    """Gemini 2.0 AI Assistant"""
    async with ctx.typing():
        res = ai_client.models.generate_content(model="gemini-2.0-flash", contents=q)
        await ctx.reply(f"🤖 **Ghost AI:** {res.text}")

# --- 6. DASHBOARD CONTROL ---
def run_discord_bot():
    bot.run(DC_TOKEN)

# 'key' argument fixes the DuplicateElementId error
if st.button("🚀 Wake Up Ghost Agent", key="final_launch_btn"):
    if not st.session_state.bot_running:
        st.session_state.bot_running = True
        thread = threading.Thread(target=run_discord_bot, daemon=True)
        thread.start()
        st.success("Ghost Agent is waking up... check Discord!")
    else:
        st.warning("Agent is already running.")

st.divider()
if at_server:
    st.info(f"🎮 Connected to: **{getattr(at_server, 'domain', 'Aternos Server')}**")