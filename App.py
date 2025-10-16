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

# --- Funcții ajutătoare ---
@st.cache_data
def incarca_coordonate(continut_fisier, tip_fisier):
    """Încarcă coordonate din CSV sau JSON"""
    try:
        if tip_fisier == "csv":
            df = pd.read_csv(io.BytesIO(continut_fisier))
        else:  # json
            data = json.loads(continut_fisier)
            if isinstance(data, dict) and "coordinates" in data:
                df = pd.DataFrame(data["coordinates"])
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                return pd.DataFrame()
        
        # Normalizează coloane
        df.columns = df.columns.str.lower().str.strip()
        if "nr" in df.columns:
            df.rename(columns={"nr": "numar"}, inplace=True)
        
        # Convertește în numere
        for col in ["numar", "x", "y"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        return df[["numar", "x", "y"]].dropna()
    except Exception as e:
        st.error(f"Eroare la încărcarea fișierului: {str(e)}")
        return pd.DataFrame()

def parseaza_coordonate_manuale(text):
    """Parsează coordonate introduse manual"""
    if not text.strip():
        return pd.DataFrame(columns=["numar", "x", "y"])
    try:
        df = pd.read_csv(io.StringIO(text), names=["numar", "x", "y"])
        df["numar"] = pd.to_numeric(df["numar"], errors="coerce")
        df["x"] = pd.to_numeric(df["x"], errors="coerce")
        df["y"] = pd.to_numeric(df["y"], errors="coerce")
        return df.dropna()
    except Exception as e:
        st.error(f"Eroare la parsare: {str(e)}")
        return pd.DataFrame()

def incarca_variante(continut_fisier):
    """Încarcă variante din CSV"""
    try:
        df = pd.read_csv(io.BytesIO(continut_fisier))
        df.columns = df.columns.str.lower().str.strip()
        if "combinație" in df.columns:
            df.rename(columns={"combinație": "combinatie"}, inplace=True)
        return df
    except Exception as e:
        st.error(f"Eroare la încărcarea variantelor: {str(e)}")
        return pd.DataFrame()

def genereaza_lua(result_df):
    """Generează output în format LUA cu template-ul complet"""
    lua_content = """-- Lista cu """ + str(len(result_df)) + """ de variante (fiecare cu """ + str(len(result_df.iloc[0]['coordonate']) if not result_df.empty else 0) + """ coordonate {x, y} distincte)
local variants = {
"""
    
    for idx, row in result_df.iterrows():
        coords = [f"{{x={int(c['x'])}, y={int(c['y'])}}}" 
                 for c in row["coordonate"] if c['x'] is not None]
        
        # Formatează coordonatele pe o singură linie
        coords_str = ", ".join(coords)
        lua_content += f"    {{{coords_str}}},\n"
    
    lua_content += """}

-- Coordonatele de bază pentru butonul Enter
local enterX, enterY = 607, 2016

-- Loop principal peste """ + str(len(result_df)) + """ variante
for i = 1, #variants do
    local numbers = variants[i]  -- Coordonatele variantei curente
    
    -- Loop peste coordonatele din variantă
    for j = 1, #numbers do
        local x, y = numbers[j].x, numbers[j].y
        Screen:click(x, y)  -- Touch la coordonata (tap rapid)
        local delay = math.random(500, 900)  -- Delay variabil 500-900 ms
        wait(delay)
    end
    
    -- După toate coordonatele: delay variabil 350-656 ms
    local postNumbersDelay = math.random(350, 656)
    wait(postNumbersDelay)
    
    -- Touch Enter cu variație random mică (±5 pe X, ±3 pe Y)
    local randomEnterX = enterX + math.random(-5, 5)
    local randomEnterY = enterY + math.random(-3, 3)
    Screen:click(randomEnterX, randomEnterY)
    
    -- Delay final variabil 5950-5999 ms
    local finalDelay = math.random(5950, 5999)
    wait(finalDelay)
end

-- Log pentru debug (vezi în console app-ului)
print("Macro finalizat după " .. #variants .. " variante cu succes!")
"""
    
    return lua_content

# --- Secțiunea 1: Coordonate ---
st.header("1️⃣ Coordonate")

col1, col2 = st.columns(2)
with col1:
    tip_input_coord = st.radio("Cum vrei să adaugi coordonate?", 
                               ["Manual", "Fișier"])

coord_df = pd.DataFrame(columns=["numar", "x", "y"])

if tip_input_coord == "Fișier":
    incarca_coords = st.file_uploader(
        "📂 Încarcă fișierul cu coordonate (CSV sau JSON)",
        type=["csv", "json"],
        key="coords_file"
    )
    if incarca_coords:
        continut = incarca_coords.read()
        tip = incarca_coords.name.split(".")[-1]
        coord_df = incarca_coordonate(continut, tip)
        if not coord_df.empty:
            st.success(f"✅ Au fost încărcate {len(coord_df)} coordonate.")
else:
    coords_manual = st.text_area(
        "Adaugă coordonate manual (format: numar,x,y)",
        placeholder="1,367,998\n2,408,998\n3,449,998",
        height=100
    )
    coord_df = parseaza_coordonate_manuale(coords_manual)
    if not coord_df.empty:
        st.success(f"✅ Au fost adăugate {len(coord_df)} coordonate.")

if not coord_df.empty:
    st.dataframe(coord_df, use_container_width=True)

# --- Secțiunea 2: Variante ---
st.header("2️⃣ Variante")

col1, col2 = st.columns(2)
with col1:
    tip_input_var = st.radio("Cum vrei să adaugi variante?", 
                             ["Manual", "Fișier"])

variants_df = pd.DataFrame(columns=["id", "combinatie"])

if tip_input_var == "Fișier":
    incarca_var = st.file_uploader(
        "📂 Încarcă fișierul CSV cu variante",
        type=["csv"],
        key="variants_file"
    )
    if incarca_var:
        variants_df = incarca_variante(incarca_var.read())
        if not variants_df.empty:
            st.success(f"✅ Au fost încărcate {len(variants_df)} variante.")
else:
    var_manual = st.text_area(
        "Adaugă variante manual (format: id,combinație)",
        placeholder="1,1 2 3 4\n2,2 3 4 5",
        height=100
    )
    if var_manual.strip():
        try:
            variants_df = pd.read_csv(io.StringIO(var_manual), 
                                     names=["id", "combinatie"])
            st.success(f"✅ Au fost adăugate {len(variants_df)} variante.")
        except Exception as e:
            st.error(f"Eroare la parsare: {str(e)}")

if not variants_df.empty:
    st.dataframe(variants_df, use_container_width=True)

# --- Secțiunea 3: Generare ---
st.header("3️⃣ Generare coordonate, vizualizare și export")

if not coord_df.empty and not variants_df.empty:
    # Creează o hartă cu coordonate pentru cautare rapidă
    coord_map = coord_df.set_index("numar")[["x", "y"]].to_dict(orient="index")

    rezultate = []
    for _, row in variants_df.iterrows():
        numere_combo = str(row["combinatie"]).split()
        coords = []
        for num in numere_combo:
            try:
                n = int(float(num))
                if n in coord_map:
                    coords.append(coord_map[n])
                else:
                    coords.append({"x": None, "y": None})
            except ValueError:
                coords.append({"x": None, "y": None})
        rezultate.append({
            "id": row["id"],
            "combinatie": row["combinatie"],
            "coordonate": coords
        })

    result_df = pd.DataFrame(rezultate)
    st.success("✅ Coordonatele au fost generate.")
    st.dataframe(result_df, use_container_width=True)

    # --- Vizualizare ---
    st.subheader("📈 Vizualizare grafică")
    varianta_selectata = st.selectbox("Alege ID variantă", result_df["id"])
    selectata = result_df[result_df["id"] == varianta_selectata].iloc[0]
    lista_coords = selectata["coordonate"]

    xs = [c["x"] for c in lista_coords if c["x"] is not None]
    ys = [c["y"] for c in lista_coords if c["y"] is not None]

    if xs and ys:
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.scatter(xs, ys, s=150, alpha=0.7, color='#1f77b4', 
                  edgecolors='black', linewidth=1.5)
        for i, (x, y) in enumerate(zip(xs, ys), 1):
            ax.annotate(str(i), (x, y), xytext=(5, 5), 
                       textcoords='offset points', fontsize=10, fontweight='bold')
        ax.set_xlabel("X", fontsize=12)
        ax.set_ylabel("Y", fontsize=12)
        ax.set_title(f"Varianța {varianta_selectata}", fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        st.pyplot(fig, use_container_width=True)
    else:
        st.warning("⚠️ Nu există coordonate valide.")

    # --- Descărcări ---
    st.subheader("📥 Descarcă rezultatele")
    col1, col2 = st.columns(2)
    
    with col1:
        buffer_csv = io.StringIO()
        result_df.to_csv(buffer_csv, index=False)
        st.download_button(
            label="⬇️ CSV",
            data=buffer_csv.getvalue(),
            file_name="rezultate_coordonate.csv",
            mime="text/csv"
        )
    
    with col2:
        lua_output = genereaza_lua(result_df)
        st.download_button(
            label="📜 LUA",
            data=lua_output,
            file_name="variants.lua",
            mime="text/plain"
        )
else:
    st.warning("⚠️ Încarcă coordonatele și variantele înainte de generare.")
