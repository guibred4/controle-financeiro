# CashQuest - Controle Financeiro Inteligente
import streamlit as st
import pandas as pd
from cashquest.supabase_client import get_supabase
from cashquest.despesas import listar_despesas, adicionar_despesa, adicionar_despesa_recorrente
from cashquest.receitas import listar_receitas, adicionar_receita
from cashquest.categorias import listar_categorias
from cashquest.grafico import mostrar_graficos
from cashquest.utils import hoje_inicio_mes
import datetime

st.set_page_config(page_title="CashQuest - Controle Financeiro", page_icon="💰", layout="wide")

@st.cache_data(ttl=300, show_spinner=False)
def get_cached_categorias(grupo_id):
    return listar_categorias(grupo_id)


def inject_styles():
    st.markdown(
        """
        <style>
        body {
            background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
        }
        .cashquest-brand {
            font-size: 48px;
            font-weight: 900;
            color: #0f172a;
            margin: 0;
        }
        .cashquest-tagline {
            font-size: 17px;
            color: #475569;
            margin-top: 8px;
            margin-bottom: 0;
            max-width: 660px;
        }
        .cashquest-hero {
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
            border-radius: 32px;
            padding: 36px;
            box-shadow: 0 30px 90px rgba(15, 23, 42, 0.20);
            margin-bottom: 32px;
            color: #ffffff;
        }
        .cashquest-hero p {
            margin: 0;
            color: #dbeafe;
            font-size: 16px;
            line-height: 1.8;
        }
        .cashquest-card {
            background: #ffffff;
            border: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 28px;
            box-shadow: 0 22px 70px rgba(15, 23, 42, 0.12);
            padding: 30px;
            margin-bottom: 28px;
        }
        .cashquest-card h2 {
            margin-top: 0;
            color: #0f172a;
        }
        .cashquest-card p {
            color: #475569;
        }
        .cashquest-info-box {
            background: rgba(59, 130, 246, 0.08);
            border-left: 4px solid #2563eb;
            padding: 18px 22px;
            border-radius: 18px;
            margin-bottom: 20px;
            color: #0f172a;
        }
        .metric-card {
            background: linear-gradient(135deg, rgba(11, 61, 145, 0.08) 0%, rgba(37, 99, 235, 0.04) 100%);
            border: 1px solid rgba(59, 130, 246, 0.18);
            border-radius: 22px;
            padding: 28px 24px;
            text-align: center;
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.06);
        }
        .metric-card .metric-value {
            font-size: 36px;
            font-weight: 900;
            color: #0b3d91;
            margin: 12px 0;
        }
        .metric-card .metric-label {
            font-size: 15px;
            color: #475569;
            font-weight: 600;
        }
        .metric-card.positive {
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.08) 0%, rgba(74, 222, 128, 0.04) 100%);
            border-color: rgba(74, 222, 128, 0.24);
        }
        .metric-card.positive .metric-value {
            color: #22c55e;
        }
        .metric-card.negative {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(248, 113, 113, 0.04) 100%);
            border-color: rgba(248, 113, 113, 0.24);
        }
        .metric-card.negative .metric-value {
            color: #ef4444;
        }
        .cashquest-card .stButton>button {
            background: linear-gradient(135deg, #0b3d91, #2563eb) !important;
            color: #ffffff !important;
            border-radius: 16px !important;
            padding: 1rem 1.5rem !important;
            font-weight: 700 !important;
        }
        .cashquest-card .stButton>button:hover {
            filter: brightness(1.08) !important;
        }
        .cashquest-card .stTextInput>div>div>input,
        .cashquest-card .stTextInput>div>div>textarea,
        .cashquest-card .stDateInput>div>div>div>div,
        .cashquest-card .stSelectbox>div>div>select {
            border-radius: 14px !important;
            background: #f8fafc !important;
            border: 1px solid #cbd5e1 !important;
        }
        .cashquest-card .stTextInput>label,
        .cashquest-card .stDateInput>label {
            color: #0f172a !important;
            font-weight: 700 !important;
        }
        .onboarding-box {
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
            border-radius: 24px;
            padding: 32px;
            color: #ffffff;
            margin-bottom: 28px;
            box-shadow: 0 28px 80px rgba(15, 23, 42, 0.18);
        }
        .onboarding-box h3 {
            margin-top: 0;
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 12px;
        }
        .onboarding-box p {
            margin: 0;
            font-size: 16px;
            color: #dbeafe;
            line-height: 1.7;
        }
        @media(max-width: 768px) {
            .cashquest-hero,
            .cashquest-card,
            .onboarding-box {
                padding: 24px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_brand_header():
    col1, col2 = st.columns([1, 3])
    with col1:
        try:
            st.image("logo.png", width=160)
        except Exception:
            st.markdown("<div style='font-size:72px; line-height: 0.85;'>💰</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='cashquest-brand'>CashQuest</div>", unsafe_allow_html=True)
        st.markdown("<div class='cashquest-tagline'>Controle financeiro pessoal com design profissional, usabilidade clara e foco em resultados.</div>", unsafe_allow_html=True)


def render_metric_card(label, value, tipo="neutro"):
    """Renderiza um card de métrica com estilo visual."""
    class_name = "metric-card " + ("positive" if tipo == "positivo" else "negative" if tipo == "negativo" else "")
    st.markdown(f"""
        <div class="{class_name}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)


def show_onboarding_dashboard(nome_usuario):
    """Exibe um dashboard de onboarding para novos usuários."""
    st.markdown("""
        <div class="onboarding-box">
            <h3>👋 Bem-vindo ao CashQuest!</h3>
            <p>Que bom ter você conosco! Este é seu espaço para controlar suas finanças de forma simples e inteligente.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="metric-card">
                <div style="font-size: 32px; margin-bottom: 8px;">📊</div>
                <div class="metric-label" style="color: #0f172a; font-weight: 700;">Passo 1</div>
                <div style="font-size: 14px; color: #64748b; margin-top: 8px;">Adicione suas despesas e receitas</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <div style="font-size: 32px; margin-bottom: 8px;">📈</div>
                <div class="metric-label" style="color: #0f172a; font-weight: 700;">Passo 2</div>
                <div style="font-size: 14px; color: #64748b; margin-top: 8px;">Visualize seus gráficos e relatórios</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card">
                <div style="font-size: 32px; margin-bottom: 8px;">💡</div>
                <div class="metric-label" style="color: #0f172a; font-weight: 700;">Passo 3</div>
                <div style="font-size: 14px; color: #64748b; margin-top: 8px;">Tome decisões financeiras melhores</div>
            </div>
        """, unsafe_allow_html=True)


def render_summary_dashboard(total_receitas, total_despesas, saldo, despesas, receitas):
    """Renderiza o painel de resumo com cards visuais."""
    st.markdown("<h2 style='color: #0f172a; margin-bottom: 24px;'>📊 Seu Resumo Financeiro</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("Total de Receitas", f"R$ {total_receitas:,.2f}", "positivo")
    with col2:
        render_metric_card("Total de Despesas", f"R$ {total_despesas:,.2f}", "negativo")
    with col3:
        tipo_saldo = "positivo" if saldo >= 0 else "negativo"
        render_metric_card("Saldo", f"R$ {saldo:,.2f}", tipo_saldo)
    
    st.markdown("---")
    st.markdown("<h3 style='color: #0f172a; margin-top: 24px; margin-bottom: 18px;'>📉 Análise Detalhada</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if despesas:
            despesas_por_cat = {}
            for d in despesas:
                cat = d.get('nome', 'Sem categoria')
                val = float(d.get('valor', 0))
                despesas_por_cat[cat] = despesas_por_cat.get(cat, 0) + val
            
            st.markdown("<div class='cashquest-card' style='background: rgba(239, 68, 68, 0.02);'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #0f172a;'>💸 Top Despesas por Categoria</h4>", unsafe_allow_html=True)
            sorted_despesas = sorted(despesas_por_cat.items(), key=lambda x: x[1], reverse=True)[:5]
            for cat, val in sorted_despesas:
                st.write(f"**{cat}**: R$ {val:,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        if receitas:
            st.markdown("<div class='cashquest-card' style='background: rgba(34, 197, 94, 0.02);'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #0f172a;'>💰 Resumo de Receitas</h4>", unsafe_allow_html=True)
            st.write(f"**Total de entradas**: {len(receitas)}")
            st.write(f"**Média por receita**: R$ {total_receitas / len(receitas):,.2f}" if len(receitas) > 0 else "Sem receitas")
            st.markdown("</div>", unsafe_allow_html=True)


def send_password_reset(email):
    try:
        supabase.auth.reset_password_email(email)
        return True, "Enviamos um link de redefinição de senha para o seu email. Verifique sua caixa de entrada e spam."
    except Exception as error:
        return False, f"Não foi possível enviar o email de recuperação: {error}"


def build_auth_page():
    st.markdown("<div class='cashquest-hero'>", unsafe_allow_html=True)
    show_brand_header()
    st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='cashquest-card'>", unsafe_allow_html=True)
        st.markdown("<h2>Bem-vindo ao CashQuest</h2>", unsafe_allow_html=True)
        st.markdown("<p>Entre ou crie sua conta com segurança. Caso precise, recupere sua senha em poucos cliques.</p>", unsafe_allow_html=True)

        tab_login, tab_signup, tab_recover = st.tabs(["Entrar", "Criar conta", "Recuperar senha"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="seu@exemplo.com")
                senha = st.text_input("Senha", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Entrar")
                if submitted:
                    if not email.strip() or not senha.strip():
                        st.error("Por favor, preencha email e senha.")
                    else:
                        try:
                            resposta = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                            st.session_state.user = resposta.user
                            st.session_state.logged_in = True
                            st.experimental_rerun()
                        except Exception as e:
                            st.error("Falha no login. Verifique suas credenciais.")
                            st.write(e)

        with tab_signup:
            with st.form("signup_form"):
                email = st.text_input("Email", key="signup_email", placeholder="seu@exemplo.com")
                senha = st.text_input("Senha", type="password", key="signup_password", placeholder="••••••••")
                confirmacao = st.text_input("Confirme a senha", type="password", key="signup_confirm", placeholder="••••••••")
                submitted = st.form_submit_button("Criar conta")
                if submitted:
                    if not email.strip() or not senha.strip() or not confirmacao.strip():
                        st.error("Preencha todos os campos para criar sua conta.")
                    elif senha != confirmacao:
                        st.error("As senhas não coincidem.")
                    else:
                        try:
                            supabase.auth.sign_up({"email": email, "password": senha})
                            st.success("Conta criada com sucesso! Verifique seu email para confirmar.")
                        except Exception as e:
                            st.error("Não foi possível criar a conta.")
                            st.write(e)

        with tab_recover:
            st.markdown("<div class='cashquest-info-box'>Insira o email cadastrado para receber um link de redefinição de senha.</div>", unsafe_allow_html=True)
            with st.form("recover_form"):
                email = st.text_input("Email de recuperação", key="recover_email", placeholder="seu@exemplo.com")
                submitted = st.form_submit_button("Enviar link de recuperação")
                if submitted:
                    if not email.strip():
                        st.error("Digite um email válido para recuperação.")
                    else:
                        success, message = send_password_reset(email.strip())
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# ================================
# Configurações da página

supabase = get_supabase()
inject_styles()

if "user" not in st.session_state:
    st.session_state.user = None
if "grupo_id" not in st.session_state:
    st.session_state.grupo_id = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    build_auth_page()

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

# Branding principal
st.markdown("<div class='cashquest-hero'>", unsafe_allow_html=True)
show_brand_header()
st.markdown("</div>", unsafe_allow_html=True)

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

        if not despesas and not receitas:
            st.info("Nenhuma transação cadastrada neste período.")
            show_onboarding_dashboard(st.session_state.user.email.split("@")[0])
        else:
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

                # Renderizar dashboard visual
                render_summary_dashboard(total_receitas, total_despesas, saldo, despesas, receitas)
                
                # Gráficos
                st.markdown("---")
                st.markdown("<h3 style='color: #0f172a; margin-top: 24px;'>📈 Gráficos e Análises</h3>", unsafe_allow_html=True)
                mostrar_graficos(df, categorias_dict)
            else:
                st.info("Nenhuma transação cadastrada neste período.")
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}. Verifique as tabelas no Supabase.")
