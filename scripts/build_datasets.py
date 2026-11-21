"""Construit les datasets calcination / broyage à partir de r3_unified_dataset.csv.

r3_unified_dataset.csv (TA + MCA) est la seule source : il remplace l'Excel
TA_MCA_MTA et les anciens r3_measurements / r3_auxiliary_measurements (supprimés).

Usage: python3 build_datasets.py <r3_unified_dataset.csv> <out_dir>
"""
import sys, re
import numpy as np
import pandas as pd

src, out = sys.argv[1:3]
u = pd.read_csv(src)
n_in = len(u)

RENAME = {
    "Sample_ID (unified)": "sample_id", "Activation_type": "activation_type",
    "R3_7d (J/g SCM)": "r3_heat_7d_j_per_g", "Original sample ID": "original_sample_id",
    "Kaolinite (wt%)": "kaolinite_pct", "Smectite / Mnt (wt%)": "smectite_pct",
    "Illite / Mica (wt%)": "illite_mica_pct", "Mixed I/S (wt%)": "mixed_is_pct",
    "Chlorite (wt%)": "chlorite_pct", "Quartz (wt%)": "quartz_pct", "Calcite (wt%)": "calcite_pct",
    "Dolomite (wt%)": "dolomite_pct", "Feldspar (wt%)": "feldspar_pct",
    "Other minerals (wt%)": "other_minerals_pct", "Raw amorphous (wt%)": "raw_amorphous_pct",
    "Total clay (reported wt%)": "total_clay_pct", "Al2O3 (wt%)": "al2o3_pct",
    "SiO2 (wt%)": "sio2_pct", "Fe2O3 (wt%)": "fe2o3_pct", "CaO (wt%)": "cao_pct",
    "MgO (wt%)": "mgo_pct", "K2O (wt%)": "k2o_pct", "Na2O (wt%)": "na2o_pct",
    "TiO2 (wt%)": "tio2_pct", "LOI (wt%)": "loi_pct",
    "TA temperature (°C)": "calcination_temp_c", "TA hold (min)": "dwell_min",
    "Milling time (min)": "milling_time_min", "Milling energy (kWh/kg SCM)": "milling_energy_kwh_per_kg",
    "D50 (µm)": "post_d50_um", "Reference (author-year)": "reference", "Reference URL": "reference_url",
    "Source table / figure": "source_locator", "R3 data quality": "r3_data_quality_raw",
    "Composition source / method": "composition_method", "Notes / QC": "notes",
    "R3 protocol / comparability": "r3_protocol",
}
missing = set(RENAME) - set(u.columns)
assert not missing, missing
d = u.rename(columns=RENAME)
d["r3_heat_7d_j_per_g"] = pd.to_numeric(d.r3_heat_7d_j_per_g, errors="coerce")
assert d.r3_heat_7d_j_per_g.notna().all()

TXT = (d.notes.fillna("") + " | " + d.source_locator.fillna("") + " | " + d.r3_protocol.fillna("")).str.lower()
SID = d.sample_id.astype(str)

# ------------------------------------------------------------------ 1. exclusions
log = []
def drop(mask, reason):
    global d, TXT, SID
    for _, r in d[mask].iterrows():
        log.append({"sample_id": r.sample_id, "reference": r.reference,
                    "r3_heat_7d_j_per_g": r.r3_heat_7d_j_per_g, "reason": reason})
    keep = ~mask
    d, TXT, SID = d[keep].copy(), TXT[keep], SID[keep]

# Vallina 2024 (S07) = mêmes échantillons que Koufany 2025 Ref1/Ref2 (même groupe, mêmes T, valeurs exactes chez Koufany)
drop(SID.isin(["Vallina24_SAu-1_T750", "Vallina24_SWy-3_T800"]),
     "doublon de Koufany25_Ref1-SCC / Ref2-SCC (valeur exacte conservée)")

# ------------------------------------------------------------------ 2. qualité R3
def quality(q):
    q = str(q).lower()
    if "deriv" in q or "estimat" in q or "convert" in q:
        return "derived"
    if "approx" in q or "visual" in q or "read-off" in q or "figure-read" in q or "digitiz" in q:
        return "figure_read"
    return "exact_numeric"
