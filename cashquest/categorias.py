from .supabase_client import get_supabase

supabase = get_supabase()

def listar_categorias(grupo_id):
    res = supabase.table("categorias").select("*").eq("grupo_id", grupo_id).execute()
    return res.data