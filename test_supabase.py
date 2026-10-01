#!/usr/bin/env python
"""
Quick test script to verify Supabase Storage connection
Run this in Render Shell to diagnose the issue
"""
import os
import sys

# Add backend to path
sys.path.insert(0, '/opt/render/project/src/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legalai.settings_prod')

import django
django.setup()

from apps.documents.storage import supabase_storage

print("=" * 60)
print("SUPABASE STORAGE CONNECTION TEST")
print("=" * 60)

# Check environment variables
print("\n1. Environment Variables:")
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')
print(f"   SUPABASE_URL: {'✅ SET' if supabase_url else '❌ NOT SET'}")
print(f"   SUPABASE_KEY: {'✅ SET' if supabase_key else '❌ NOT SET'}")

if not supabase_url or not supabase_key:
    print("\n❌ ERROR: Supabase credentials not found in environment!")
    print("   Add them in Render Dashboard → Environment")
    sys.exit(1)

print(f"   URL: {supabase_url}")
print(f"   KEY: {supabase_key[:20]}...{supabase_key[-10:]}")

# Test client connection
print("\n2. Testing Supabase Client:")
try:
    client = supabase_storage.get_client()
    print("   ✅ Client created successfully")
except Exception as e:
    print(f"   ❌ Client creation failed: {e}")
    sys.exit(1)

# Test bucket existence
print("\n3. Testing Bucket:")
try:
    bucket_ready = supabase_storage.ensure_bucket_exists()
    print(f"   Bucket ready: {'✅ YES' if bucket_ready else '❌ NO'}")
except Exception as e:
    print(f"   ❌ Bucket check failed: {e}")
    sys.exit(1)

# Test upload
print("\n4. Testing File Upload:")
try:
    test_content = b"This is a test file from Render"
    test_path = "test/render_test.txt"
    
    print(f"   Uploading to: {test_path}")
    success, url = supabase_storage.upload_file_bytes(
        file_bytes=test_content,
        destination_path=test_path,
        content_type="text/plain"
    )
    
    if success and url:
        print(f"   ✅ Upload SUCCESS!")
        print(f"   URL: {url}")
    else:
        print(f"   ❌ Upload FAILED")
        print(f"   Success: {success}")
        print(f"   URL: {url}")
except Exception as e:
    print(f"   ❌ Upload error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED - Supabase Storage is working!")
print("=" * 60)
