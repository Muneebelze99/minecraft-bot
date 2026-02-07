import streamlit as st
import discord
from discord.ext import commands
from python_aternos import Client
from google import genai
import threading
import asyncio
import re

# --- 1. DASHBOARD CONFIG ---
st.set_page_config(page_title="Ghost Agent Dashboard", page_icon="👻")
st.title("🕵️ Unknown_boy8805's Ghost Agent")

# --- 2. INTENTS (THE SERVER REPLY FIX) ---
intents = discord.Intents.default()
intents.message_content = True  # Crucial for reading !ask and !find_tp
intents.guilds = True
intents.messages = True

# --- 3. LOAD SECRETS ---
try:
    AT_USER = st.secrets["ATERNOS_USER"]
    AT_PASS = st.secrets["ATERNOS_PASS"]
    DC_TOKEN = st.secrets["DISCORD_TOKEN"]
    GEM_KEY = st.secrets["GEMINI_KEY"]
except Exception as e:
    st.error("❌ Secrets missing! Go to Streamlit Settings > Secrets.")
    st.stop()

# --- 4. THE GHOST ENGINE ---
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize Clients
try:
    # Fixed login method for python-aternos
    at_client = Client(user=AT_USER, password=AT_PASS)
    at_server = at_client.list_servers()[0]
    ai_client = genai.Client(api_key=GEM_KEY)
except Exception as e:
    st.error(f"❌ Connection Error: {e}")

async def ghost_cleaner():
    """Spams the console with blank lines to hide recent commands"""
    for _ in range(25):
        at_server.send_command("tellraw @a {'text':''}")

@bot.event
async def on_ready():
    print(f"✅ Ghost Agent connected as {bot.user}")

@bot.command()
async def ping(ctx):
    """Test if bot can see you in the server"""
    await ctx.send(f"🏓 Pong! I see you, {ctx.author.name}!")

@bot.command()
async def ask(ctx, *, question: str):
    """AI Minecraft Assistant"""
    async with ctx.typing():
        try:
            response = ai_client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=question
            )
            await ctx.reply(f"🤖 **Ghost AI:** {response.text}")
        except Exception as e:
            await ctx.send(f"⚠️ AI Error: {e}")

@bot.command()
async def find_tp(ctx, structure: str):
    """Locate and TP without leaving a trace"""
    at_server.send_command("gamerule sendCommandFeedback false")
    at_server.send_command(f"locate structure minecraft:{structure}")
    
    await asyncio.sleep(2)
    log_content = at_server.get_log().content
    # Search for coordinates in the console log
    match = re.search(r"is at \[(-?\d+), (~|-?\d+), (-?\d+)\]", log_content)
    
    if match:
        coords = f"{match.group(1)} 100 {match.group(3)}"
        at_server.send_command(f"tp Unknown_boy8805 {coords}")
        await ghost_cleaner()
        await ctx.send(f"🌌 **Warped to {structure}.** Console traces wiped.")
    else:
        await ctx.send(f"❌ Could not find a {structure} nearby.")

@bot.command()
async def spy(ctx):
    """See what other players are doing in the console"""
    log_content = at_server.get_log().content
    cmds = re.findall(r"(\w+) issued server command: (/.+)", log_content)
    if cmds:
        report = "\n".join([f"👤 `{p}`: `{c}`" for p, c in cmds[-10:]])
        await ctx.send(f"🕵️ **Command History:**\n{report}")
    else:
        await ctx.send("🕵️ No player commands found in recent logs.")

# --- 5. STREAMLIT CONTROL ---
def start_bot():
    bot.run(DC_TOKEN)

if st.button("🚀 Wake Up Ghost Agent"):
    if "running" not in st.session_state:
        st.session_state.running = True
        # Run Discord in background thread
        thread = threading.Thread(target=start_bot, daemon=True)
        thread.start()
        st.success("Ghost Agent is waking up! Check Discord.")
    else:
        st.warning("Agent is already online.")

st.divider()
st.info("Directly controlling Minecraft server: " + at_server.address)