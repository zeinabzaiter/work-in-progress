import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Charger les données brutes des antibiotiques (même fichier utilisé dans l'analyse précédente)
@st.cache_data
def load_atb_data():
    df_atb = pd.read_excel("staph_aureus_autre_atb.xlsx", header=[0, 1])
    df_atb.columns = [f"{col[0]} - {col[1]}" if not pd.isna(col[1]) else col[0] for col in df_atb.columns]
    df_atb.rename(columns={df_atb.columns[0]: "Month"}, inplace=True)
    return df_atb

df_atb_raw = load_atb_data()

# Calcul des seuils d'alerte selon la règle de Tukey pour chaque antibiotique
def calculate_tukey_alerts(df):
    alert_data = {}
    
    # Calculer IQR, Q1, Q3, et les seuils d'alerte
    for antibiotic in df.columns[1:]:
        # Calculer les quartiles
        Q1 = df[antibiotic].quantile(0.25)
        Q3 = df[antibiotic].quantile(0.75)
        IQR = Q3 - Q1
        
        # Calculer les seuils d'alerte
        lower_threshold = Q1 - 1.5 * IQR
        upper_threshold = Q3 + 1.5 * IQR
        
        # Vérifier si des alertes existent pour cet antibiotique
        alert_data[antibiotic] = {
            "lower_threshold": lower_threshold,
            "upper_threshold": upper_threshold,
            "alerts": {
                "below": df[df[antibiotic] < lower_threshold],
                "above": df[df[antibiotic] > upper_threshold]
            }
        }
    
    return alert_data

# Charger les données des antibiotiques
df_atb_raw = load_atb_data()

# Calculer les alertes selon la règle de Tukey
alerts = calculate_tukey_alerts(df_atb_raw)

# Afficher les alertes
for antibiotic, alert_info in alerts.items():
    # Afficher les alertes inférieures
    if not alert_info['alerts']['below'].empty:
        st.warning(f"⚠️ ALERTE : Des valeurs de {antibiotic} sont inférieures au seuil inférieur ({alert_info['lower_threshold']})")

    # Afficher les alertes supérieures
    if not alert_info['alerts']['above'].empty:
        st.error(f"🚨 ALERTE : Des valeurs de {antibiotic} sont supérieures au seuil supérieur ({alert_info['upper_threshold']})")

# Graphique interactif : Tendance de la résistance (%R) par antibiotique
st.markdown("### 📈 Tendance de la résistance (%R)")

# Préparer les données pour l'affichage
df_plot = df_atb_raw.melt(id_vars="Month", var_name="Antibiotic", value_name="% Resistance")

# Filtre de sélection d'antibiotiques
selected_abx = st.multiselect(
    "Choisir les antibiotiques à afficher",
    options=sorted(df_plot["Antibiotic"].unique()),
    default=sorted(df_plot["Antibiotic"].unique())[:3]
)

# Création du graphe Plotly
fig_abx = go.Figure()
for abx in selected_abx:
    abx_data = df_plot[df_plot["Antibiotic"] == abx]
    fig_abx.add_trace(go.Scatter(
        x=abx_data["Month"],
        y=abx_data["% Resistance"],
        mode="lines+markers",
        name=abx,
        marker=dict(size=8),
        line=dict(width=3),
        hovertemplate=f"<b>{abx}</b><br>Mois: %{{x}}<br>%R: %{{y:.1f}}%<extra></extra>"
    ))

fig_abx.update_layout(
    title="Évolution mensuelle de la résistance (%R)",
    xaxis_title="Mois",
    yaxis_title="% Résistance",
    hovermode="x unified",
    height=500
)

st.plotly_chart(fig_abx, use_container_width=True)

# Graphique interactif : Nombre de cas par semaine
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

# Graphique interactif : Prévalence par semaine
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

# Onglet : Autres antibiotiques
st.subheader("🧬 Autres antibiotiques")

# Charger les données brutes (même fichier utilisé dans l'analyse précédente)
@st.cache_data
def load_atb_data():
    df_atb = pd.read_excel("staph_aureus_autre_atb.xlsx", header=[0, 1])
    df_atb.columns = [f"{col[0]} - {col[1]}" if not pd.isna(col[1]) else col[0] for col in df_atb.columns]
    df_atb.rename(columns={df_atb.columns[0]: "Month"}, inplace=True)
    return df_atb

df_atb_raw = load_atb_data()

st.markdown("### 📋 Tableau brut des antibiotiques")
st.dataframe(df_atb_raw, use_container_width=True)

# Version reformattée avec %R uniquement
df_percent_r = df_atb_raw[["Month"] + [col for col in df_atb_raw.columns if "% R" in col]]
df_long = pd.melt(df_percent_r, id_vars="Month", var_name="Antibiotic", value_name="% Resistance")
df_long["Antibiotic"] = df_long["Antibiotic"].str.extract(r'([A-Za-zé]+)', expand=False)

st.markdown("### 📊 Résistance (%R) par antibiotique")
st.dataframe(df_long.dropna(), use_container_width=True)

# 📈 Graphique interactif : évolution de %R par antibiotique
st.markdown("### 📈 Tendance de la résistance (%R)")

# Nettoyage pour le graphe
df_plot = df_long.dropna()
df_plot["Month"] = df_plot["Month"].str.capitalize()

# Filtre de sélection d'antibiotiques
selected_abx = st.multiselect(
    "Choisir les antibiotiques à afficher",
    options=sorted(df_plot["Antibiotic"].unique()),
    default=sorted(df_plot["Antibiotic"].unique())[:3]
)

# Création du graphe Plotly
fig_abx = go.Figure()
for abx in selected_abx:
    abx_data = df_plot[df_plot["Antibiotic"] == abx]
    fig_abx.add_trace(go.Scatter(
        x=abx_data["Month"],
        y=abx_data["% Resistance"],
        mode="lines+markers",
        name=abx,
        marker=dict(size=8),
        line=dict(width=3),
        hovertemplate=f"<b>{abx}</b><br>Mois: %{{x}}<br>%R: %{{y:.1f}}%<extra></extra>"
    ))

fig_abx.update_layout(
    title="Évolution mensuelle de la résistance (%R)",
    xaxis_title="Mois",
    yaxis_title="% Résistance",
    hovermode="x unified",
    height=500
)

st.plotly_chart(fig_abx, use_container_width=True)
