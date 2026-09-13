import asyncio
import os
from supabase import create_client

async def main():
    # Use dummy credentials to see the error type for invalid password or existing user
    url = "https://example.supabase.co"
    key = "dummy"
    try:
        supabase = create_client(url, key)
        result = supabase.auth.sign_up({"email": "test@example.com", "password": "123"})
        print(result)
    except Exception as e:
        print("EXCEPTION CAUGHT:", type(e))
        print("MESSAGE:", str(e))
        if hasattr(e, 'message'):
            print("e.message:", e.message)
        if hasattr(e, 'to_dict'):
            print("e.to_dict:", e.to_dict())

if __name__ == "__main__":
    asyncio.run(main())
