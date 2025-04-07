
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

# Filtrage des données
df_filtered = df[(df["Week"] >= selected_weeks[0]) & (df["Week"] <= selected_weeks[1])]

colors = {
    "MRSA": "orange",
    "VRSA": "red",
    "Wild": "green",
    "others": "blue"
}

# Graphique en nombre de cas
st.subheader("🧪 Nombre de cas par semaine")
fig1, ax1 = plt.subplots(figsize=(14, 6))
for pheno in selected_pheno:
    ax1.plot(df_filtered["Week"], df_filtered[pheno], label=pheno, color=colors[pheno], linewidth=3, marker='o')
ax1.set_xlabel("Semaine")
ax1.set_ylabel("Nombre de cas")
ax1.set_title("Évolution hebdomadaire - Nombre de cas")
ax1.grid(True)
ax1.legend()
st.pyplot(fig1)

# Graphique en pourcentage
st.subheader("📊 Prévalence (%) par semaine")
fig2, ax2 = plt.subplots(figsize=(14, 6))
for pheno in selected_pheno:
    percentage = df_filtered[pheno] / df_filtered["Total"] * 100
    ax2.plot(df_filtered["Week"], percentage, label=pheno, color=colors[pheno], linewidth=3, marker='s', linestyle='--')
ax2.set_xlabel("Semaine")
ax2.set_ylabel("Prévalence (%)")
ax2.set_title("Évolution hebdomadaire - Pourcentage")
ax2.grid(True)
ax2.legend()
st.pyplot(fig2)
