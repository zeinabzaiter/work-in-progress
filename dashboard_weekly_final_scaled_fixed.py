
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

@st.cache_data
def load_atb_data():
    df = pd.read_excel("staph_aureus_autre_atb.xlsx", header=[0, 1])
    mois = df[('Unnamed: 0_level_0', 'Unnamed: 0_level_1')].rename("Month")
    percent_r_cols = df.columns[4::5]
    df_percent_r = df[percent_r_cols].copy()
    df_percent_r.columns = [col[1].strip() for col in percent_r_cols]
    df_percent_r.insert(0, "Month", mois)
    df_long = pd.melt(df_percent_r, id_vars="Month", var_name="Antibiotic", value_name="% Resistance")
    return df, df_long

df = load_data()
df_atb_raw, df_atb = load_atb_data()

st.title("📈 Dashboard Hebdomadaire - Staphylococcus aureus")

with st.sidebar:
    st.header("Filtres")
    selected_weeks = st.slider(
        "Semaine",
        int(df["Week"].min()),
        int(df["Week"].max()),
        (int(df["Week"].min()), int(df["Week"].max()))
    )
    selected_pheno = st.multiselect(
        "Phénotypes",
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

# Graphique Nombre de cas
st.subheader("🧪 Nombre de cas par semaine")
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
fig1.update_layout(xaxis_title="Semaine", yaxis_title="Nombre de cas", hovermode="x unified")
st.plotly_chart(fig1, use_container_width=True)

# Graphique %R
st.subheader("📊 Prévalence (%) par semaine")
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
fig2.update_layout(xaxis_title="Semaine", yaxis_title="Prévalence (%)", hovermode="x unified", yaxis=dict(range=[0, 100]))
st.plotly_chart(fig2, use_container_width=True)

# Alertes
st.subheader("🚨 Alertes")
import numpy as np
mean_mrsa = df["MRSA"].mean()
std_mrsa = df["MRSA"].std()
threshold = mean_mrsa + 2 * std_mrsa
if df_filtered["MRSA"].max() > threshold:
    st.warning(f"⚠️ ALERTE : Cas MRSA > Moyenne + 2SD ({threshold:.1f})")
if df_filtered["VRSA"].sum() > 0:
    st.error(f"🚨 ALERTE : {df_filtered['VRSA'].sum()} cas VRSA détectés")

# Antibiotiques
st.header("🧬 Autres antibiotiques")

st.markdown("### 📋 Données brutes")
st.dataframe(df_atb_raw)

st.markdown("### 📊 Taux de résistance (%R)")
st.dataframe(df_atb)

st.markdown("### 📈 Tendance de la résistance (%R)")
abx_list = sorted(df_atb["Antibiotic"].unique())
selected_abx = st.multiselect("Choisir antibiotiques", abx_list, default=abx_list[:3])

fig_abx = go.Figure()
for abx in selected_abx:
    abx_data = df_atb[df_atb["Antibiotic"] == abx]
    fig_abx.add_trace(go.Scatter(
        x=abx_data["Month"],
        y=abx_data["% Resistance"],
        mode="lines+markers",
        name=abx,
        hovertemplate=f"<b>{abx}</b><br>Mois: %{{x}}<br>%R: %{{y:.1f}}%<extra></extra>"
    ))
fig_abx.update_layout(xaxis_title="Mois", yaxis_title="% Résistance", hovermode="x unified", yaxis=dict(range=[0, 100]))
st.plotly_chart(fig_abx, use_container_width=True)
