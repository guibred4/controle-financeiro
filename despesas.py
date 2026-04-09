from supabase_client import get_supabase
import datetime

supabase = get_supabase()

def listar_despesas(grupo_id, data_inicio=None, data_fim=None):
    try:
        query = supabase.table("despesas").select("*").eq("grupo_id", grupo_id)
        if data_inicio:
            query = query.gte("data", str(data_inicio))
        if data_fim:
            query = query.lte("data", str(data_fim))
        res = query.execute()
        despesas = res.data

        # Incluir despesas recorrentes geradas
        recorrentes = listar_despesas_recorrentes(grupo_id)
        for rec in recorrentes:
            datas = gerar_datas_recorrentes(rec, data_inicio, data_fim)
            for data in datas:
                despesas.append({
                    "id": f"rec_{rec['id']}_{data.strftime('%Y-%m-%d')}",
                    "descricao": rec["descricao"],
                    "valor": rec["valor"],
                    "categoria_id": rec["categoria_id"],
                    "grupo_id": grupo_id,
                    "data": data.strftime("%Y-%m-%d")
                })

        return despesas
    except Exception as e:
        # Log do erro e retorno vazio para evitar crash
        print(f"Erro em listar_despesas: {e}")
        return []

def adicionar_despesa(grupo_id, descricao, valor, categoria_id, data):
    if isinstance(data, str):
        data_str = data
    else:
        data_str = data.strftime("%Y-%m-%d")

    supabase.table("despesas").insert({
        "descricao": descricao,
        "valor": valor,
        "categoria_id": categoria_id,
        "grupo_id": grupo_id,
        "data": data_str
    }).execute()

def listar_despesas_recorrentes(grupo_id):
    try:
        res = supabase.table("despesas_recorrentes").select("*").eq("grupo_id", grupo_id).execute()
        return res.data
    except:
        return []  # Tabela não existe ainda

def adicionar_despesa_recorrente(grupo_id, descricao, valor, categoria_id, dia_do_mes, data_inicio, data_fim):
    supabase.table("despesas_recorrentes").insert({
        "descricao": descricao,
        "valor": valor,
        "categoria_id": categoria_id,
        "grupo_id": grupo_id,
        "dia_do_mes": dia_do_mes,
        "data_inicio": data_inicio.strftime("%Y-%m-%d"),
        "data_fim": data_fim.strftime("%Y-%m-%d")
    }).execute()

def gerar_datas_recorrentes(rec, data_inicio, data_fim):
    datas = []
    inicio = datetime.datetime.strptime(rec["data_inicio"], "%Y-%m-%d").date()
    fim = datetime.datetime.strptime(rec["data_fim"], "%Y-%m-%d").date()
    dia = rec["dia_do_mes"]

    if data_inicio:
        periodo_inicio = data_inicio
    else:
        periodo_inicio = inicio

    if data_fim:
        periodo_fim = data_fim
    else:
        periodo_fim = fim

    ano_atual = periodo_inicio.year
    mes_atual = periodo_inicio.month

    while True:
        try:
            data_candidata = datetime.date(ano_atual, mes_atual, dia)
            if data_candidata >= inicio and data_candidata <= fim and data_candidata >= periodo_inicio and data_candidata <= periodo_fim:
                datas.append(data_candidata)
        except ValueError:
            pass  # Dia inválido para o mês

        mes_atual += 1
        if mes_atual > 12:
            mes_atual = 1
            ano_atual += 1

        if datetime.date(ano_atual, mes_atual, 1) > periodo_fim:
            break

    return datas