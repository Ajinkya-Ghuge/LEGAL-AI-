# Fix Supabase Signup Issue

## Problem
Users can't signup because email confirmation is required.

## Solution

### Go to Supabase Dashboard:
1. Open: https://supabase.com/dashboard
2. Select project: `miiineezxbvmhlxavbfh`
3. Go to **Authentication** → **Providers**
4. Click on **Email** provider
5. **DISABLE** "Confirm email" option
6. Click **Save**

This allows users to signup without email verification.

### Alternative: Manual User Creation
Create users directly in dashboard:
1. **Authentication** → **Users**
2. Click **Add User** (+ button)
3. Enter:
   - Email: `test@example.com`
   - Password: `test123456`
   - Auto-confirm user: ✅ YES
4. Click **Create**

Now user can login immediately!
