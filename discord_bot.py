import discord
from discord.ext import commands
from aiohttp import web, ClientSession
from aiohttp.web import Response
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Tuple, Dict, Optional
import time
import secrets
import hashlib
import json

import database
import logger
import config

log = logger.setup_logger("discord_bot")

intents = discord.Intents.default()
intents.message_content = True
try:
    bot = commands.Bot(command_prefix='!', intents=intents)
except discord.PrivilegedIntentsRequired:
    log.warning("Message Content Intent not enabled. Using default intents without message_content.")
    intents.message_content = False
    bot = commands.Bot(command_prefix='!', intents=intents)

CHANNEL_ID = config.DISCORD_CHANNEL_ID
app = web.Application()
routes = web.RouteTableDef()

rate_limit_store = defaultdict(list)

def check_rate_limit(ip: str) -> bool:
    now = time.time()
    window_start = now - config.RATE_LIMIT_WINDOW
    
    requests = rate_limit_store[ip]
    requests[:] = [req_time for req_time in requests if req_time > window_start]
    
    if len(requests) >= config.RATE_LIMIT_REQUESTS:
        return False
    
    requests.append(now)
    return True

def validate_report_data(data: dict) -> Tuple[bool, str]:
    if not isinstance(data, dict):
        return False, "Invalid data format"
    
    reporter = data.get('reporter', {})
    reported = data.get('reported', {})
    
    if not isinstance(reporter, dict) or not isinstance(reported, dict):
        return False, "Invalid reporter or reported data"
    
    reporter_id = reporter.get('userId', 0)
    reported_id = reported.get('userId', 0)
    
    if not isinstance(reporter_id, int) or reporter_id <= 0:
        return False, "Invalid reporter user ID"
    
    if not isinstance(reported_id, int) or reported_id <= 0:
        return False, "Invalid reported user ID"
    
    abuse_type = data.get('abuseType', '')
    if not isinstance(abuse_type, str) or len(abuse_type) > 100:
        return False, "Invalid abuse type"
    
    additional_info = data.get('additionalInfo', '')
    if not isinstance(additional_info, str) or len(additional_info) > 2000:
        return False, "Invalid additional info"
    
    return True, ""

@routes.get('/')
async def health_check(request):
    return web.json_response({"status": "online", "bot": "ready"})

@routes.post('/report')
async def handle_report(request):
    client_ip = request.remote
    
    if not check_rate_limit(client_ip):
        log.warning(f"Rate limit exceeded for IP: {client_ip}")
        return web.json_response(
            {"status": "error", "message": "Rate limit exceeded"},
            status=429,
            headers={"Retry-After": str(config.RATE_LIMIT_WINDOW)}
        )
    
    if config.API_KEY and config.API_KEY != "":
        api_key = request.headers.get('X-API-Key', '')
        if api_key != config.API_KEY:
            log.warning(f"Invalid API key from IP: {client_ip}")
            return web.json_response(
                {"status": "error", "message": "Unauthorized"},
                status=401
            )
    
    try:
        data = await request.json()
        
        is_valid, error_msg = validate_report_data(data)
        if not is_valid:
            log.warning(f"Invalid report data from IP {client_ip}: {error_msg}")
            return web.json_response(
                {"status": "error", "message": error_msg},
                status=400
            )
        
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
        
        report_id = await database.add_report(
            reporter_id, reported_id, abuse_type, additional_info,
            timestamp, str(server_id), place_id
        )
        
        log.info(f"Report #{report_id} received: {reported_id} reported by {reporter_id}")
        
        reports_24h = await database.get_reports_last_24h(reported_id)
        reports_month = await database.get_reports_last_month(reported_id)
        reporter_history = await database.get_reporter_history(reporter_id)
        time_since_last = await database.get_time_since_last_report(reported_id, exclude_timestamp=timestamp)
        most_common_reason = await database.get_most_common_reason(reported_id, exclude_timestamp=timestamp)
        
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
        
        total_reports = await database.get_report_stats()
        embed.set_footer(text=f"Reported by {reporter_name} • Report #{report_id} • Total: {total_reports['total_reports']}")
        
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            try:
                await channel.send(embed=embed)
                log.info(f"Report #{report_id} sent to Discord channel")
            except discord.errors.HTTPException as e:
                log.error(f"Failed to send embed to Discord: {e}")
                return web.json_response(
                    {"status": "error", "message": "Failed to send to Discord"},
                    status=500
                )
        else:
            log.error(f"Channel {CHANNEL_ID} not found!")
            return web.json_response(
                {"status": "error", "message": "Discord channel not found"},
                status=500
            )
        
        return web.json_response({"status": "success", "report_id": report_id})
    
    except Exception as e:
        log.error(f"Error handling report from IP {client_ip}: {e}", exc_info=True)
        return web.json_response(
            {"status": "error", "message": "Internal server error"},
            status=500
        )

