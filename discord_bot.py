import discord
from discord.ext import commands
import aiohttp
from aiohttp import web
import json
import asyncio
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

CHANNEL_ID = None
app = web.Application()
routes = web.RouteTableDef()

@routes.get('/')
async def health_check(request):
    return web.json_response({"status": "online", "bot": "ready"})

@routes.post('/report')
async def handle_report(request):
    try:
        data = await request.json()
        
        reporter = data.get('reporter', {})
        reported = data.get('reported', {})
        reason = data.get('reason', 'No reason provided')
        
        reporter_name = reporter.get('name', 'Unknown')
        reporter_id = reporter.get('userId', 0)
        reporter_thumbnail = reporter.get('thumbnail', '')
        reporter_profile = reporter.get('profileUrl', '')
        
        reported_name = reported.get('name', 'Unknown')
        reported_id = reported.get('userId', 0)
        reported_thumbnail = reported.get('thumbnail', '')
        reported_profile = reported.get('profileUrl', '')
        
        server_id = data.get('serverId', 'Unknown')
        place_id = data.get('placeId', 0)
        
        embed = discord.Embed(
            title="Player Report",
            description=f"**Reason:** {reason}",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="Reporter",
            value=f"[{reporter_name}]({reporter_profile}) (ID: {reporter_id})",
            inline=True
        )
        
        embed.add_field(
            name="Reported Player",
            value=f"[{reported_name}]({reported_profile}) (ID: {reported_id})",
            inline=True
        )
        
        embed.add_field(
            name="Server Info",
            value=f"Job ID: {server_id}\nPlace ID: {place_id}",
            inline=False
        )
        
        embed.set_thumbnail(url=reported_thumbnail)
        embed.set_image(url=reporter_thumbnail)
        
        embed.set_footer(text=f"Reported by {reporter_name}")
        
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)
            print(f"[discord_bot] Report sent to Discord channel")
        else:
            print(f"[discord_bot] Channel not found! Make sure CHANNEL_ID is set correctly.")
        
        return web.json_response({"status": "success"})
    
    except Exception as e:
        print(f"[discord_bot] Error handling report: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)

app.router.add_routes(routes)

async def start_web_server():
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    site = web.TCPSite(runner, host, port)
    await site.start()
    print(f"[discord_bot] Web server started on http://{host}:{port}")

@bot.event
async def on_ready():
    print(f"[discord_bot] Bot logged in as {bot.user}")
    await start_web_server()

async def main():
    token = os.getenv('DISCORD_BOT_TOKEN')
    global CHANNEL_ID
    CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', 0))
    
    if not token:
        print("[discord_bot] ERROR: DISCORD_BOT_TOKEN environment variable not set!")
        return
    
    if not CHANNEL_ID:
        print("[discord_bot] ERROR: DISCORD_CHANNEL_ID environment variable not set!")
        return
    
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())

