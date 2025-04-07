
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

@st.cache_data
def load_weekly_abx():
    df = pd.read_excel("weekly_abx_resistance.xlsx")
    return df

df_abx = load_weekly_abx()

st.title("📆 Résistance hebdomadaire - Autres antibiotiques")

abx_list = sorted(df_abx["Antibiotic"].unique())
selected_abx = st.multiselect("Choisir antibiotiques à afficher", abx_list, default=abx_list[:3])

fig = go.Figure()
for abx in selected_abx:
    data = df_abx[df_abx["Antibiotic"] == abx]
    fig.add_trace(go.Scatter(
        x=data["Week"],
        y=data["% Resistance"],
        mode="lines+markers",
        name=abx,
        hovertemplate="<b>%{text}</b><br>Semaine: %{x}<br>%R: %{y:.1f}%",
        text=[abx] * len(data)
    ))

fig.update_layout(
    title="Évolution hebdomadaire de la résistance (%R)",
    xaxis_title="Semaine",
    yaxis_title="% Résistance",
    hovermode="x unified",
    yaxis=dict(range=[0, 100])
)

st.plotly_chart(fig, use_container_width=True)
