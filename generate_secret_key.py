"""
Generate a new Django SECRET_KEY
Run: python generate_secret_key.py
"""
from django.core.management.utils import get_random_secret_key

print("\n" + "="*70)
print("🔐 NEW DJANGO SECRET KEY")
print("="*70)
print("\nAdd this to your .env file:")
print(f"\nSECRET_KEY={get_random_secret_key()}")
print("\n" + "="*70)
print("⚠️  NEVER commit this key to version control!")
print("="*70 + "\n")
