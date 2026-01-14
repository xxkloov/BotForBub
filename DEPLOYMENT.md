# Deployment Guide - Koyeb with Persistent Storage

## Step-by-Step Deployment

### Option 1: Koyeb Storage (Recommended - Simpler!)

Koyeb provides persistent storage volumes perfect for SQLite databases. No external database needed!

### 1. Setup Koyeb Hosting with Storage

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
8. **Add Persistent Storage:**
   - Scroll down to **"Volumes"** section
   - Click **"Add Volume"**
   - **Name:** `database-storage`
   - **Mount Path:** `/app/data`
   - **Size:** 1GB (free tier includes storage)
   - Click **"Add"**
9. Go to **Environment Variables** tab
10. Add these variables:

```
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_discord_channel_id
ADMIN_PASSWORD=your_secure_password_here
API_KEY=your_optional_api_key
PLACE_ID=132682513110700
```

**Note:** Don't set `DATABASE_URL` - we'll use SQLite with Koyeb storage!

11. Click **"Deploy"**
12. Wait for deployment (~3-5 minutes)
13. Get your URL: `https://your-app-name.koyeb.app`

### Option 2: Supabase PostgreSQL (Optional - For Advanced Use)

If you prefer PostgreSQL, you can still use Supabase:

1. Go to https://supabase.com
2. Sign up (free account)
3. Click "New Project"
4. Fill in project details
5. Go to **Settings** > **Database**
6. Copy the **URI** connection string
7. Add to Koyeb environment variables:
   ```
   DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
   ```

### 3. Update Database Path (For Koyeb Storage)

We need to update the database to use the mounted volume. The code will automatically use `/app/data/reports.db` when deployed on Koyeb.

### 5. Update Roblox Script

1. Open `ReportServer.lua` in your Roblox project
2. Update the URL:
   ```lua
   local BOT_SERVER_URL = "https://your-app-name.koyeb.app/report"
   local API_KEY = "your_optional_api_key"  -- Same as in Koyeb
   ```
3. Save and publish your game

### 6. Enable HTTP Service in Roblox

1. In Roblox Studio: **Game Settings**
2. Go to **Security** tab
3. Enable **"Allow HTTP Requests"**
4. Add domain: `your-app-name.koyeb.app`
5. Save

### 7. Test the System

1. Visit: `https://your-app-name.koyeb.app/dashboard`
2. Login with your `ADMIN_PASSWORD`
3. Check if dashboard loads
4. Test a report from your Roblox game
5. Check Discord channel for the report

## Verification Checklist

- [ ] Koyeb app created and deployed
- [ ] Persistent volume added (`/app/data`)
- [ ] All environment variables set in Koyeb
- [ ] Koyeb deployment successful (green status)
- [ ] Dashboard accessible at `/dashboard`
- [ ] Admin panel accessible at `/admin`
- [ ] Roblox script updated with Koyeb URL
- [ ] HTTP Service enabled in Roblox
- [ ] Test report sent successfully
- [ ] Database file created in volume (check Koyeb logs)

## Monitoring

**Koyeb Logs:**
- Go to your Koyeb app dashboard
- Click "Logs" tab
- View real-time logs

**Database Location:**
- Database file: `/app/data/reports.db` (in persistent volume)
- Logs: `/app/data/logs/` (if configured)

## Backup

**Koyeb Volume Backup:**
- Koyeb volumes are persistent and survive deployments
- To backup: Download volume or use Koyeb's backup feature
- Database file location: `/app/data/reports.db`

**Manual Backup:**
- Access Koyeb console/SSH (if available)
- Copy `/app/data/reports.db` to your local machine

## Troubleshooting

**Deployment fails:**
- Check build logs in Koyeb
- Verify `requirements.txt` is correct
- Ensure Python version matches `runtime.txt`

**Database connection fails:**
- Check if volume is mounted correctly in Koyeb
- Verify `/app/data` directory exists
- Check Koyeb logs for permission errors
- Ensure volume is attached to your service

**Bot not responding:**
- Check Koyeb logs for errors
- Verify Discord token is correct
- Check channel ID is correct

## Cost

**Koyeb Free Tier:**
- 2 services
- 256MB RAM per service
- Persistent storage volumes (included)
- Always-on (no sleep)
- Free forever

**Total Cost: $0/month** ✅

**Note:** Using Koyeb storage is simpler and free! No need for Supabase unless you need PostgreSQL features.

