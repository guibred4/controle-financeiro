from supabase import create_client, Client
import os

SUPABASE_URL = "https://<sua-url>.supabase.co"
SUPABASE_KEY = "<sua-anon-key>"

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)
