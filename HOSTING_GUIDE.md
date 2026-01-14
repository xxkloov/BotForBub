# Hosting & Database Guide

## Best Free Hosting Options (24/7 Uptime)

### 🏆 Option 1: Koyeb (BEST for 24/7 - Always On)

**Why Koyeb:**
- ✅ **Always-on** (never sleeps)
- ✅ 256MB RAM (enough for this bot)
- ✅ 2 free services
- ✅ Auto-deploy from GitHub
- ✅ Free SSL/HTTPS
- ✅ No credit card required

**Setup:**
1. Go to https://www.koyeb.com and sign up
2. Click "Create App" > "GitHub"
3. Connect your repository
4. Settings:
   - **Name:** `roblox-report-bot`
   - **Build Command:** `pip install -r requirements.txt`
   - **Run Command:** `python discord_bot.py`
5. Environment Variables:
   - `DISCORD_BOT_TOKEN`
   - `DISCORD_CHANNEL_ID`
   - `API_KEY` (optional)
   - `ADMIN_PASSWORD`
   - `PLACE_ID` (optional, defaults to your game)
6. Click "Deploy"
7. Get URL: `https://your-app.koyeb.app`

**Pros:** Always-on, simple setup, reliable
**Cons:** Limited to 256MB RAM (should be fine)

---

### 🥈 Option 2: Fly.io (Great for 24/7)

**Why Fly.io:**
- ✅ Always-on free tier
- ✅ 3GB storage
- ✅ 3 shared VMs
- ✅ 160GB outbound data/month
- ✅ Good performance

**Setup:**
1. Go to https://fly.io and sign up
2. Install Fly CLI: https://fly.io/docs/getting-started/installing-flyctl/
3. Login: `flyctl auth login`
4. In project directory: `flyctl launch`
5. Set secrets:
   ```bash
   flyctl secrets set DISCORD_BOT_TOKEN=your_token
   flyctl secrets set DISCORD_CHANNEL_ID=your_channel_id
   flyctl secrets set ADMIN_PASSWORD=your_password
   ```
6. Deploy: `flyctl deploy`

**Pros:** More resources, always-on
**Cons:** Requires CLI setup

---

### 🥉 Option 3: Railway (Easy Setup)

**Why Railway:**
- ✅ Always-on free tier
- ✅ $5 free credit monthly
- ✅ Easy GitHub integration
- ✅ Built-in PostgreSQL option

**Setup:**
1. Go to https://railway.app and sign up
2. Click "New Project" > "Deploy from GitHub"
3. Select your repository
4. Add environment variables in Settings
5. Deploy automatically

**Pros:** Easy, includes database options
**Cons:** Limited free credit

---

## Database Options

### Current: SQLite (File-based)
- ✅ Simple, no setup needed
- ✅ Works great for small-medium apps
- ✅ Zero configuration
- ⚠️ File-based (can lose data if hosting resets)
- ⚠️ Not ideal for multiple instances

**Best for:** Single instance, simple deployments

---

### Recommended: PostgreSQL (Production-ready)

**Free PostgreSQL Options:**

#### Option A: Supabase (Recommended)
- ✅ 500MB database free
- ✅ Always free tier
- ✅ Managed backups
- ✅ Easy connection
- ✅ Web dashboard

**Setup:**
1. Go to https://supabase.com
2. Create new project
3. Get connection string from Settings > Database
4. Set `DATABASE_URL` environment variable

#### Option B: Railway PostgreSQL
- ✅ Free with Railway hosting
- ✅ 1GB storage
- ✅ Automatic backups
- ✅ Integrated with Railway

#### Option C: Render PostgreSQL
- ✅ Free tier available
- ✅ 90 days retention
- ✅ Easy setup

**Pros:** Production-ready, reliable, scalable
**Cons:** Requires setup, slightly more complex

---

## Recommended Setup

### For Best 24/7 Uptime:
1. **Hosting:** Koyeb (always-on, simple)
2. **Database:** Supabase PostgreSQL (free, reliable, separate from hosting)

### For Easy Setup:
1. **Hosting:** Railway (includes free PostgreSQL)
2. **Database:** Railway PostgreSQL (integrated)

### For Maximum Simplicity:
1. **Hosting:** Koyeb
2. **Database:** SQLite (current, works fine for single instance)

---

## Migration Guide

The code supports both SQLite (current) and PostgreSQL. To switch:

1. Set `DATABASE_URL` environment variable:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

2. The bot will automatically use PostgreSQL if `DATABASE_URL` is set, otherwise SQLite.

---

## Storage Requirements

- **SQLite:** ~1-10MB for thousands of reports
- **PostgreSQL:** ~50-100MB for thousands of reports (includes overhead)

Both are well within free tier limits.

---

## Recommendation

**Best Overall:** Koyeb + Supabase PostgreSQL
- Always-on hosting
- Reliable database with backups
- Both free forever
- Easy to set up

**Simplest:** Koyeb + SQLite
- Always-on hosting
- No database setup needed
- Works great for single instance

