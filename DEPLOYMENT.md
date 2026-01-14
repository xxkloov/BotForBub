# Deployment Guide - Koyeb + Supabase

## Step-by-Step Deployment

### 1. Setup Supabase Database

1. Go to https://supabase.com
2. Sign up (free account)
3. Click "New Project"
4. Fill in:
   - **Name:** `roblox-report-bot`
   - **Database Password:** (save this!)
   - **Region:** Choose closest to you
5. Wait for project creation (~2 minutes)
6. Go to **Settings** > **Database**
7. Find **Connection string** section
8. Copy the **URI** connection string:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
9. Replace `[YOUR-PASSWORD]` with your actual password
10. Save this - you'll need it for Koyeb

### 2. Setup Koyeb Hosting

1. Go to https://www.koyeb.com
2. Sign up (free account, no credit card)
3. Click **"Create App"**
4. Select **"GitHub"**
5. Authorize Koyeb to access your GitHub
6. Select repository: `xxkloov/BotForBub`
7. Configure app:
   - **Name:** `roblox-report-bot`
   - **Region:** Choose closest to you
   - **Build Command:** `pip install -r requirements.txt`
   - **Run Command:** `python discord_bot.py`
8. Go to **Environment Variables** tab
9. Add these variables:

```
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_discord_channel_id
ADMIN_PASSWORD=your_secure_password_here
API_KEY=your_optional_api_key
PLACE_ID=132682513110700
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
```

10. Click **"Deploy"**
11. Wait for deployment (~3-5 minutes)
12. Get your URL: `https://your-app-name.koyeb.app`

### 3. Update Roblox Script

1. Open `ReportServer.lua` in your Roblox project
2. Update the URL:
   ```lua
   local BOT_SERVER_URL = "https://your-app-name.koyeb.app/report"
   local API_KEY = "your_optional_api_key"  -- Same as in Koyeb
   ```
3. Save and publish your game

### 4. Enable HTTP Service in Roblox

1. In Roblox Studio: **Game Settings**
2. Go to **Security** tab
3. Enable **"Allow HTTP Requests"**
4. Add domain: `your-app-name.koyeb.app`
5. Save

### 5. Test the System

1. Visit: `https://your-app-name.koyeb.app/dashboard`
2. Login with your `ADMIN_PASSWORD`
3. Check if dashboard loads
4. Test a report from your Roblox game
5. Check Discord channel for the report

## Verification Checklist

- [ ] Supabase project created
- [ ] Database connection string copied
- [ ] Koyeb app created and deployed
- [ ] All environment variables set in Koyeb
- [ ] Koyeb deployment successful (green status)
- [ ] Dashboard accessible at `/dashboard`
- [ ] Admin panel accessible at `/admin`
- [ ] Roblox script updated with Koyeb URL
- [ ] HTTP Service enabled in Roblox
- [ ] Test report sent successfully

## Monitoring

**Koyeb Logs:**
- Go to your Koyeb app dashboard
- Click "Logs" tab
- View real-time logs

**Supabase Dashboard:**
- Go to Supabase project
- Click "Table Editor" to see reports
- Check "Database" > "Connection Pooling" for stats

## Backup

**Database Backup (Supabase):**
- Supabase automatically backs up daily
- Go to Settings > Database > Backups
- Can restore from any backup point

**SQLite Backup (if not using Supabase):**
- Download `reports.db` from Koyeb
- Or use Koyeb's volume persistence

## Troubleshooting

**Deployment fails:**
- Check build logs in Koyeb
- Verify `requirements.txt` is correct
- Ensure Python version matches `runtime.txt`

**Database connection fails:**
- Verify `DATABASE_URL` format is correct
- Check Supabase project is active
- Ensure password in URL is correct (URL-encoded if needed)

**Bot not responding:**
- Check Koyeb logs for errors
- Verify Discord token is correct
- Check channel ID is correct

## Cost

**Koyeb Free Tier:**
- 2 services
- 256MB RAM per service
- Always-on (no sleep)
- Free forever

**Supabase Free Tier:**
- 500MB database
- 2GB bandwidth
- Free forever

**Total Cost: $0/month** ✅

