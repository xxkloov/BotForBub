# Roblox Report System with Discord Bot

A comprehensive report system for Roblox games that sends player reports to Discord with analytics dashboard and admin panel.

## Features

- 🚨 **Player Reports** - Players can report others with abuse type and additional info
- 📊 **Analytics Dashboard** - View game stats, report statistics, and trends
- 👥 **Admin Panel** - Web-based interface to manage admin permissions
- 🔒 **Security** - API key authentication, rate limiting, input validation
- 💾 **Database** - SQLite (default) or PostgreSQL (Supabase) support
- 📈 **Statistics** - Most reported players, abuse type breakdown, hourly trends
- 🎮 **Game Stats** - Real-time game statistics from Roblox API

## Quick Start

### 1. Discord Bot Setup

1. Go to https://discord.com/developers/applications
2. Create a new application and bot
3. Get your bot token and channel ID
4. Invite bot to your server with "Send Messages" and "Embed Links" permissions

### 2. Deploy to Koyeb (Recommended)

**Koyeb provides 24/7 uptime for free!**

1. Go to https://www.koyeb.com and sign up
2. Click "Create App" > "GitHub"
3. Connect your repository: `xxkloov/BotForBub`
4. Settings:
   - **Name:** `roblox-report-bot`
   - **Build Command:** `pip install -r requirements.txt`
   - **Run Command:** `python discord_bot.py`
5. Environment Variables:
   ```
   DISCORD_BOT_TOKEN=your_bot_token
   DISCORD_CHANNEL_ID=your_channel_id
   ADMIN_PASSWORD=your_secure_password
   API_KEY=your_api_key_optional
   PLACE_ID=132682513110700
   ```
6. Click "Deploy"
7. Get your URL: `https://your-app.koyeb.app`

### 3. Add Persistent Storage (Recommended)

**Koyeb provides persistent storage - perfect for SQLite!**

1. In Koyeb app settings, go to **"Volumes"** section
2. Click **"Add Volume"**
3. Configure:
   - **Name:** `database-storage`
   - **Mount Path:** `/app/data`
   - **Size:** 1GB (free tier includes storage)
4. Click **"Add"**

**Note:** The bot will automatically use `/app/data/reports.db` for the database. No external database needed!

**Alternative:** If you prefer PostgreSQL, you can use Supabase and set `DATABASE_URL` environment variable.

### 4. Update Roblox Script

In your Roblox game, update `ReportServer.lua`:

```lua
local BOT_SERVER_URL = "https://your-app.koyeb.app/report"
local API_KEY = "your_api_key"  -- Optional, set in Koyeb env vars
```

### 5. Enable HTTP Service in Roblox

1. In Roblox Studio: Game Settings > Security
2. Enable "Allow HTTP Requests"
3. Add your Koyeb domain to allowed domains

## Access Points

Once deployed:

- **Dashboard:** `https://your-app.koyeb.app/dashboard` - View statistics and reports
- **Admin Panel:** `https://your-app.koyeb.app/admin` - Manage admin permissions
- **API Endpoint:** `https://your-app.koyeb.app/report` - For Roblox reports
- **Health Check:** `https://your-app.koyeb.app/` - Check if bot is online

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_BOT_TOKEN` | Yes | Discord bot token |
| `DISCORD_CHANNEL_ID` | Yes | Discord channel ID for reports |
| `ADMIN_PASSWORD` | Yes | Password for admin panel login |
| `API_KEY` | No | API key for report endpoint (optional) |
| `PLACE_ID` | No | Roblox Place ID (defaults to your game) |
| `DATABASE_URL` | No | PostgreSQL connection string (uses SQLite with Koyeb storage if not set) |
| `DATA_DIR` | No | Data directory path (default: `/app/data` for Koyeb, current dir for local) |
| `HOST` | No | Server host (default: 0.0.0.0) |
| `PORT` | No | Server port (default: 5000, Koyeb sets automatically) |

## Discord Bot Commands

Admins can use these commands in Discord:

- `!reports <user_id>` - View reports for a specific user
- `!stats` - Show report statistics
- `!recent <count>` - Show recent reports (1-20)
- `!search <term>` - Search reports by abuse type or info

## Dashboard Features

The web dashboard shows:

- **Game Statistics** - Current players, visits, favorites, likes
- **Report Statistics** - Total, today, this week, this month
- **Most Reported Players** - Top 10 with report counts
- **Recent Reports** - Last 20 reports with details
- **Abuse Type Breakdown** - Distribution of report types
- **Top Reporters** - Users who report most
- **Hourly Activity** - Reports by hour chart

## Admin Panel Features

- Add/remove Discord admins via web interface
- View all current admins
- Secure password-protected access
- Session-based authentication

## File Structure

```
ReportsDiscordBot/
├── discord_bot.py      # Main bot and web server
├── database.py          # Database operations (SQLite/PostgreSQL)
├── config.py            # Configuration management
├── logger.py            # Logging system
├── admin_panel.html     # Admin management interface
├── dashboard.html       # Analytics dashboard
├── ReportServer.lua     # Roblox server script
├── requirements.txt     # Python dependencies
├── Procfile             # Koyeb/Render deployment config
└── README.md            # This file
```

## Database

### SQLite (Default)
- No setup required
- File-based, easy backups
- Perfect for single instance
- Works on any hosting

### PostgreSQL (Supabase)
- Production-ready
- Managed backups
- Better for scaling
- Set `DATABASE_URL` to enable

## Troubleshooting

**Bot not receiving reports:**
- Check HTTP Service is enabled in Roblox
- Verify URL in `ReportServer.lua` matches your Koyeb URL
- Check Koyeb logs for errors

**Dashboard not loading:**
- Make sure you're logged in via `/admin`
- Check browser console for errors
- Verify environment variables are set

**Database errors:**
- If using Supabase, verify `DATABASE_URL` is correct
- Check Supabase dashboard for connection issues
- SQLite will create automatically if no `DATABASE_URL`

## Support

For issues or questions, check the repository: https://github.com/xxkloov/BotForBub

## License

This project is open source and available for use.
