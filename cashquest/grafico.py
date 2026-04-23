import streamlit as st
import plotly.express as px
import pandas as pd

def mostrar_graficos(df, categorias_dict):
    saldo_total = df['valor'].sum()
    st.metric("💰 Saldo Total", f"R$ {saldo_total:,.2f}")

    # Separar despesas e receitas
    df_despesas = df[df['tipo'] == 'Despesa']
    df_receitas = df[df['tipo'] == 'Receita']

    if not df_despesas.empty:
        st.subheader("Despesas por Categoria")
        # Filtrar top 6 categorias por valor absoluto para evitar overflow
        top_categorias = df_despesas.groupby("categoria")["valor"].sum().abs().nlargest(6).index
        num_cols = min(len(top_categorias), 3)  # Máximo 3 colunas para melhor distribuição
        cols = st.columns(num_cols)
        for i, cat in enumerate(top_categorias):
            total_cat = df_despesas[df_despesas["categoria"] == cat]["valor"].sum()
            with cols[i % num_cols]:
                st.metric(f"{cat}", f"R$ {total_cat:,.2f}", help=f"Total para {cat}")

        fig1 = px.pie(df_despesas, names="categoria", values=df_despesas["valor"].abs(), title="Distribuição de Despesas por Categoria - CashQuest")
        st.plotly_chart(fig1, use_container_width=True)

    if not df_receitas.empty:
        st.subheader("Receitas por Categoria")
        # Como receitas não têm categoria, mostrar total de receitas
        total_receitas = df_receitas["valor"].sum()
        st.metric("💰 Total Receitas", f"R$ {total_receitas:,.2f}")

        # Gráfico simples para receitas (se houver variação, mas por enquanto placeholder)
        fig3 = px.bar(df_receitas, x="data", y="valor", title="Receitas ao Longo do Tempo - CashQuest")
        st.plotly_chart(fig3, use_container_width=True)

    df_time = df.groupby("data")["valor"].sum().reset_index()
    fig2 = px.line(df_time, x="data", y="valor", title="Saldo ao Longo do Tempo - CashQuest", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Tabela de Transações - CashQuest")
    # Limitar a 50 linhas para performance
    df_display = df.tail(50) if len(df) > 50 else df
    st.dataframe(df_display[["tipo", "descricao", "valor", "categoria", "data"]], use_container_width=True)