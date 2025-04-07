
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Dashboard Hebdomadaire - Phénotypes")

@st.cache_data
def load_data():
    df = pd.read_excel("staph_aureus_phenotypes.xlsx", sheet_name="Sheet1")
    valid_months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    df = df[df["Month"].isin(valid_months)].copy()
    df["Date"] = pd.to_datetime(df["Month"] + " 2024", format="%B %Y")
    df["Week"] = df["Date"].dt.isocalendar().week
    return df

df = load_data()

st.title("📈 Dashboard Hebdomadaire - Phénotypes de Staphylococcus aureus")

# Sidebar filters
with st.sidebar:
    st.header("Filtres")
    selected_weeks = st.slider(
        "Sélectionnez les semaines",
        int(df["Week"].min()),
        int(df["Week"].max()),
        (int(df["Week"].min()), int(df["Week"].max()))
    )
    selected_pheno = st.multiselect(
        "Phénotypes à afficher",
        ["MRSA", "VRSA", "Wild", "others"],
        default=["MRSA", "VRSA", "Wild", "others"]
    )

df_filtered = df[(df["Week"] >= selected_weeks[0]) & (df["Week"] <= selected_weeks[1])]

colors = {
    "MRSA": "orange",
    "VRSA": "red",
    "Wild": "green",
    "others": "blue"
}

# Graphique interactif : Nombre de cas
st.subheader("🧪 Nombre de cas par semaine (Interactif)")

fig1 = go.Figure()
for pheno in selected_pheno:
    fig1.add_trace(go.Scatter(
        x=df_filtered["Week"],
        y=df_filtered[pheno],
        mode='lines+markers',
        name=pheno,
        marker=dict(size=8),
        line=dict(width=3),
        hovertemplate=f"<b>{pheno}</b><br>Semaine: %{{x}}<br>Cas: %{{y}}<extra></extra>",
        line_color=colors[pheno]
    ))

fig1.update_layout(
    xaxis_title="Semaine",
    yaxis_title="Nombre de cas",
    title="Évolution hebdomadaire du nombre de cas par phénotype",
    hovermode="x unified",
    height=500
)
st.plotly_chart(fig1, use_container_width=True)

# Graphique interactif : Pourcentage
st.subheader("📊 Prévalence (%) par semaine (Interactif)")

fig2 = go.Figure()
for pheno in selected_pheno:
    fig2.add_trace(go.Scatter(
        x=df_filtered["Week"],
        y=(df_filtered[pheno] / df_filtered["Total"]) * 100,
        mode='lines+markers',
        name=pheno,
        marker=dict(size=8),
        line=dict(width=3),
        hovertemplate=f"<b>{pheno}</b><br>Semaine: %{{x}}<br>Prévalence: %{{y:.1f}}%<extra></extra>",
        line_color=colors[pheno]
    ))

fig2.update_layout(
    xaxis_title="Semaine",
    yaxis_title="Prévalence (%)",
    title="Évolution hebdomadaire des phénotypes en %",
    hovermode="x unified",
    height=500
)
st.plotly_chart(fig2, use_container_width=True)


# 🚨 ALERTES

st.subheader("🚨 Alertes de surveillance")

import numpy as np

mean_mrsa = df["MRSA"].mean()
std_mrsa = df["MRSA"].std()
mrsa_threshold = mean_mrsa + 2 * std_mrsa
vrsa_cases_detected = df_filtered["VRSA"].sum()

if df_filtered["MRSA"].max() > mrsa_threshold:
    st.warning(f"⚠️ ALERTE : Le nombre de cas MRSA dépasse la moyenne + 2 écarts-types ({mrsa_threshold:.1f})")

if vrsa_cases_detected > 0:
    st.error(f"🚨 ALERTE : {vrsa_cases_detected} cas de VRSA détectés dans la période sélectionnée")
