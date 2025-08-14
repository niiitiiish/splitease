# Deploy SpliEase to Render with Neon Database

## 🚀 Quick Deployment Steps

### 1. Commit Your Changes
```bash
git add .
git commit -m "Switch to Neon database and fix startup issues"
git push origin main
```

### 2. Update Render Environment Variables
1. Go to [render.com](https://render.com) and sign in
2. Find your SpliEase service
3. Click on your service name
4. Go to "Environment" tab
5. Add/update the `DATABASE_URL` environment variable with:
   ```
   postgresql://neondb_owner:npg_1AxtOX3Jlvud@ep-weathered-boat-ad256w08-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
   ```

### 3. Redeploy
1. Go to "Manual Deploy" tab
2. Click "Deploy latest commit"
3. Wait for deployment to complete

## 🔧 What Changed

### Fixed Issues:
- ✅ Moved database table creation to startup event
- ✅ Added proper error handling for database connection
- ✅ Updated database configuration to use environment variables
- ✅ Added SSL support for Neon database

### Database Migration:
- ✅ From: Expired Render PostgreSQL
- ✅ To: Neon PostgreSQL (free tier)

## 📊 Neon Database Info
- **Host:** ep-weathered-boat-ad256w08-pooler.c-2.us-east-1.aws.neon.tech
- **Database:** neondb
- **Username:** neondb_owner
- **Storage:** 0.5GB (free tier)
- **No time limits** (unlike Render's 90-day limit)

## 🧪 Test Your Deployment
After deployment, test these features:
1. **Registration:** Create a new account
2. **Login:** Use admin/admin123 or create new user
3. **Groups:** Create and manage expense groups
4. **Expenses:** Add and track expenses

## 🚨 Troubleshooting

### If deployment fails:
1. Check Render logs for errors
2. Verify `DATABASE_URL` environment variable is set correctly
3. Ensure Neon database is accessible

### If database connection fails:
1. Check Neon dashboard for connection status
2. Verify SSL settings in connection string
3. Test connection locally first

## 🎯 Next Steps
1. ✅ Deploy to Render
2. ✅ Test all features
3. ✅ Monitor performance
4. 🚀 Share your app with users!

Your SpliEase app will now work reliably with Neon's free database service! 