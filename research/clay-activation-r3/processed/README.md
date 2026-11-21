# Datasets R3 : calcination vs broyage

Générés par `scripts/build_datasets.py` à partir de **`r3_unified_dataset.csv`** (268 lignes TA + MCA, toutes avec chaleur R3 à 7 j ; les 17 lignes MTA et les 125 lignes Bahhou 2026 ont été supprimées du dépôt).

```
python3 scripts/build_datasets.py research/clay-activation-r3/r3_unified_dataset.csv research/clay-activation-r3/processed
python3 scripts/consistency.py research/clay-activation-r3/processed
```

### Pourquoi ce fichier source
`r3_unified_dataset.csv` contient tout ce qu'il y a dans l'Excel `TA_MCA_MTA_R3_XRF_QXRD_20261111.xlsx` (mêmes valeurs pour les identifiants communs) **plus** : Marsh et al. 2026 / S01 (48 lignes de broyage, dont 34 avec énergie mesurée), Zunino & Scrivener 2024 (12), Panzer 2024 / S03 et Koutsouradi 2024 / S02 avec température et minéralogie, et 10 lignes Mañosa de plus. Les anciens fichiers `r3_measurements.csv` et `r3_auxiliary_measurements.csv` ont été supprimés : leur chaleur 7 j est entièrement dans ce fichier.

## Fichiers

| Fichier | Lignes | Argiles distinctes (`parent_clay_id`) |
|---|---|---|
| `calcination_dataset.csv` | 112 | 81 |
| `mechanical_dataset.csv` | 147 | 30 |
| `dropped_rows.csv` | 9 | lignes retirées, avec la raison |

22 argiles (`parent_clay_id`) sont présentes dans les deux tables. Pour un jeu commun : `pd.concat` des deux fichiers.

Lignes retirées : 6 Martirena 2026 (température de calcination non rapportée ; refroidissement oxydant vs réducteur), 2 Vallina 2024 (= Koufany 2025 Ref1/Ref2-SCC), 1 doublon exact interne Plusquellec (IC_M300_60_TEA1p0).

## Colonnes

**Communes** : `sample_id`, `parent_clay_id` (clé de CV groupée : même publication + même composition brute), `reference` (filtre / CV par source ; détails de la source : joindre `r3_unified_dataset.csv` sur `sample_id`), minéralogie brute (`*_pct`), oxydes, `post_d50_um`.

**Calcination** : `calcination_temp_c`, `dwell_min`, `furnace_type` (flash, rotary_kiln, muffle, bogie_hearth, lab_furnace).

**Broyage** : `milling_time_min` (147/147), `mill_rpm` (142), `ball_to_powder_ratio` (132), `mill_type` (121), `grinding_aid_tea_wt_pct` (14), `co_milled_glass_pct` / `co_milled_na2sio3_pct` (Callender : additifs co-broyés), `milling_energy_kwh_per_kg` (34, Marsh 2026).
Les variables extraites (`mill_rpm`, `ball_to_powder_ratio`, `mill_type`, `furnace_type`, TEA, additifs) viennent des codes d'échantillon (prioritaires) puis des notes de chaque ligne.

**Cible** : `r3_heat_7d_j_per_g` (J/g de SCM, 7 j, 40 °C).
- `r3_quality` : exact_numeric / figure_read / derived.
- `r3_unit_converted` : vrai si convertie depuis J/g de solides (Zunino 2024, facteur 4,5 donné par les auteurs).
- `protocol_documented` : protocole R3 noté dans la source.

## Points d'attention
- Bahhou 2026 (S22, 125 lignes) supprimé : compilation secondaire sans source primaire par ligne, valeurs > 1000 J/g et paires contradictoires ; en CV groupée, l'ajouter augmentait la RMSE sur les autres sources de 161 à 188 J/g.
- Marsh 2026 : pas de composition brute dans la source (K = kaolin, Mt = montmorillonite) ; les 52 autres valeurs originales sont sur Zenodo (10.5281/zenodo.17771208), non extraites.
- `milling_energy_kwh_per_kg` : seulement Marsh 2026 ; ailleurs utiliser `mill_rpm`, `milling_time_min`, `ball_to_powder_ratio`.
- Sources citées dans `sources.json` mais sans aucune donnée dans le dépôt : S04 (UR2, 47 échantillons avec R3, XRF, QXRD), S05 (Maier, 13 argiles), S08/S18 (palygorskites), S11, S12.
