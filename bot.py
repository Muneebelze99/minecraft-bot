import streamlit as st
import discord
from discord.ext import commands
from python_aternos import Client
from google import genai
import threading
import asyncio
import re

# --- 1. DASHBOARD UI ---
st.set_page_config(page_title="Ghost Agent", page_icon="👻")
st.title("🕵️ Ghost Agent Dashboard")

# --- 2. THE SERVER FIX (INTENTS) ---
# This is why it wasn't replying in servers!
intents = discord.Intents.default()
intents.message_content = True  # Allows bot to read "!ask" etc.
intents.guilds = True           # Allows bot to see server channels
intents.messages = True         # Allows bot to see message events

# --- 3. LOAD SECRETS ---
try:
    AT_USER = st.secrets["ATERNOS_USER"]
    AT_PASS = st.secrets["ATERNOS_PASS"]
    DC_TOKEN = st.secrets["DISCORD_TOKEN"]
    GEM_KEY = st.secrets["GEMINI_KEY"]
except Exception as e:
    st.error("❌ Missing Secrets! Check Streamlit Settings.")
    st.stop()

# --- 4. THE GHOST ENGINE ---
bot = commands.Bot(command_prefix="!", intents=intents)

# Aternos & Gemini Clients
at_client = Client.from_credentials(AT_USER, AT_PASS)
at_server = at_client.list_servers()[0]
ai_client = genai.Client(api_key=GEM_KEY)

async def ghost_log_wipe():
    """Hides console activity"""
    for _ in range(25):
        at_server.send_command("tellraw @a {'text':''}")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    """Test if bot can hear you in the server"""
    await ctx.send(f"🏓 Pong! I see you, {ctx.author.name}!")

@bot.command()
async def ask(ctx, *, question: str):
    """2026 Gemini AI Command"""
    async with ctx.typing():
        try:
            response = ai_client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=question
            )
            await ctx.reply(f"🤖 **Gemini:** {response.text}")
        except Exception as e:
            await ctx.send(f"⚠️ AI Error: {str(e)}")

@bot.command()
async def find_tp(ctx, structure: str):
    """Ghost TP Logic"""
    # Hide the setup
    at_server.send_command("gamerule sendCommandFeedback false")
    at_server.send_command(f"locate structure minecraft:{structure}")
    
    await asyncio.sleep(2)
    log = at_server.get_log().content
    match = re.search(r"is at \[(-?\d+), (~|-?\d+), (-?\d+)\]", log)
    
    if match:
        coords = f"{match.group(1)} 100 {match.group(3)}"
        at_server.send_command(f"tp Unknown_boy8805 {coords}")
        await ghost_log_wipe()
        await ctx.send(f"🌌 Ghost-warped to **{structure}**. Logs cleared.")
    else:
        await ctx.send("❌ Could not find that structure.")

# --- 5. STREAMLIT RUNNER ---
def start_bot():
    bot.run(DC_TOKEN)

if st.button("🚀 Wake Up Ghost Agent"):
    if "active" not in st.session_state:
        st.session_state.active = True
        threading.Thread(target=start_bot, daemon=True).start()
        st.success("Ghost Agent is connecting to Discord...")
    else:
        st.warning("Agent is already running.")