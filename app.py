# app.py - Controle Financeiro (versão ajustada) 232332
import streamlit as st
import pandas as pd
from supabase_client import get_supabase
from despesas import listar_despesas, adicionar_despesa
from categorias import listar_categorias
from grafico import mostrar_graficos
from utils import hoje_inicio_mes
import datetime

# ================================
# Configurações da página
# ================================
supabase = get_supabase()
st.set_page_config(page_title="Controle Financeiro", page_icon="💰", layout="wide")

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
    st.title("💰 Controle Financeiro")
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
pagina = st.sidebar.radio("Menu", ["Adicionar Despesa", "Resumo / Gráficos"])
data_inicio, data_fim = st.sidebar.date_input("Período", hoje_inicio_mes())

# ================================
# ADICIONAR DESPESA
# ================================
if pagina == "Adicionar Despesa":
    st.subheader("Adicionar Despesa")
    categorias = listar_categorias(grupo_id)
    cat_options = {c["nome"]: c["id"] for c in categorias}

    with st.form("nova_despesa"):
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor", min_value=0.0, step=0.01)
        categoria = st.selectbox("Categoria", options=list(cat_options.keys()))
        data = st.date_input("Data", value=datetime.date.today())
        submitted = st.form_submit_button("Adicionar")
        if submitted:
            adicionar_despesa(grupo_id, descricao, valor, cat_options[categoria], str(data))  # converte date para string
            st.success("Despesa adicionada!")

# ================================
# RESUMO / GRÁFICOS
# ================================
elif pagina == "Resumo / Gráficos":
    st.subheader("Resumo de Despesas")
    despesas = listar_despesas(grupo_id, data_inicio, data_fim)

    if despesas:
        df = pd.DataFrame(despesas)
        categorias_dict = {c["id"]: c["nome"] for c in listar_categorias(grupo_id)}
        df["categoria"] = df["categoria_id"].map(categorias_dict)
        df["valor"] = pd.to_numeric(df["valor"])

        mostrar_graficos(df, categorias_dict)
    else:
        st.info("Nenhuma despesa cadastrada neste período.")
