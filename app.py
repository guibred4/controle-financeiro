# CashQuest - Controle Financeiro Inteligente
import streamlit as st
import pandas as pd
from supabase_client import get_supabase
from despesas import listar_despesas, adicionar_despesa, adicionar_despesa_recorrente
from receitas import listar_receitas, adicionar_receita
from categorias import listar_categorias
from grafico import mostrar_graficos
from utils import hoje_inicio_mes
import datetime

# Cache para categorias (dados estáticos) - Temporariamente removido para debug
# @st.cache_data(ttl=300)
def get_cached_categorias(grupo_id):
    return listar_categorias(grupo_id)

# ================================
# Configurações da página
# ================================
supabase = get_supabase()
st.set_page_config(page_title="CashQuest - Controle Financeiro", page_icon="💰", layout="wide")

# ================================
# Inicialização da sessão
# ================================
if "user" not in st.session_state:
    st.session_state.user = None
if "grupo_id" not in st.session_state:
    st.session_state.grupo_id = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ================================
# LOGIN / CADASTRO
# ================================
if not st.session_state.logged_in:
    st.title("💰 CashQuest - Controle Financeiro Inteligente")
    st.subheader("Gerencie suas finanças com facilidade e insights visuais.")
    st.subheader("Login / Cadastro")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    col1, col2 = st.columns(2)

    if col1.button("Login"):
        try:
            resposta = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            st.session_state.user = resposta.user
            st.session_state.logged_in = True
        except Exception as e:
            st.error("Login inválido")
            st.write(e)

    if col2.button("Criar conta"):
        try:
            supabase.auth.sign_up({"email": email, "password": senha})
            st.success("Conta criada! Faça login.")
        except Exception as e:
            st.error("Erro ao criar conta")
            st.write(e)

    st.stop()  # impede o resto do app até que o usuário logue

# ================================
# SIDEBAR
# ================================
st.sidebar.success(f"Logado como: {st.session_state.user.email}")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.session_state.logged_in = False
    st.stop()  # força voltar para tela de login

# ================================
# FUNÇÃO PARA BUSCAR OU CRIAR GRUPO
# ================================
def buscar_grupo_usuario():
    user_id = st.session_state.user.id

    res = supabase.table("membros_grupo").select("grupo_id").eq("user_id", user_id).execute()
    if res.data and len(res.data) > 0:
        return res.data[0]["grupo_id"]

    # Cria grupo principal
    grupo = supabase.table("grupos").insert({
        "nome": "Grupo Principal",
        "user_id": user_id
    }).execute()
    grupo_id = grupo.data[0]["id"]

    # Associa usuário ao grupo
    supabase.table("membros_grupo").insert({
        "user_id": user_id,
        "grupo_id": grupo_id
    }).execute()

    # Cria categorias padrão
    categorias_padrao = ["Alimentação", "Transporte", "Lazer", "Saúde",
                         "Moradia", "Educação", "Roupas", "Outros"]
    for cat in categorias_padrao:
        supabase.table("categorias").insert({
            "nome": cat,
            "grupo_id": grupo_id
        }).execute()

    return grupo_id

if st.session_state.grupo_id is None:
    st.session_state.grupo_id = buscar_grupo_usuario()
grupo_id = st.session_state.grupo_id

# ================================
# MENU LATERAL
# ================================
pagina = st.sidebar.radio("Menu", ["Adicionar Despesa", "Adicionar Receita", "Resumo / Gráficos"])
data_inicio, data_fim = st.sidebar.date_input("Período", hoje_inicio_mes())
st.sidebar.markdown("---")
st.sidebar.info("💡 **Dicas do CashQuest**: Adicione despesas recorrentes para automatizar entradas mensais. Monitore seu saldo para evitar surpresas!")

