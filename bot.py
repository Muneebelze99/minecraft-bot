import streamlit as st
import discord
from discord.ext import commands
from python_aternos import Client
from google import genai
import threading
import asyncio
import re

# --- 1. CONFIG ---
st.set_page_config(page_title="Ghost Agent Console", page_icon="👻")
st.title("🕵️ Ghost Agent: Console Command Center")

# --- 2. THE SERVER FIX (INTENTS) ---
intents = discord.Intents.default()
intents.message_content = True 
intents.guilds = True

# --- 3. SETTINGS ---
# Replace this with your Discord Channel ID to receive the "I'm awake" message
GHOST_CHANNEL_ID = 123456789012345678 

# --- 4. SECRETS ---
try:
    AT_USER = st.secrets["ATERNOS_USER"]
    AT_PASS = st.secrets["ATERNOS_PASS"]
    DC_TOKEN = st.secrets["DISCORD_TOKEN"]
    GEM_KEY = st.secrets["GEMINI_KEY"]
except:
    st.error("❌ Secrets missing! Add ATERNOS_USER, ATERNOS_PASS, DISCORD_TOKEN, and GEMINI_KEY to Streamlit.")
    st.stop()

# --- 5. THE GHOST ENGINE ---
if 'bot_active' not in st.session_state:
    st.session_state.bot_active = False

@st.cache_resource
def get_aternos():
    try:
        at = Client(user=AT_USER, password=AT_PASS)
        return at.list_servers()[0]
    except Exception as e:
        st.error(f"Aternos Login Failed: {e}")
        return None

at_server = get_aternos()
ai_client = genai.Client(api_key=GEM_KEY)
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 6. GHOST UTILITIES ---
async def ghost_wipe():
    """Hides console traces immediately"""
    at_server.send_command("gamerule sendCommandFeedback false")
    at_server.send_command("gamerule logAdminCommands false")
    for _ in range(20):
        at_server.send_command("tellraw @a {'text':''}")

# --- 7. DISCORD EVENTS & COMMANDS ---
@bot.event
async def on_ready():
    print(f"✅ Ghost Agent Online: {bot.user}")
    channel = bot.get_channel(GHOST_CHANNEL_ID)
    if channel:
        await channel.send("👻 **Ghost Agent Awakened.** Console link established. Stealth: `ACTIVE`.")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong! Console is responsive.")

@bot.command()
async def grant_me(ctx):
    """Gives you OP from the console silently"""
    at_server.send_command(f"op {ctx.author.name}")
    await ghost_wipe()
    await ctx.send(f"🤫 **{ctx.author.name}** now has Console Authority.")

@bot.command()
async def bypass(ctx, *, cmd: str):
    """Executes any command directly as the Server Console"""
    at_server.send_command(cmd)
    await ghost_wipe()
    await ctx.send(f"✅ Executed: `{cmd}`. Logs wiped.")

@bot.command()
async def track(ctx, target: str):
    """Locate player via entity data"""
    at_server.send_command(f"data get entity {target} Pos")
    await asyncio.sleep(1.5)
    log = at_server.get_log().content
    match = re.findall(rf"{target} has the following entity data: \[(-?\d+\.\d+)d, (-?\d+\.\d+)d, (-?\d+\.\d+)d\]", log)
    if match:
        x, y, z = match[-1]
        await ctx.send(f"📍 **Radar:** `{target}` is at **X: {float(x):.1f}, Y: {float(y):.1f}, Z: {float(z):.1f}**")
        await ghost_wipe()
    else:
        await ctx.send(f"❌ Failed to find `{target}`.")

@bot.command()
async def ask(ctx, *, q):
    """AI Assistant"""
    async with ctx.typing():
        res = ai_client.models.generate_content(model="gemini-2.0-flash", contents=q)
        await ctx.reply(f"🤖 **Ghost AI:** {res.text}")

# --- 8. DASHBOARD ---
if st.button("🚀 Wake Up Ghost Agent", key="ghost_v3_btn"):
    if not st.session_state.bot_active:
        st.session_state.bot_active = True
        threading.Thread(target=lambda: bot.run(DC_TOKEN), daemon=True).start()
        st.success("Bot is connecting... check Discord!")
    else:
        st.warning("Ghost Agent is already running.")

st.divider()
if at_server:
    st.info(f"🎮 Target Server: **{getattr(at_server, 'domain', 'Aternos')}**")