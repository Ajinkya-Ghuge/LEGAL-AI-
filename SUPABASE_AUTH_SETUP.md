# Supabase Authentication Setup Guide

## Step 1: Create Supabase Project

1. Go to https://supabase.com
2. Sign up / Login
3. Click "New Project"
4. Fill details:
   - Project Name: `legal-ai`
   - Database Password: (create strong password)
   - Region: (closest to you)
5. Click "Create Project"
6. Wait 2-3 minutes for setup

## Step 2: Get Your Credentials

Once project is ready:

1. Go to **Settings** (gear icon) → **API**
2. Copy these values:
   - **Project URL** (looks like: `https://xxx.supabase.co`)
   - **anon/public key** (looks like: `eyJhbGc...`)

3. Add to your `.env` file:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

## Step 3: Enable Email Authentication

1. Go to **Authentication** → **Providers**
2. Make sure **Email** is enabled
3. Configure email settings:
   - Go to **Authentication** → **Email Templates**
   - Customize templates if needed (optional)

## Step 4: Test User Creation

You can create test users in two ways:

### Option A: Via Supabase Dashboard
1. Go to **Authentication** → **Users**
2. Click "Add User"
3. Enter email and password
4. User created!

### Option B: Via Signup Page (we'll build this)
Users will sign up through your app

## Step 5: Install Supabase JS Client

```bash
pip install supabase
```

That's it! Now I'll integrate this into your Django app.
