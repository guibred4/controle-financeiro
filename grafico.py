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
        col_cards = st.columns(len(categorias_dict))
        for i, (cat_id, nome) in enumerate(categorias_dict.items()):
            total_cat = df_despesas[df_despesas["categoria_id"] == cat_id]["valor"].sum()
            if total_cat != 0:
                col_cards[i].metric(f"{nome}", f"R$ {total_cat:,.2f}")

        fig1 = px.pie(df_despesas, names="categoria", values="valor", title="Distribuição de Despesas por Categoria")
        st.plotly_chart(fig1, use_container_width=True)

    if not df_receitas.empty:
        st.subheader("Receitas por Categoria")
        fig3 = px.pie(df_receitas, names="categoria", values="valor", title="Distribuição de Receitas por Categoria")
        st.plotly_chart(fig3, use_container_width=True)

    df_time = df.groupby("data")["valor"].sum().reset_index()
    fig2 = px.line(df_time, x="data", y="valor", title="Saldo ao Longo do Tempo", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Tabela de Transações")
    st.dataframe(df[["tipo", "descricao", "valor", "categoria", "data"]])