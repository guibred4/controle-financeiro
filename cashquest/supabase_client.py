# supabase_client.py
from supabase import create_client, Client
import os

# Pega URL e KEY do ambiente
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL ou KEY não configurados!")
    return create_client(SUPABASE_URL, SUPABASE_KEY)
