import streamlit as st
import pandas as pd
import json
import io
import matplotlib.pyplot as plt

st.set_page_config(page_title="Generator Coordonate", page_icon="📍", layout="centered")

st.title("📍 Generator Coordonate pentru Variante")

st.markdown("""
Adaugă coordonate și variante (manual, CSV sau JSON).  
Apoi generează automat coordonatele, vizualizează-le și exportă în format `.lua`.
""")

# --- Secțiunea 1: Coordonate ---
st.header("1️⃣ Coordonate")

uploaded_coords = st.file_uploader(
    "📂 Încarcă fișierul cu coordonate (acceptă CSV sau JSON)",
    type=["csv", "json"]
)

coord_df = pd.DataFrame(columns=["numar", "x", "y"])

if uploaded_coords:
    if uploaded_coords.name.endswith(".csv"):
        coord_df = pd.read_csv(uploaded_coords)
        # Normalizează coloane și convertește la numere
        coord_df.columns = coord_df.columns.str.lower().str.strip()
        if "nr" in coord_df.columns:
            coord_df.rename(columns={"nr": "numar"}, inplace=True)
        coord_df["numar"] = pd.to_numeric(coord_df["numar"], errors="coerce")
        coord_df["x"] = pd.to_numeric(coord_df["x"], errors="coerce")
        coord_df["y"] = pd.to_numeric(coord_df["y"], errors="coerce")
        coord_df = coord_df.dropna()
        st.success(f"Au fost încărcate {len(coord_df)} coordonate din CSV.")
    elif uploaded_coords.name.endswith(".json"):
        data = json.load(uploaded_coords)
        if isinstance(data, dict) and "coordinates" in data:
            coords = data["coordinates"]
        elif isinstance(data, list):
            coords = data
        else:
            st.error("⚠️ Format JSON invalid")
            coords = []
        if coords:
            coord_df = pd.DataFrame(coords)
            coord_df.columns = coord_df.columns.str.lower().str.strip()
            if "nr" in coord_df.columns:
                coord_df.rename(columns={"nr": "numar"}, inplace=True)
            coord_df["numar"] = pd.to_numeric(coord_df["numar"], errors="coerce")
            coord_df["x"] = pd.to_numeric(coord_df["x"], errors="coerce")
            coord_df["y"] = pd.to_numeric(coord_df["y"], errors="coerce")
            coord_df = coord_df.dropna()
            st.success(f"Au fost încărcate {len(coord_df)} coordonate din JSON.")
else:
    manual_coords = st.text_area(
        "Adaugă coordonate manual (format: numar,x,y)",
        placeholder="1,367,998\n2,408,998\n3,449,998"
    )
    if manual_coords.strip():
        coord_df = pd.read_csv(io.StringIO(manual_coords), names=["numar", "x", "y"])
        coord_df["numar"] = pd.to_numeric(coord_df["numar"], errors="coerce")
        coord_df["x"] = pd.to_numeric(coord_df["x"], errors="coerce")
        coord_df["y"] = pd.to_numeric(coord_df["y"], errors="coerce")
        coord_df = coord_df.dropna()

if not coord_df.empty:
    st.dataframe(coord_df.head(10))

# --- Secțiunea 2: Variante ---
st.header("2️⃣ Variante")

uploaded_variants = st.file_uploader("📂 Încarcă fișierul CSV cu variante", type=["csv"])
variants_df = pd.DataFrame(columns=["id", "combinatie"])

if uploaded_variants:
    variants_df = pd.read_csv(uploaded_variants)
    variants_df.columns = variants_df.columns.str.lower().str.strip()
    if "combinație" in variants_df.columns:
        variants_df.rename(columns={"combinație": "combinatie"}, inplace=True)
    st.success(f"Au fost încărcate {len(variants_df)} variante.")
else:
    manual_variants = st.text_area(
        "Adaugă variante manual (format: id,combinație)",
        placeholder="1,1 2 3 4\n2,2 3 4 5"
    )
    if manual_variants.strip():
        variants_df = pd.read_csv(io.StringIO(manual_variants), names=["id", "combinatie"])

if not variants_df.empty:
    st.dataframe(variants_df.head(10))

# --- Secțiunea 3: Generare ---
st.header("3️⃣ Generare coordonate, vizualizare și export")

if not coord_df.empty and not variants_df.empty:
    coord_map = coord_df.set_index("numar")[["x", "y"]].to_dict(orient="index")

    results = []
    for _, row in variants_df.iterrows():
        combo_nums = str(row["combinatie"]).split()
        coords = []
        for num in combo_nums:
            try:
                n = int(float(num))
                if n in coord_map:
                    coords.append(coord_map[n])
                else:
                    coords.append({"x": None, "y": None})
            except:
                coords.append({"x": None, "y": None})
        results.append({
            "id": row["id"],
            "combinatie": row["combinatie"],
            "coordonate": coords
        })

    result_df = pd.DataFrame(results)
    st.success("✅ Coordonatele au fost generate.")
    st.dataframe(result_df.head(10))

    # --- Vizualizare ---
    st.subheader("📈 Vizualizare grafică")
    variant_select = st.selectbox("Alege ID variantă", result_df["id"])
    selected = result_df[result_df["id"] == variant_select].iloc[0]
    coords_list = selected["coordonate"]

    xs = [c["x"] for c in coords_list if c["x"] is not None]
    ys = [c["y"] for c in coords_list if c["y"] is not None]

    if xs and ys:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(xs, ys, s=100, alpha=0.6)
        for i, (x, y) in enumerate(zip(xs, ys)):
            ax.text(x, y, str(i + 1), fontsize=9, ha='right')
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title(f"Varianța {variant_select}")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    else:
        st.warning("Nu există coordonate valide.")

    # --- Export CSV ---
    csv_buffer = io.StringIO()
    result_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="⬇️ Descarcă rezultatele (CSV)",
        data=csv_buffer.getvalue(),
        file_name="rezultate_coordonate.csv",
        mime="text/csv"
    )

    # --- Export LUA ---
    lua_output = "local variants = {\n"
    for idx, row in result_df.iterrows():
        lua_output += f"    -- Varianta {row['id']}\n    {{"
        coords = [f"{{x={int(c['x'])}, y={int(c['y'])}}}" for c in row["coordonate"] if c['x'] is not None]
        
        # Grupează coordonatele pe mai multe rânduri (4 pe rând)
        for i in range(0, len(coords), 4):
            group = ", ".join(coords[i:i+4])
            if i == 0:
                lua_output += group
            else:
                lua_output += ", " + group
            if i + 4 < len(coords):
                lua_output += ",\n"
        
        lua_output += "}},\n"
    lua_output += "}\n"

    st.download_button(
        label="📜 Descarcă fișierul LUA",
        data=lua_output,
        file_name="variants.lua",
        mime="text/plain"
    )
else:
    st.warning("⚠️ Încarcă coordonatele și variantele înainte de generare.")