async def is_admin(user_id: int) -> bool:
    if config.ADMIN_USER_IDS and user_id in config.ADMIN_USER_IDS:
        return True
    return await database.is_admin(user_id)

@bot.command(name='reports')
async def reports_command(ctx, user_id: int = None):
    if not await is_admin(ctx.author.id):
        await ctx.send("❌ You don't have permission to use this command.")
        return
    
    if not user_id:
        await ctx.send("❌ Usage: `!reports <user_id>`")
        return
    
    try:
        reports = await database.get_reports_by_user(user_id, limit=10)
        
        if not reports:
            await ctx.send(f"📋 No reports found for user ID: `{user_id}`")
            return
        
        embed = discord.Embed(
            title=f"📋 Reports for User {user_id}",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        report_text = ""
        for i, report in enumerate(reports[:5], 1):
            timestamp_str = datetime.fromtimestamp(report['timestamp']).strftime('%Y-%m-%d %H:%M')
            report_text += f"**{i}.** {report['abuse_type']} - {timestamp_str}\n"
            if report['additional_info']:
                info_preview = report['additional_info'][:50]
                report_text += f"   *{info_preview}...*\n"
        
        if len(reports) > 5:
            report_text += f"\n*... and {len(reports) - 5} more*"
        
        embed.add_field(name="Recent Reports", value=report_text or "None", inline=False)
        embed.set_footer(text=f"Total: {len(reports)} reports")
        
        await ctx.send(embed=embed)
        log.info(f"Admin {ctx.author.id} queried reports for user {user_id}")
    
    except ValueError:
        await ctx.send("❌ Invalid user ID. Please provide a number.")
    except Exception as e:
        log.error(f"Error in reports command: {e}", exc_info=True)
        await ctx.send("❌ An error occurred while fetching reports.")

@bot.command(name='stats')
async def stats_command(ctx):
    if not await is_admin(ctx.author.id):
        await ctx.send("❌ You don't have permission to use this command.")
        return
    
    try:
        stats = await database.get_report_stats()
        
        embed = discord.Embed(
            title="📊 Report Statistics",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="Total Reports", value=f"`{stats['total_reports']}`", inline=True)
        embed.add_field(name="Today's Reports", value=f"`{stats['today_reports']}`", inline=True)
        embed.add_field(name="Unique Reported Users", value=f"`{stats['unique_reported']}`", inline=True)
        embed.add_field(name="Most Common Abuse Type", value=f"`{stats['top_abuse_type']}`", inline=False)
        
        await ctx.send(embed=embed)
        log.info(f"Admin {ctx.author.id} queried statistics")
    
    except Exception as e:
        log.error(f"Error in stats command: {e}", exc_info=True)
        await ctx.send("❌ An error occurred while fetching statistics.")

@bot.command(name='recent')
async def recent_command(ctx, count: int = 10):
    if not await is_admin(ctx.author.id):
        await ctx.send("❌ You don't have permission to use this command.")
        return
    
    if count < 1 or count > 20:
        await ctx.send("❌ Count must be between 1 and 20.")
        return
    
    try:
        reports = await database.get_recent_reports(limit=count)
        
        if not reports:
            await ctx.send("📋 No reports found.")
            return
        
        embed = discord.Embed(
            title=f"📋 Recent Reports ({len(reports)})",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow()
        )
        
        report_text = ""
        for i, report in enumerate(reports, 1):
            timestamp_str = datetime.fromtimestamp(report['timestamp']).strftime('%m-%d %H:%M')
            report_text += f"**{i}.** User `{report['reported_id']}` - {report['abuse_type']} - {timestamp_str}\n"
        
        embed.add_field(name="Reports", value=report_text[:1024] or "None", inline=False)
        
        await ctx.send(embed=embed)
        log.info(f"Admin {ctx.author.id} queried recent {count} reports")
    
    except ValueError:
        await ctx.send("❌ Invalid count. Please provide a number.")
    except Exception as e:
        log.error(f"Error in recent command: {e}", exc_info=True)
        await ctx.send("❌ An error occurred while fetching recent reports.")

@bot.command(name='search')
async def search_command(ctx, *, search_term: str = None):
    if not await is_admin(ctx.author.id):
        await ctx.send("❌ You don't have permission to use this command.")
        return
    
    if not search_term:
        await ctx.send("❌ Usage: `!search <term>`")
        return
    
    try:
        reports = await database.search_reports(search_term, limit=10)
        
        if not reports:
            await ctx.send(f"📋 No reports found matching: `{search_term}`")
            return
        
        embed = discord.Embed(
            title=f"🔍 Search Results for: {search_term}",
            color=discord.Color.purple(),
            timestamp=discord.utils.utcnow()
        )
        
        report_text = ""
        for i, report in enumerate(reports, 1):
            timestamp_str = datetime.fromtimestamp(report['timestamp']).strftime('%m-%d %H:%M')
            report_text += f"**{i}.** User `{report['reported_id']}` - {report['abuse_type']} - {timestamp_str}\n"
        
        embed.add_field(name="Results", value=report_text[:1024] or "None", inline=False)
        embed.set_footer(text=f"Found {len(reports)} results")
        
        await ctx.send(embed=embed)
        log.info(f"Admin {ctx.author.id} searched for: {search_term}")
    
    except Exception as e:
        log.error(f"Error in search command: {e}", exc_info=True)
        await ctx.send("❌ An error occurred while searching reports.")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

async def check_auth(request: web.Request) -> bool:
    session_token = request.cookies.get('admin_session', '')
    if session_token:
        return await database.validate_admin_session(session_token)
    return False

@routes.post('/admin/login')
async def admin_login(request):
    try:
        data = await request.json()
        password = data.get('password', '')
        
        if hash_password(password) == hash_password(config.ADMIN_PASSWORD):
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=24)
            
            await database.create_admin_session(session_token, expires_at)
            
            response = web.json_response({"status": "success", "message": "Login successful"})
            response.set_cookie('admin_session', session_token, max_age=86400, httponly=True, samesite='Lax')
            return response
        else:
            return web.json_response({"status": "error", "message": "Invalid password"}, status=401)
    except Exception as e:
        log.error(f"Error in admin login: {e}", exc_info=True)
        return web.json_response({"status": "error", "message": "Internal server error"}, status=500)