d["r3_quality"] = d.r3_data_quality_raw.map(quality)
d["r3_unit_converted"] = TXT.str.contains("j/g solids") | d.r3_data_quality_raw.astype(str).str.contains("converted")
d["protocol_documented"] = d.r3_protocol.notna()
d["is_secondary_compilation"] = d.reference.astype(str).str.contains("secondary compilation")
d["process_family"] = d.activation_type.map({"TA": "thermal", "MCA": "mechanical"})

# ------------------------------------------------------------------ 3. variables extraites des notes / IDs
def first_num(pattern, s):
    m = re.search(pattern, s)
    return float(m.group(1)) if m else np.nan

rpm, bpr, aid = [], [], []
for sid, t, fam in zip(SID, TXT, d.process_family):
    if fam != "mechanical":
        rpm.append(np.nan); bpr.append(np.nan); aid.append(np.nan); continue
    # vitesse : code d'échantillon en priorité (spécifique à la ligne), sinon notes
    r = np.nan
    for pat in [r"MuscMCA_(\d{3})_", r"DoE_(\d{3})_", r"_M(\d{3})_\d+", r"_M(\d{3})(?:_|$)",
                r"_H(\d{3})_", r"KM-(\d{3})-"]:
        m = re.search(pat, sid)
        if m:
            r = float(m.group(1)); break
    if np.isnan(r):
        r = first_num(r"(\d{2,4})\s*rpm", t)
    rpm.append(r)
    b = first_num(r"BPR(\d+)", sid)
    if np.isnan(b):
        b = first_num(r"bpr\s*(?:of\s*)?~?\s*(\d+(?:\.\d+)?)", t)
    if np.isnan(b):
        b = first_num(r"(\d+(?:\.\d+)?)\s*:\s*1\s*bpr", t)
    bpr.append(b)
    a = re.search(r"TEA(\d)p(\d+)", sid)
    if a:
        aid.append(float(f"{a.group(1)}.{a.group(2)}"))
    else:
        aid.append(first_num(r"(\d+(?:\.\d+)?)\s*wt%\s*(?:triethanolamine|tea)", t))
d["mill_rpm"], d["ball_to_powder_ratio"], d["grinding_aid_tea_wt_pct"] = rpm, bpr, aid

def mill_type(t):
    for pat, lab in [(r"pm ?100|pm ?400|pulverisette|fritsch p-?6|planetary", "planetary"),
                     (r"vibrating disk|vibratory disc|disc mill|disk mill", "vibrating_disk"),
                     (r"attrit", "attritor"), (r"vibrat", "vibratory"), (r"drum mill", "drum"),
                     (r"roller mill|roll mill", "roller"), (r"ball mill", "ball_unspecified")]:
        if re.search(pat, t):
            return lab
    return np.nan
d["mill_type"] = [mill_type(t) if f == "mechanical" else np.nan for t, f in zip(TXT, d.process_family)]

def furnace(t):
    for pat, lab in [(r"flash", "flash"), (r"rotary kiln|rotary-kiln", "rotary_kiln"),
                     (r"bogie hearth", "bogie_hearth"), (r"muffle", "muffle"),
                     (r"chamber furnace|laboratory furnace|lab furnace|electric furnace", "lab_furnace")]:
        if re.search(pat, t):
            return lab
    return np.nan
d["furnace_type"] = [furnace(t) if f == "thermal" else np.nan for t, f in zip(TXT, d.process_family)]
# co-broyage avec un additif (Callender : verre recyclé WGP, silicate de sodium), en % massique
def pct(pat, sid):
    m = re.search(pat, sid)
    return float(m.group(1).replace("_", ".")) if m else 0.0
d["co_milled_glass_pct"] = [pct(r"_(\d+(?:_\d)?)WGP", sid) if f == "mechanical" else np.nan for sid, f in zip(SID, d.process_family)]
d["co_milled_na2sio3_pct"] = [pct(r"_(\d+(?:_\d)?)Na2SiO3", sid) if f == "mechanical" else np.nan for sid, f in zip(SID, d.process_family)]
d["cooling"] = np.where(SID.str.endswith("_CC"), "reducing",
                        np.where(SID.str.startswith("Martirena") & SID.str.endswith("_NC"), "oxidizing", None))

