import streamlit as st
import plotly.express as px
import pandas as pd

def mostrar_graficos(df, categorias_dict):
    st.metric("💸 Total de Despesas", f"R$ {df['valor'].sum():,.2f}")

    st.subheader("Despesas por Categoria")
    col_cards = st.columns(len(categorias_dict))
    for i, (nome, cat_id) in enumerate(categorias_dict.items()):
        total_cat = df[df["categoria_id"] == cat_id]["valor"].sum()
        col_cards[i].metric(f"{nome}", f"R$ {total_cat:,.2f}")

    fig1 = px.pie(df, names="categoria", values="valor", title="Distribuição por Categoria")
    st.plotly_chart(fig1, use_container_width=True)

    df_time = df.groupby("data")["valor"].sum().reset_index()
    fig2 = px.line(df_time, x="data", y="valor", title="Despesas ao Longo do Tempo", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Tabela de Despesas")
    st.dataframe(df[["descricao", "valor", "categoria", "data"]])