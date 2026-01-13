import discord
from discord.ext import commands
import aiohttp
from aiohttp import web
import json
import asyncio
import os
from datetime import datetime
from collections import Counter

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

CHANNEL_ID = None
app = web.Application()
routes = web.RouteTableDef()

REPORTS_FILE = "reports.json"

def load_reports():
    try:
        if os.path.exists(REPORTS_FILE):
            with open(REPORTS_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"[discord_bot] Error loading reports: {e}")
        return []

def save_reports(reports):
    try:
        with open(REPORTS_FILE, 'w') as f:
            json.dump(reports, f, indent=2)
    except Exception as e:
        print(f"[discord_bot] Error saving reports: {e}")

def getReportsLast24H(reportedId):
    reports = load_reports()
    now = datetime.now().timestamp()
    day_ago = now - 86400
    count = sum(1 for r in reports if r.get('reportedId') == reportedId and r.get('timestamp', 0) >= day_ago)
    return count

def getReportsLastMonth(reportedId):
    reports = load_reports()
    now = datetime.now().timestamp()
    month_ago = now - (86400 * 30)
    count = sum(1 for r in reports if r.get('reportedId') == reportedId and r.get('timestamp', 0) >= month_ago)
    return count

def getReporterHistory(reporterId):
    reports = load_reports()
    count = sum(1 for r in reports if r.get('reporterId') == reporterId)
    return count

def getTimeSinceLastReport(reportedId, exclude_timestamp=None):
    reports = load_reports()
    reported_reports = [r for r in reports if r.get('reportedId') == reportedId]
    if exclude_timestamp:
        reported_reports = [r for r in reported_reports if r.get('timestamp', 0) != exclude_timestamp]
    if not reported_reports:
        return None
    latest = max(reported_reports, key=lambda x: x.get('timestamp', 0))
    latest_time = latest.get('timestamp', 0)
    if latest_time == 0:
        return None
    time_diff = datetime.now().timestamp() - latest_time
    if time_diff < 60:
        return f"{int(time_diff)} seconds ago"
    elif time_diff < 3600:
        return f"{int(time_diff / 60)} minutes ago"
    elif time_diff < 86400:
        return f"{int(time_diff / 3600)} hours ago"
    else:
        return f"{int(time_diff / 86400)} days ago"

def getMostCommonReason(reportedId, exclude_timestamp=None):
    reports = load_reports()
    reported_reports = [r for r in reports if r.get('reportedId') == reportedId]
    if exclude_timestamp:
        reported_reports = [r for r in reported_reports if r.get('timestamp', 0) != exclude_timestamp]
    if not reported_reports:
        return None
    reasons = [r.get('abuseType', 'Unknown') for r in reported_reports]
    if not reasons:
        return None
    counter = Counter(reasons)
    most_common = counter.most_common(1)[0]
    return f"{most_common[0]} ({most_common[1]} times)"

@routes.get('/')
async def health_check(request):
    return web.json_response({"status": "online", "bot": "ready"})

@routes.post('/report')
async def handle_report(request):
    try:
        data = await request.json()
        
        reporter = data.get('reporter', {})
        reported = data.get('reported', {})
        abuse_type = data.get('abuseType', 'Unknown')
        additional_info = data.get('additionalInfo', '')
        
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
        timestamp = data.get('timestamp', int(datetime.now().timestamp()))
        
        reports = load_reports()
        report_entry = {
            'reporterId': reporter_id,
            'reportedId': reported_id,
            'abuseType': abuse_type,
            'additionalInfo': additional_info,
            'timestamp': timestamp,
            'serverId': server_id,
            'placeId': place_id
        }
        reports.append(report_entry)
        save_reports(reports)
        
        reports_24h = getReportsLast24H(reported_id)
        reports_month = getReportsLastMonth(reported_id)
        reporter_history = getReporterHistory(reporter_id)
        time_since_last = getTimeSinceLastReport(reported_id, exclude_timestamp=timestamp)
        most_common_reason = getMostCommonReason(reported_id, exclude_timestamp=timestamp)
        
        embed = discord.Embed(
            title="🚨 Player Report",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="📋 Abuse Type",
            value=f"**{abuse_type}**",
            inline=False
        )
        
        if additional_info and additional_info.strip():
            embed.add_field(
                name="📝 Additional Information",
                value=additional_info[:1024],
                inline=False
            )
        
        embed.add_field(
            name="👤 Reporter",
            value=f"[{reporter_name}]({reporter_profile})\nID: `{reporter_id}`\nTotal Reports Made: `{reporter_history}`",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Reported Player",
            value=f"[{reported_name}]({reported_profile})\nID: `{reported_id}`",
            inline=True
        )
        
        stats_text = f"Last 24 Hours: `{reports_24h}`\nLast Month: `{reports_month}`"
        if time_since_last:
            stats_text += f"\nLast Report: `{time_since_last}`"
        if most_common_reason:
            stats_text += f"\nMost Common Reason: `{most_common_reason}`"
        
        embed.add_field(
            name="📊 Report Statistics",
            value=stats_text,
            inline=False
        )
        
        embed.add_field(
            name="🌐 Server Information",
            value=f"Job ID: `{server_id}`\nPlace ID: `{place_id}`",
            inline=False
        )
        
        embed.set_thumbnail(url=reported_thumbnail)
        embed.set_image(url=reporter_thumbnail)
        
        embed.set_footer(text=f"Reported by {reporter_name} • Report #{len(reports)}")
        
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
    port_str = os.getenv('PORT', '5000')
    port = int(port_str) if port_str and port_str.strip() else 5000
    host = os.getenv('HOST', '0.0.0.0')
    site = web.TCPSite(runner, host, port)
    await site.start()
    print(f"[discord_bot] Web server started on http://{host}:{port}")

@bot.event
async def on_ready():
    print(f"[discord_bot] Bot logged in as {bot.user}")

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
    
    await start_web_server()
    
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())

