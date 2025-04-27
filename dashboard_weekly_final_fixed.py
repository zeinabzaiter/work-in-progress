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

# Nettoyer les données en supprimant les lignes avec des NaN dans les colonnes d'intérêt
df_atb_raw_clean = df_atb_raw.dropna(subset=[col for col in df_atb_raw.columns if "% R" in col])

# Calcul des seuils d'alerte selon la règle de Tukey pour chaque antibiotique
def calculate_tukey_alerts(df):
    alert_data = {}
    
    # Calculer IQR, Q1, Q3, et les seuils d'alerte
    for antibiotic in df.columns[1:]:
        # Vérifier si la colonne contient des NaN ou des valeurs non numériques
        if df[antibiotic].dtype not in ['float64', 'int64']:
            continue  # Ignore les colonnes non numériques
        
        if df[antibiotic].isnull().sum() > 0:
            df[antibiotic] = df[antibiotic].fillna(df[antibiotic].mean())  # Remplacer NaN par la moyenne de la colonne
        
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

# Calculer les alertes selon la règle de Tukey
alerts = calculate_tukey_alerts(df_atb_raw_clean)

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
df_plot = df_atb_raw_clean.melt(id_vars="Month", var_name="Antibiotic", value_name="% Resistance")

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
