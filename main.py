import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

@bot.tree.command(name="hello", description="Say hello to the bot")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Yo {interaction.user.mention}, welcome! 😎")

@bot.tree.command(name="members", description="Show member count")
async def members(interaction: discord.Interaction):
    count = interaction.guild.member_count
    await interaction.response.send_message(f"👥 There are `{count}` members here!")

@bot.tree.command(name="start", description="Start your journey here")
async def start(interaction: discord.Interaction):
    await interaction.response.send_message(f"📝 Hey {interaction.user.mention}, answer a few quick questions!")

# === MUSIC COMMANDS ===

@bot.tree.command(name="play", description="Play a YouTube song in VC")
async def play(interaction: discord.Interaction, url: str):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)

    if not voice_client:
        voice_client = await voice_channel.connect()

    await interaction.response.send_message(f"🎶 Playing: {url}", ephemeral=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
        source = FFmpegPCMAudio(audio_url)

        if not voice_client.is_playing():
            voice_client.play(source)

@bot.tree.command(name="pause", description="Pause the music")
async def pause(interaction: discord.Interaction):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await interaction.response.send_message("⏸ Music paused!")
    else:
        await interaction.response.send_message("❌ Nothing is playing.")

@bot.tree.command(name="resume", description="Resume the music")
async def resume(interaction: discord.Interaction):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("▶️ Music resumed!")
    else:
        await interaction.response.send_message("❌ Music is not paused.")

@bot.tree.command(name="stop", description="Stop the music")
async def stop(interaction: discord.Interaction):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await interaction.response.send_message("🛑 Music stopped!")
    else:
        await interaction.response.send_message("❌ Nothing is playing.")

@bot.tree.command(name="leave", description="Make bot leave VC")
async def leave(interaction: discord.Interaction):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if voice_client:
        await voice_client.disconnect()
        await interaction.response.send_message("👋 Left the voice channel.")
    else:
        await interaction.response.send_message("❌ I'm not in a voice channel.")

bot.run(TOKEN)
