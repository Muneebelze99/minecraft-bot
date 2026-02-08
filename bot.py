import streamlit as st
import discord
from discord.ext import commands
from python_aternos import Client
from google import genai
import threading
import asyncio
import re

# --- 1. DASHBOARD CONFIG ---
st.set_page_config(page_title="Ghost Agent OP Console", page_icon="👻")
st.title("🕵️ Ghost Agent: Unknown_boy8805 Edition")

# Required Intents to read messages and handle servers
intents = discord.Intents.default()
intents.message_content = True 
intents.guilds = True

# --- 2. SETTINGS ---
# Replace with your actual Discord Channel ID
GHOST_CHANNEL_ID = 123456789012345678 

# Load Secrets
try:
    AT_USER = st.secrets["ATERNOS_USER"]
    AT_PASS = st.secrets["ATERNOS_PASS"]
    DC_TOKEN = st.secrets["DISCORD_TOKEN"]
    GEM_KEY = st.secrets["GEMINI_KEY"]
except:
    st.error("❌ Secrets missing in Streamlit Settings!")
    st.stop()

# --- 3. THE GHOST ENGINE ---
if 'bot_active' not in st.session_state:
    st.session_state.bot_active = False

@st.cache_resource
def get_aternos_access():
    try:
        at = Client(user=AT_USER, password=AT_PASS)
        # Finds the server you have access to
        all_serv = at.list_servers()
        return all_serv[0] if all_serv else None
    except Exception as e:
        st.error(f"Aternos Login Failed: {e}")
        return None

at_server = get_aternos_access()
ai_client = genai.Client(api_key=GEM_KEY)
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 4. GHOST UTILITIES ---
async def ghost_wipe():
    """Hides OP commands from the console history"""
    at_server.send_command("gamerule sendCommandFeedback false")
    at_server.send_command("gamerule logAdminCommands false")
    for _ in range(25):
        at_server.send_command("tellraw @a {'text':''}")

# --- 5. DISCORD EVENTS & OP COMMANDS ---
@bot.event
async def on_ready():
    print(f"✅ Ghost Agent Online: {bot.user}")
    channel = bot.get_channel(GHOST_CHANNEL_ID)
    if channel:
        await channel.send("👻 **Ghost Agent Awakened.** OP permissions detected. Stealth: `ENABLED`.")

@bot.command()
async def gear_up(ctx):
    """Gives you God Gear via Console"""
    at_server.send_command(f"give {ctx.author.name} netherite_sword{{Enchantments:[{{id:sharpness,lvl:5}}]}}")
    at_server.send_command(f"give {ctx.author.name} golden_apple 64")
    await ghost_wipe()
    await ctx.send(f"🎒 **Kit Sent to {ctx.author.name}.** Console traces wiped.")

@bot.command()
async def track(ctx, target: str):
    """Finds a player's exact location using OP data commands"""
    at_server.send_command(f"data get entity {target} Pos")
    await asyncio.sleep(1.5)
    log = at_server.get_log().content
    match = re.findall(rf"{target} has the following entity data: \[(-?\d+\.\d+)d, (-?\d+\.\d+)d, (-?\d+\.\d+)d\]", log)
    if match:
        x, y, z = match[-1]
        await ctx.send(f"📍 **Radar:** `{target}` is at **X: {float(x):.1f}, Y: {float(y):.1f}, Z: {float(z):.1f}**")
        await ghost_wipe()
    else:
        await ctx.send(f"❌ Target `{target}` is hidden or offline.")

@bot.command()
async def bypass(ctx, *, cmd: str):
    """Run ANY command as the OP bot (Total Control)"""
    at_server.send_command(cmd)
    await ghost_wipe()
    await ctx.send(f"✅ Console Executed: `{cmd}`")

@bot.command()
async def ask(ctx, *, q):
    """AI Assistant (Gemini 2.0 Flash)"""
    async with ctx.typing():
        res = ai_client.models.generate_content(model="gemini-2.0-flash", contents=q)
        await ctx.reply(f"🤖 **Ghost AI:** {res.text}")

# --- 6. DASHBOARD CONTROL ---
def start_bot():
    bot.run(DC_TOKEN)

if st.button("🚀 Wake Up Ghost Agent", key="ghost_vFinal"):
    if not st.session_state.bot_active:
        st.session_state.bot_active = True
        threading.Thread(target=start_bot, daemon=True).start()
        st.success("Bot is connecting... check Discord!")
    else:
        st.warning("Ghost Agent is already running.")

st.divider()
if at_server:
    st.info(f"🎮 Controlling: **{getattr(at_server, 'domain', 'Aternos Server')}**")