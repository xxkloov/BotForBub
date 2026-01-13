# Roblox Report System with Discord Bot

This system allows players to report other players in Roblox, and sends the reports to a Discord channel with player images and details.

## Setup Instructions

### 1. Discord Bot Setup

#### Step 1: Create Discord Application

1. Go to https://discord.com/developers/applications
2. Click "New Application" and give it a name (e.g., "Roblox Report Bot")
3. Click "Create"

#### Step 2: Create Bot and Get Token

1. In the left sidebar, click "Bot"
2. Click "Add Bot" and confirm
3. Under "Token" section, click "Reset Token" or "Copy" (if it's already visible)
4. **COPY THIS TOKEN** - This is your `DISCORD_BOT_TOKEN`
   - ⚠️ **IMPORTANT:** Never share this token! It's like a password for your bot
   - Example format: `YOUR_BOT_TOKEN_HERE` (long string of letters and numbers)
5. Click "Save Changes" (no privileged intents needed - bot only sends messages)

#### Step 3: Invite Bot to Your Server

1. Go to "OAuth2" > "URL Generator" in the left sidebar
2. Under "Scopes", check:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Under "Bot Permissions", check:
   - ✅ `Send Messages`
   - ✅ `Embed Links`
   - ✅ `Attach Files`
   - ✅ `Read Message History` (optional but recommended)
4. Copy the generated URL at the bottom
5. Open the URL in your browser
6. Select your Discord server and click "Authorize"
7. Complete any CAPTCHA if prompted

#### Step 4: Get Channel ID

1. Open Discord app or web
2. Go to User Settings (gear icon) > Advanced
3. Enable "Developer Mode" (toggle it ON)
4. Go to your Discord server
5. Right-click on the channel where you want reports to be sent
6. Click "Copy ID" at the bottom
7. **This is your `DISCORD_CHANNEL_ID`**
   - Example: `123456789012345678` (just numbers)

**Quick Summary:**
- **Token** = Bot's password (from Discord Developer Portal > Bot > Token)
- **Channel ID** = The channel where reports will be posted (right-click channel > Copy ID)

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file or set environment variables:

**Windows (PowerShell):**
```powershell
$env:DISCORD_BOT_TOKEN="your_bot_token_here"
$env:DISCORD_CHANNEL_ID="your_channel_id_here"
```

**Windows (Command Prompt):**
```cmd
set DISCORD_BOT_TOKEN=your_bot_token_here
set DISCORD_CHANNEL_ID=your_channel_id_here
```

**Linux/Mac:**
```bash
export DISCORD_BOT_TOKEN="your_bot_token_here"
export DISCORD_CHANNEL_ID="your_channel_id_here"
```

### 4. Update Roblox Script

In `Manager.lua`, update the `BOT_SERVER_URL` if your server is not running on localhost:5000:

```lua
local BOT_SERVER_URL = "http://your-server-ip:5000/report"
```

**Important:** If your Roblox game is running on Roblox servers (not local), you'll need to:
- Host the bot on a server accessible from the internet
- Use a service like ngrok for testing: `ngrok http 5000`
- Update the URL in Manager.lua to point to your public URL

### 5. Enable HTTP Service in Roblox

1. In Roblox Studio, go to Game Settings
2. Navigate to Security
3. Enable "Allow HTTP Requests"
4. Add your bot server URL to the allowed domains

### 6. Run the Discord Bot

```bash
python discord_bot.py
```

The bot will:
- Connect to Discord
- Start a web server on `http://localhost:5000`
- Listen for report requests from Roblox

### 7. Test the System

The bot is now ready to receive reports from your Roblox game. When a player reports another player, you'll see an embed in your Discord channel with:
- Reporter's name and profile image
- Reported player's name and thumbnail
- The reason for the report
- Server and place information

## Cloud Hosting (100% Free - Run Bot 24/7 Without Your PC)

You don't need to keep your PC running! Here are **completely free** hosting options (no trials, no credit cards):

### Option 1: Render (Recommended - 100% Free Forever)

**Free tier includes:** Unlimited apps, 750 hours/month (enough for 24/7), auto-deploy from GitHub

1. Go to https://render.com and sign up (free, no credit card)
2. Click "New" > "Web Service"
3. Connect your GitHub repository (`xxkloov/BotForBub`)
4. Settings:
   - **Name:** `roblox-report-bot` (or any name)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python discord_bot.py`
   - **Environment:** Python 3
5. Click "Advanced" and add environment variables:
   - `DISCORD_BOT_TOKEN` = your bot token
   - `DISCORD_CHANNEL_ID` = your channel ID
   - `PORT` = (Render sets this automatically, you can leave it)
6. Click "Create Web Service"
7. Wait for deployment (2-3 minutes)
8. Get your public URL (e.g., `https://roblox-report-bot.onrender.com`)
9. Update `BOT_SERVER_URL` in Manager.lua to: `https://roblox-report-bot.onrender.com/report`

**Note:** Free tier may spin down after 15 minutes of inactivity, but will wake up when a request comes in (takes ~30 seconds).

### Option 2: Fly.io (100% Free Forever)

**Free tier includes:** 3 shared VMs, 3GB storage, 160GB outbound data/month

1. Go to https://fly.io and sign up (free)
2. Install Fly CLI: https://fly.io/docs/getting-started/installing-flyctl/
3. Login: `flyctl auth login`
4. In your project directory, run: `flyctl launch`
5. Follow prompts (don't deploy yet)
6. Set secrets:
   ```bash
   flyctl secrets set DISCORD_BOT_TOKEN=your_token
   flyctl secrets set DISCORD_CHANNEL_ID=your_channel_id
   ```
7. Deploy: `flyctl deploy`
8. Get URL: `flyctl status` (will show app URL)
9. Update `BOT_SERVER_URL` in Manager.lua

### Option 3: Koyeb (100% Free Forever)

**Free tier includes:** 2 services, 256MB RAM, always-on (no sleep)

1. Go to https://www.koyeb.com and sign up (free)
2. Click "Create App" > "GitHub"
3. Connect your repository
4. Settings:
   - **Name:** `roblox-report-bot`
   - **Build Command:** `pip install -r requirements.txt`
   - **Run Command:** `python discord_bot.py`
5. Go to "Environment Variables" tab and add:
   - `DISCORD_BOT_TOKEN`
   - `DISCORD_CHANNEL_ID`
6. Click "Deploy"
7. Get your URL (e.g., `https://roblox-report-bot-xxxxx.koyeb.app`)
8. Update `BOT_SERVER_URL` in Manager.lua

### Option 4: Replit (Free, but sleeps after inactivity)

**Free tier:** Always free, but sleeps after 5 minutes of no activity (wakes up on request)

1. Go to https://replit.com and sign up (free)
2. Click "Create Repl" > "Python"
3. Name it `roblox-discord-bot`
4. Upload your files or use Git import:
   - Click "Version control" > "Import from GitHub"
   - Enter `xxkloov/BotForBub`
5. Go to "Secrets" (lock icon) and add:
   - `DISCORD_BOT_TOKEN`
   - `DISCORD_CHANNEL_ID`
6. Click "Run"
7. Get your Repl URL (e.g., `https://roblox-discord-bot.xxkloov.repl.co`)
8. Update `BOT_SERVER_URL` in Manager.lua

**Note:** Free Repls sleep after inactivity. Use UptimeRobot (free) to ping your Repl every 5 minutes to keep it awake.

### Option 5: PythonAnywhere (Free Tier)

**Free tier:** 1 web app, runs 24/7, but limited CPU time

1. Go to https://www.pythonanywhere.com and sign up (free)
2. Upload your files via Files tab
3. Go to Web tab > "Add a new web app"
4. Choose "Manual configuration" > Python 3.10
5. Edit WSGI file to run your bot (or use Tasks tab for scheduled tasks)
6. Set environment variables in Web tab > "Environment variables"
7. Reload web app
8. Get your URL (e.g., `https://yourusername.pythonanywhere.com`)
9. Update `BOT_SERVER_URL` in Manager.lua

### After Hosting

Once your bot is hosted, update `Manager.lua`:

```lua
local BOT_SERVER_URL = "https://your-hosting-url.com/report"
```

**Important Steps:**
1. Add the domain to Roblox HTTP Service allowed domains (in Game Settings > Security)
2. All free hosting services provide HTTPS automatically
3. Test the connection from Roblox
4. Check hosting logs if reports aren't coming through

### Keeping Free Services Awake (Optional)

Some free services (like Render free tier) may sleep after inactivity. To keep them awake:

**UptimeRobot (Free):**
1. Go to https://uptimerobot.com (free forever)
2. Sign up and create a monitor
3. Monitor type: "HTTP(s)"
4. URL: Your bot's health endpoint or main URL
5. Interval: 5 minutes
6. This will ping your service every 5 minutes to keep it awake

## Troubleshooting

- **Bot not receiving reports:** Check that HTTP Service is enabled in Roblox and the URL is correct
- **Channel not found:** Verify the CHANNEL_ID is correct and the bot has access to the channel
- **Connection errors:** Make sure the bot server is running and accessible from Roblox servers
- **Bot goes offline:** Check hosting service logs, ensure environment variables are set correctly
- **Port issues:** Most cloud services set PORT automatically via environment variable

