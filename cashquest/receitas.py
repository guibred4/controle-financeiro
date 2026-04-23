from .supabase_client import get_supabase

supabase = get_supabase()

def listar_receitas(grupo_id, data_inicio=None, data_fim=None):
    query = supabase.table("receitas").select("*").eq("grupo_id", grupo_id)
    if data_inicio:
        query = query.gte("data", str(data_inicio))
    if data_fim:
        query = query.lte("data", str(data_fim))
    res = query.execute()
    return res.data

def adicionar_receita(grupo_id, descricao, valor, data):
    if isinstance(data, str):
        data_str = data
    else:
        data_str = data.strftime("%Y-%m-%d")

    supabase.table("receitas").insert({
        "descricao": descricao,
        "valor": valor,
        "grupo_id": grupo_id,
        "data": data_str
    }).execute()