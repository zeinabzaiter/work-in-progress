
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Dashboard Hebdomadaire - Staphylococcus aureus")

# Charger les fichiers
@st.cache_data
def load_data():
    df1 = pd.read_excel("staph_aureus_phenotypes.xlsx", sheet_name="Sheet1")
    df2 = pd.read_excel("staphylococcus_2024_new.xlsx", sheet_name="Sheet1")
    return df1, df2

df_phenotypes, df_prelevements = load_data()

# Nettoyage des dates
df_prelevements["DATE_PRELEVEMENT"] = pd.to_datetime(df_prelevements["DATE_PRELEVEMENT"], errors='coerce')
df_prelevements = df_prelevements.dropna(subset=["DATE_PRELEVEMENT"])

# Ajouter la semaine ISO
df_prelevements["Semaine"] = df_prelevements["DATE_PRELEVEMENT"].dt.isocalendar().week
df_prelevements["Année"] = df_prelevements["DATE_PRELEVEMENT"].dt.isocalendar().year

# Regrouper par semaine pour le nombre total de cas
weekly_counts = df_prelevements.groupby(["Année", "Semaine"]).size().reset_index(name="Total")

# Préparer les données de phénotypes
df_phenotypes_filtered = df_phenotypes.copy()
df_phenotypes_filtered = df_phenotypes_filtered.iloc[:12]  # Janvier à Décembre

# Ajouter colonne 'Semaine' fictive (une semaine par mois)
df_phenotypes_filtered["Semaine"] = df_phenotypes_filtered.index + 1
df_phenotypes_filtered["Année"] = 2024

# Mise en forme long format
phenotypes_long = df_phenotypes_filtered.melt(
    id_vars=["Semaine", "Année"], value_vars=["MRSA", "VRSA", "Wild", "others"],
    var_name="Phénotype", value_name="Nombre"
)

# Graphique
st.subheader("Évolution hebdomadaire par phénotype")
fig, ax = plt.subplots(figsize=(15, 7))
for phenotype in phenotypes_long["Phénotype"].unique():
    data = phenotypes_long[phenotypes_long["Phénotype"] == phenotype]
    ax.plot(data["Semaine"], data["Nombre"], label=phenotype, linewidth=3, marker='o')

ax.set_xlabel("Semaine", fontsize=16)
ax.set_ylabel("Nombre de cas", fontsize=16)
ax.set_title("Nombre de cas hebdomadaire par phénotype (2024)", fontsize=20, weight='bold')
ax.legend(title="Phénotype")
ax.grid(True)
st.pyplot(fig)