@routes.post('/admin/logout')
async def admin_logout(request):
    response = web.json_response({"status": "success", "message": "Logged out"})
    response.del_cookie('admin_session')
    return response

@routes.get('/admin/check')
async def admin_check(request):
    is_authenticated = await check_auth(request)
    return web.json_response({"authenticated": is_authenticated})

@routes.get('/admin/admins')
async def get_admins(request):
    if not await check_auth(request):
        return web.json_response({"status": "error", "message": "Unauthorized"}, status=401)
    
    try:
        admins = await database.get_all_admins()
        return web.json_response({"status": "success", "admins": admins})
    except Exception as e:
        log.error(f"Error getting admins: {e}", exc_info=True)
        return web.json_response({"status": "error", "message": "Internal server error"}, status=500)

@routes.post('/admin/admins')
async def add_admin_endpoint(request):
    if not await check_auth(request):
        return web.json_response({"status": "error", "message": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        user_id = data.get('user_id')
        
        if not user_id or not isinstance(user_id, int):
            return web.json_response({"status": "error", "message": "Invalid user_id"}, status=400)
        
        success = await database.add_admin(user_id)
        if success:
            log.info(f"Admin added via web panel: {user_id}")
            return web.json_response({"status": "success", "message": "Admin added successfully"})
        else:
            return web.json_response({"status": "error", "message": "Failed to add admin"}, status=500)
    except Exception as e:
        log.error(f"Error adding admin: {e}", exc_info=True)
        return web.json_response({"status": "error", "message": "Internal server error"}, status=500)

@routes.delete('/admin/admins/{user_id}')
async def remove_admin_endpoint(request):
    if not await check_auth(request):
        return web.json_response({"status": "error", "message": "Unauthorized"}, status=401)
    
    try:
        user_id = int(request.match_info['user_id'])
        success = await database.remove_admin(user_id)
        if success:
            log.info(f"Admin removed via web panel: {user_id}")
            return web.json_response({"status": "success", "message": "Admin removed successfully"})
        else:
            return web.json_response({"status": "error", "message": "Admin not found"}, status=404)
    except ValueError:
        return web.json_response({"status": "error", "message": "Invalid user_id"}, status=400)
    except Exception as e:
        log.error(f"Error removing admin: {e}", exc_info=True)
        return web.json_response({"status": "error", "message": "Internal server error"}, status=500)

async def fetch_roblox_game_stats(place_id: str) -> Optional[Dict]:
    if not place_id:
        return None
    
    try:
        async with ClientSession() as session:
            place_url = f"https://games.roblox.com/v1/games?placeIds={place_id}"
            async with session.get(place_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('data') and len(data['data']) > 0:
                        place_data = data['data'][0]
                        universe_id = place_data.get('universeId')
                        
                        if universe_id:
                            universe_url = f"https://games.roblox.com/v1/games?universeIds={universe_id}"
                            async with session.get(universe_url, timeout=10) as universe_response:
                                if universe_response.status == 200:
                                    universe_data = await universe_response.json()
                                    if universe_data.get('data') and len(universe_data['data']) > 0:
                                        universe_info = universe_data['data'][0]
                                        return {
                                            "name": universe_info.get('name', 'Unknown'),
                                            "playing": universe_info.get('playing', 0),
                                            "visits": universe_info.get('visits', 0),
                                            "favorites": universe_info.get('favoritedCount', 0),
                                            "likes": universe_info.get('likes', 0),
                                            "maxPlayers": universe_info.get('maxPlayers', 0),
                                            "created": universe_info.get('created', ''),
                                            "updated": universe_info.get('updated', ''),
                                            "universeId": universe_id,
                                            "placeId": place_id
                                        }
                        
                        return {
                            "name": place_data.get('name', 'Unknown'),
                            "playing": place_data.get('playing', 0),
                            "visits": place_data.get('visits', 0),
                            "favorites": place_data.get('favoritedCount', 0),
                            "likes": place_data.get('likes', 0),
                            "maxPlayers": place_data.get('maxPlayers', 0),
                            "created": place_data.get('created', ''),
                            "updated": place_data.get('updated', ''),
                            "placeId": place_id
                        }
    except Exception as e:
        log.error(f"Error fetching Roblox game stats: {e}", exc_info=True)
        return None

@routes.get('/api/dashboard')
async def dashboard_data(request):
    if not await check_auth(request):
        return web.json_response({"status": "error", "message": "Unauthorized"}, status=401)
    
    try:
        game_stats = await fetch_roblox_game_stats(config.PLACE_ID)
        
        report_stats = await database.get_report_stats()
        most_reported = await database.get_most_reported_players(10)
        recent_reports = await database.get_recent_reports_detailed(20)
        abuse_types = await database.get_reports_by_abuse_type()
        top_reporters = await database.get_top_reporters(10)
        reports_by_hour = await database.get_reports_by_hour()
        
        today_reports = await database.get_reports_today()
        week_reports = await database.get_reports_this_week()
        month_reports = await database.get_reports_this_month()
        
        return web.json_response({
            "status": "success",
            "game_stats": game_stats,
            "report_stats": {
                **report_stats,
                "today": today_reports,
                "week": week_reports,
                "month": month_reports
            },
            "most_reported": most_reported,
            "recent_reports": recent_reports,
            "abuse_types": abuse_types,
            "top_reporters": top_reporters,
            "reports_by_hour": reports_by_hour
        })
    except Exception as e:
        log.error(f"Error getting dashboard data: {e}", exc_info=True)
        return web.json_response({"status": "error", "message": "Internal server error"}, status=500)

@routes.get('/admin')
async def admin_panel(request):
    import os
    html_path = os.path.join(os.path.dirname(__file__), 'admin_panel.html')
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return Response(text=html_content, content_type='text/html')
    except FileNotFoundError:
        return Response(text="Admin panel not found", status=404)

@routes.get('/dashboard')
async def dashboard_panel(request):
    import os
    html_path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return Response(text=html_content, content_type='text/html')
    except FileNotFoundError:
        return Response(text="Dashboard not found", status=404)

app.router.add_routes(routes)

async def start_web_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, config.HOST, config.PORT)
    await site.start()
    log.info(f"Web server started on http://{config.HOST}:{config.PORT}")

@bot.event
async def on_ready():
    log.info(f"Bot logged in as {bot.user} (ID: {bot.user.id})")
    log.info(f"Bot is in {len(bot.guilds)} guild(s)")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    log.error(f"Command error in {ctx.command}: {error}", exc_info=True)
    await ctx.send(f"❌ An error occurred: {error}")

async def cleanup_sessions_task():
    while True:
        try:
            await asyncio.sleep(3600)
            await database.cleanup_expired_sessions()
            log.debug("Cleaned up expired admin sessions")
        except Exception as e:
            log.error(f"Error cleaning up sessions: {e}", exc_info=True)

async def main():
    try:
        await database.init_database()
        log.info("Database initialized")
        
        await database.migrate_json_to_db()
        log.info("JSON migration completed (if applicable)")
        
        if config.ADMIN_USER_IDS:
            for user_id in config.ADMIN_USER_IDS:
                await database.add_admin(user_id)
            log.info(f"Migrated {len(config.ADMIN_USER_IDS)} admin(s) from config to database")
        
        asyncio.create_task(cleanup_sessions_task())
        
        await start_web_server()
        
        await bot.start(config.DISCORD_BOT_TOKEN)
    
    except Exception as e:
        log.critical(f"Fatal error during startup: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Bot shutting down...")
    except Exception as e:
        log.critical(f"Fatal error: {e}", exc_info=True)
