# ML-2026-P2: Clay Activation & R³ Pozzolanic Reactivity Database

Ce dépôt rassemble, harmonise et structure les données expérimentales de réactivité pouzzolanique des argiles activées mesurées par calorimétrie isotherme **R³ (Rapid, Relevant and Reliable)** selon les standards ASTM C1897-20 / RILEM TC 267-TRM.

---

## 📊 Synthèse des Données Fusionnées

Le jeu de données unifié combine les données initiales du dépôt GitHub et la compilation multi-sources récente (TA / MCA) :

| Jeu de données | Fichier | Observations | Métrique principale | Activation couverte |
| :--- | :--- | :---: | :--- | :--- |
| **Jeu Unifié Principal (Machine Learning)** | [`research/clay-activation-r3/r3_unified_dataset.csv`](file:///c:/MAIN/Code/GitHub/ML-2026-P2/research/clay-activation-r3/r3_unified_dataset.csv) | **268** | **Chaleur R³ à 7 jours** ($J/g$ d'argile activée) | **TA** (120), **MCA** (148) |
| **Registre des Sources Bibliographiques** | [`research/clay-activation-r3/sources.json`](file:///c:/MAIN/Code/GitHub/ML-2026-P2/research/clay-activation-r3/sources.json) | **36 études** | Métadonnées, DOI, conditions | S01 à S36 |

---

## 🔬 Modes d'Activation Couverts

1. **Activation Thermique (TA - 120 échantillons)** :
   - Calcination statique (four à moufle), rotatif pilote, flash calciner industriel.
   - Températures de 400 °C à 1200 °C, temps de séjour de 15 min à 240 min.
2. **Activation Mécanochimique (MCA - 148 échantillons)** :
   - Broyage planétaire haute énergie (Retsch PM100/PM400, Fritsch P6).
   - Vitesses de rotation (150 à 650 rpm), temps de broyage (5 à 720 min), ratios billes/poudre (BPR 2:1 à 35:1), consommations énergétiques mesurées (kWh/kg).
*Activation mécano-thermique (MTA) : 17 valeurs R³ sur ~6 argiles, insuffisant pour un modèle ; supprimée du dépôt.*

---

## 📋 Dictionnaire des Variables (`r3_unified_dataset.csv`)

- **Identifiants & Cible** : `Sample_ID (unified)`, `Activation_type` (TA, MCA), `R3_7d (J/g SCM)`, `Original sample ID`
- **Minéralogie quantitative du précurseur brut (wt%)** : `Kaolinite`, `Smectite / Mnt`, `Illite / Mica`, `Mixed I/S`, `Chlorite`, `Quartz`, `Calcite`, `Dolomite`, `Feldspar`, `Other minerals`, `Raw amorphous`, `Total clay`
- **Composition chimique XRF (wt% oxydes)** : `Al2O3`, `SiO2`, `Fe2O3`, `CaO`, `MgO`, `K2O`, `Na2O`, `TiO2`, `LOI`
- **Paramètres opératoires d'activation** : `TA temperature (°C)`, `TA hold (min)`, `Milling time (min)`, `Milling energy (kWh/kg SCM)`, `D50 (µm)`
- **Traçabilité & Qualité** : `Reference (author-year)`, `Reference URL`, `Source table / figure`, `R3 data quality`, `Composition source / method`, `Notes / QC`, `R3 protocol / comparability`
