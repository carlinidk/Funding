import discord
from discord import app_commands
from discord.ext import commands
from amazon_api import search_amazon
from config import DISCORD_BOT_TOKEN

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash commands synced: {len(synced)}")
    except Exception as e:
        print(e)

@bot.tree.command(name="amazon", description="Search Amazon for products")
async def amazon_command(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    result = search_amazon(query)

    if not result:
        await interaction.followup.send("❌ No results found.")
        return
    
    embed = discord.Embed(
        title=result["title"],
        url=result["url"],
        description=f"💰 **Price:** {result['price']}\n⭐ **Rating:** {result['rating']}",
        color=0xFFA500
    )
    if result["image"]:
        embed.set_thumbnail(url=result["image"])

    await interaction.followup.send(embed=embed)

bot.run(DISCORD_BOT_TOKEN)
