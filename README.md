# Roblox Report System with Discord Bot

This system allows players to report other players in Roblox, and sends the reports to a Discord channel with player images and details.

## Setup Instructions

### 1. Discord Bot Setup

1. Go to https://discord.com/developers/applications
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot" and confirm
5. Under "Token", click "Reset Token" and copy the token
6. Enable "Message Content Intent" under "Privileged Gateway Intents"
7. Go to "OAuth2" > "URL Generator"
8. Select scopes: `bot` and `applications.commands`
9. Select bot permissions: `Send Messages`, `Embed Links`, `Attach Files`
10. Copy the generated URL and open it in your browser to invite the bot to your server
11. Get your Discord channel ID (enable Developer Mode in Discord, right-click channel, Copy ID)

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

## Cloud Hosting (Run Bot 24/7 Without Your PC)

You don't need to keep your PC running! Here are free/paid hosting options:

### Option 1: Railway (Recommended - Free Tier Available)

1. Go to https://railway.app and sign up with GitHub
2. Click "New Project" > "Deploy from GitHub repo"
3. Connect your repository or create a new one
4. Add environment variables in Railway dashboard:
   - `DISCORD_BOT_TOKEN`
   - `DISCORD_CHANNEL_ID`
   - `PORT` (Railway sets this automatically, but you can set it manually)
5. Railway will automatically deploy and keep your bot running 24/7
6. Get your public URL from Railway (e.g., `https://your-app.railway.app`)
7. Update `BOT_SERVER_URL` in Manager.lua to: `https://your-app.railway.app/report`

### Option 2: Render (Free Tier Available)

1. Go to https://render.com and sign up
2. Click "New" > "Web Service"
3. Connect your GitHub repository
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python discord_bot.py`
   - **Environment:** Python 3
5. Add environment variables:
   - `DISCORD_BOT_TOKEN`
   - `DISCORD_CHANNEL_ID`
   - `PORT` (Render sets this automatically)
6. Deploy and get your public URL
7. Update `BOT_SERVER_URL` in Manager.lua

### Option 3: Heroku (Paid, but has free alternatives)

1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
2. Login: `heroku login`
3. Create app: `heroku create your-bot-name`
4. Set environment variables:
   ```bash
   heroku config:set DISCORD_BOT_TOKEN=your_token
   heroku config:set DISCORD_CHANNEL_ID=your_channel_id
   ```
5. Deploy: `git push heroku main`
6. Get URL: `heroku info` (will show web URL)
7. Update `BOT_SERVER_URL` in Manager.lua

### Option 4: Replit (Free, but may sleep)

1. Go to https://replit.com
2. Create new Python repl
3. Upload your files
4. Set environment variables in Secrets tab
5. Run the bot (use "Always On" for paid plan, or free tier may sleep)

### Option 5: VPS (DigitalOcean, Linode, etc.)

For more control, rent a VPS ($5-10/month):
1. Create Ubuntu server
2. SSH into it
3. Install Python and dependencies
4. Use `screen` or `tmux` to keep bot running:
   ```bash
   screen -S discordbot
   python discord_bot.py
   # Press Ctrl+A then D to detach
   ```

### After Hosting

Once your bot is hosted, update `Manager.lua`:

```lua
local BOT_SERVER_URL = "https://your-hosting-url.com/report"
```

Make sure to:
- Add the domain to Roblox HTTP Service allowed domains
- Use HTTPS if your hosting provides it (most do)
- Test the connection from Roblox

## Troubleshooting

- **Bot not receiving reports:** Check that HTTP Service is enabled in Roblox and the URL is correct
- **Channel not found:** Verify the CHANNEL_ID is correct and the bot has access to the channel
- **Connection errors:** Make sure the bot server is running and accessible from Roblox servers
- **Bot goes offline:** Check hosting service logs, ensure environment variables are set correctly
- **Port issues:** Most cloud services set PORT automatically via environment variable