# ================================
# ADICIONAR DESPESA
# ================================
if pagina == "Adicionar Despesa":
    st.subheader("Adicionar Despesa - CashQuest")
    categorias = get_cached_categorias(grupo_id)
    cat_options = {c["nome"]: c["id"] for c in categorias}

    with st.form("nova_despesa"):
        descricao = st.text_input("Descrição", max_chars=100, help="Descrição da despesa (máx. 100 caracteres)")
        valor = st.number_input("Valor", min_value=0.01, step=0.01, help="Valor em reais")
        categoria = st.selectbox("Categoria", options=list(cat_options.keys()))
        recorrente = st.checkbox("Despesa Recorrente (Mensal)", help="Marque para despesas que se repetem mensalmente")
        
        if recorrente:
            dia_do_mes = st.number_input("Dia do Mês", min_value=1, max_value=31, value=5, help="Dia do mês para recorrência")
            data_inicio = st.date_input("Data de Início", value=datetime.date.today().replace(day=1), help="Quando começa a recorrência")
            data_fim = st.date_input("Data de Fim", value=datetime.date(2027, 1, 5), help="Quando termina a recorrência")
        else:
            data = st.date_input("Data", value=datetime.date.today(), help="Data da despesa")
        
        submitted = st.form_submit_button("Adicionar")
        if submitted:
            if valor <= 0:
                st.error("Valor deve ser maior que zero.")
            elif not descricao.strip():
                st.error("Descrição não pode estar vazia.")
            else:
                if recorrente:
                    adicionar_despesa_recorrente(grupo_id, descricao.strip(), valor, cat_options[categoria], dia_do_mes, data_inicio, data_fim)
                    st.success("Despesa recorrente adicionada!")
                else:
                    adicionar_despesa(grupo_id, descricao.strip(), valor, cat_options[categoria], data)
                    st.success("Despesa adicionada!")

# ================================
# ADICIONAR RECEITA
# ================================
elif pagina == "Adicionar Receita":
    st.subheader("Adicionar Receita - CashQuest")

    with st.form("nova_receita"):
        descricao = st.text_input("Descrição", max_chars=100, help="Descrição da receita (máx. 100 caracteres)")
        valor = st.number_input("Valor", min_value=0.01, step=0.01, help="Valor em reais")
        data = st.date_input("Data", value=datetime.date.today(), help="Data da receita")
        submitted = st.form_submit_button("Adicionar")
        if submitted:
            if valor <= 0:
                st.error("Valor deve ser maior que zero.")
            elif not descricao.strip():
                st.error("Descrição não pode estar vazia.")
            else:
                adicionar_receita(grupo_id, descricao.strip(), valor, data)
                st.success("Receita adicionada!")
elif pagina == "Resumo / Gráficos":
    st.subheader("Resumo Financeiro - CashQuest")
    try:
        despesas = listar_despesas(grupo_id, data_inicio, data_fim)
        receitas = listar_receitas(grupo_id, data_inicio, data_fim)

        if despesas or receitas:
            # Preparar DataFrame para despesas
            df_despesas = pd.DataFrame(despesas) if despesas else pd.DataFrame()
            if not df_despesas.empty:
                df_despesas["tipo"] = "Despesa"
                df_despesas["valor"] = -pd.to_numeric(df_despesas["valor"])  # Negativo para despesas

            # Preparar DataFrame para receitas
            df_receitas = pd.DataFrame(receitas) if receitas else pd.DataFrame()
            if not df_receitas.empty:
                df_receitas["tipo"] = "Receita"
                df_receitas["valor"] = pd.to_numeric(df_receitas["valor"])
                df_receitas["categoria"] = "Receita"  # Placeholder, pois receitas não têm categoria

            # Combinar
            df = pd.concat([df_despesas, df_receitas], ignore_index=True)
            if not df.empty:
                categorias_dict = {c["id"]: c["nome"] for c in get_cached_categorias(grupo_id)}
                df["categoria"] = df.apply(lambda row: categorias_dict.get(row["categoria_id"], "Receita") if pd.notna(row.get("categoria_id")) else "Receita", axis=1)

                # Calcular totais
                total_receitas = df_receitas["valor"].sum() if not df_receitas.empty else 0
                total_despesas = -df_despesas["valor"].sum() if not df_despesas.empty else 0  # Já negativo
                saldo = total_receitas - total_despesas

                # Métricas principais
                col1, col2, col3 = st.columns(3)
                col1.metric("💰 Total Receitas", f"R$ {total_receitas:,.2f}")
                col2.metric("💸 Total Despesas", f"R$ {total_despesas:,.2f}")
                if saldo >= 0:
                    col3.metric("📈 Saldo", f"R$ {saldo:,.2f}", delta=f"+R$ {saldo:,.2f}")
                else:
                    col3.metric("📉 Saldo", f"R$ {saldo:,.2f}", delta=f"R$ {saldo:,.2f}")

                # Gráficos
                mostrar_graficos(df, categorias_dict)
            else:
                st.info("Nenhuma transação cadastrada neste período.")
        else:
            st.info("Nenhuma transação cadastrada neste período.")
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}. Verifique as tabelas no Supabase.")
