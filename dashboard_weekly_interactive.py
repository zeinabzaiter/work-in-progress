
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

# Filtrage
df_filtered = df[(df["Week"] >= selected_weeks[0]) & (df["Week"] <= selected_weeks[1])]

colors = {
    "MRSA": "orange",
    "VRSA": "red",
    "Wild": "green",
    "others": "blue"
}

# Graphique interactif pour les pourcentages
st.subheader("📊 Prévalence (%) par semaine (Interactif)")

fig = go.Figure()

for pheno in selected_pheno:
    fig.add_trace(go.Scatter(
        x=df_filtered["Week"],
        y=(df_filtered[pheno] / df_filtered["Total"]) * 100,
        mode='lines+markers',
        name=pheno,
        marker=dict(size=8),
        line=dict(width=3),
        hovertemplate=f"<b>{pheno}</b><br>Semaine: %{{x}}<br>Prévalence: %{{y:.1f}}%<extra></extra>",
        line_color=colors[pheno]
    ))

fig.update_layout(
    xaxis_title="Semaine",
    yaxis_title="Prévalence (%)",
    title="Évolution hebdomadaire des phénotypes en %",
    hovermode="x unified",
    height=500
)

st.plotly_chart(fig, use_container_width=True)