# ------------------------------------------------------------------ 4. parent_clay_id
COMP = ["sio2_pct", "al2o3_pct", "fe2o3_pct", "kaolinite_pct", "smectite_pct", "illite_mica_pct"]
ref_key = d.reference.astype(str).str.extract(r"^([^\s,(]+)")[0].str.replace("[^A-Za-z]", "", regex=True)
ckey = d[COMP].apply(lambda r: "" if r.isna().all() else "|".join("na" if pd.isna(v) else f"{v:.1f}" for v in r), axis=1)
codes = {k: i for i, k in enumerate(sorted(set(zip(ref_key, ckey))), 1)}
# sans composition : argile = préfixe de l'ID avant le code de traitement (ex. Marsh26_K_D5 -> Marsh26_K)
def stem(sid):
    parts = sid.split("_")
    return "_".join(parts[:2]) if len(parts) > 2 else sid
d["parent_clay_id"] = [f"{rk}-C{codes[(rk, ck)]:03d}" if ck else f"{rk}-{stem(s)}"
                       for rk, ck, s in zip(ref_key, ckey, SID)]

# doublons exacts internes (même argile, mêmes conditions, même valeur) : surtout Bahhou
key = ["parent_clay_id", "process_family", "calcination_temp_c", "dwell_min", "milling_time_min",
       "mill_rpm", "ball_to_powder_ratio", "r3_heat_7d_j_per_g"]
dup = d.duplicated(key, keep="first") & d[COMP].notna().any(axis=1)
drop(dup, "doublon exact interne (même argile, mêmes conditions, même valeur)")

# ------------------------------------------------------------------ 5. sortie
# sample_id : clé (jointure avec r3_unified_dataset pour la traçabilité) ; parent_clay_id : groupes de CV ;
# reference : filtre / CV par source ; is_secondary_compilation : avec / sans Bahhou
ID = ["sample_id", "parent_clay_id", "reference", "is_secondary_compilation"]
CLAY = ["kaolinite_pct", "smectite_pct", "illite_mica_pct", "mixed_is_pct", "chlorite_pct", "quartz_pct",
        "calcite_pct", "dolomite_pct", "feldspar_pct", "other_minerals_pct", "raw_amorphous_pct",
        "total_clay_pct", "sio2_pct", "al2o3_pct", "fe2o3_pct", "cao_pct", "mgo_pct", "k2o_pct",
        "na2o_pct", "tio2_pct", "loi_pct", "composition_method"]
THERMAL = ["calcination_temp_c", "dwell_min", "furnace_type", "cooling"]
MECH = ["milling_time_min", "mill_rpm", "ball_to_powder_ratio", "mill_type", "grinding_aid_tea_wt_pct",
        "co_milled_glass_pct", "co_milled_na2sio3_pct", "milling_energy_kwh_per_kg"]
POST = ["post_d50_um"]
TARGET = ["r3_heat_7d_j_per_g", "r3_quality", "r3_unit_converted", "protocol_documented",
          "r3_data_quality_raw", "r3_protocol", "notes"]

allx = d[ID + ["process_family"] + CLAY + THERMAL + MECH + POST + TARGET].reset_index(drop=True)
th = allx[allx.process_family == "thermal"][ID + CLAY + THERMAL + POST + TARGET]
me = allx[allx.process_family == "mechanical"][ID + CLAY + MECH + POST + TARGET]
th.to_csv(f"{out}/calcination_dataset.csv", index=False)
me.to_csv(f"{out}/mechanical_dataset.csv", index=False)
pd.DataFrame(log).to_csv(f"{out}/dropped_rows.csv", index=False)

# ------------------------------------------------------------------ 6. contrôles
assert len(th) + len(me) == len(allx) == n_in - len(log)
assert allx.sample_id.is_unique
print(f"input {n_in} | dropped {len(log)} | thermal {len(th)} | mechanical {len(me)}")
print(pd.DataFrame(log).reason.value_counts().to_string())
for name, df in [("thermal", th), ("mechanical", me)]:
    print(f"\n== {name}: rows {len(df)}, parent clays {df.parent_clay_id.nunique()}")
    print(" quality:", df.r3_quality.value_counts().to_dict())
    cols = THERMAL if name == "thermal" else MECH
    print(" filled:", {c: int(df[c].notna().sum()) for c in cols + ["post_d50_um"]})
pt = set(th.parent_clay_id); pm = set(me.parent_clay_id)
print("\nclays with both thermal and mechanical:", len(pt & pm))
