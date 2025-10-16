import streamlit as st
import pandas as pd
import json
import io
import matplotlib.pyplot as plt
from collections import Counter
import random
from itertools import combinations

st.set_page_config(page_title="Generator Variante + Coordonate", page_icon="📍", layout="wide")

st.title("📍 Generator Variante + Coordonate (Integrat)")

# --- Session State ---
if "variants" not in st.session_state:
    st.session_state.variants = []
if "top_numbers" not in st.session_state:
    st.session_state.top_numbers = []
if "frequency" not in st.session_state:
    st.session_state.frequency = {}

# --- TAB 1: GENERARE VARIANTE ---
tab1, tab2 = st.tabs(["🎲 Generare Variante", "📍 Coordonate + Export"])

with tab1:
    st.header("🎲 Pasul 1: Generare Variante")
    
    # --- Secțiunea 1: Încărcarea datelor ---
    st.subheader("📊 1. Încarcă datele extragerilor")
    
    tab1a, tab1b = st.tabs(["📁 Import Fișier", "✍️ Manual"])
    
    with tab1a:
        uploaded_file = st.file_uploader("📂 CSV/TXT cu extragerile din runde", type=["csv", "txt"])
        
        if uploaded_file:
            try:
                content = uploaded_file.read().decode("utf-8")
                lines = [line.strip() for line in content.split("\n") if line.strip()]
                
                all_numbers = []
                for line in lines:
                    numbers = [int(x.strip()) for x in line.split(",")]
                    all_numbers.extend(numbers)
                
                frequency = Counter(all_numbers)
                sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
                st.session_state.frequency = dict(sorted_freq)
                
                st.success(f"✅ Încărcate {len(lines)} runde cu total {len(all_numbers)} numere")
                
                st.subheader("📋 Rundele încărcate:")
                rounds_df = pd.DataFrame([[i+1, line] for i, line in enumerate(lines)], columns=["Runda", "Numere"])
                st.dataframe(rounds_df, use_container_width=True, hide_index=True)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Runde", len(lines))
                col2.metric("Total numere", len(all_numbers))
                col3.metric("Numere unice", len(frequency))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🔥 Top 15 frecvente")
                    top15_df = pd.DataFrame(sorted_freq[:15], columns=["Număr", "Frecvență"])
                    st.dataframe(top15_df, use_container_width=True)
                
                with col2:
                    st.subheader("❄️ Bottom 15 reci")
                    bottom15_df = pd.DataFrame(sorted_freq[-15:], columns=["Număr", "Frecvență"])
                    st.dataframe(bottom15_df, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Eroare: {str(e)}")
    
    with tab1b:
        st.subheader("✍️ Adaugă rundele manual")
        
        manual_input = st.text_area(
            "Introduce rundele (o rună pe linie, numere separate cu virgulă)",
            placeholder="7, 27, 22, 34, 59, 14, 55, 52, 47, 41, 51, 11\n51, 3, 61, 10, 27, 55, 24, 39, 12, 14, 65, 58",
            height=200
        )
        
        if st.button("✅ Procesează rundele"):
            if manual_input.strip():
                try:
                    lines = [line.strip() for line in manual_input.split("\n") if line.strip()]
                    
                    all_numbers = []
                    for line in lines:
                        numbers = [int(x.strip()) for x in line.split(",")]
                        all_numbers.extend(numbers)
                    
                    frequency = Counter(all_numbers)
                    sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
                    st.session_state.frequency = dict(sorted_freq)
                    
                    st.success(f"✅ Procesate {len(lines)} runde")
                    
                    st.subheader("📋 Rundele adăugate:")
                    rounds_df = pd.DataFrame([[i+1, line] for i, line in enumerate(lines)], columns=["Runda", "Numere"])
                    st.dataframe(rounds_df, use_container_width=True, hide_index=True)
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Runde", len(lines))
                    col2.metric("Total numere", len(all_numbers))
                    col3.metric("Numere unice", len(frequency))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("🔥 Top 15 frecvente")
                        top15_df = pd.DataFrame(sorted_freq[:15], columns=["Număr", "Frecvență"])
                        st.dataframe(top15_df, use_container_width=True)
                    
                    with col2:
                        st.subheader("❄️ Bottom 15 reci")
                        bottom15_df = pd.DataFrame(sorted_freq[-15:], columns=["Număr", "Frecvență"])
                        st.dataframe(bottom15_df, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ Eroare: {str(e)}")
    
    # --- Secțiunea 2: Configurare filtre ---
    st.subheader("⚙️ 2. Configurare filtre")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("❄️ Exclude cele mai reci numere")
        
        exclude_mode = st.radio(
            "Cum vrei să excludi?",
            ["🔢 Automata (cele mai reci)", "✍️ Manual (numere specifice)", "🔀 Ambele"],
            horizontal=True
        )
        
        exclude_numbers = set()
        auto_exclude = set()
        
        if exclude_mode in ["🔢 Automata (cele mai reci)", "🔀 Ambele"]:
            auto_cold_count = st.selectbox(
                "Exclude topul celor mai reci",
                [0, 5, 10, 15, 20],
                index=0
            )
            
            if st.session_state.frequency and auto_cold_count > 0:
                sorted_freq = sorted(st.session_state.frequency.items(), key=lambda x: x[1], reverse=True)
                auto_exclude = set([x[0] for x in sorted_freq[-auto_cold_count:]])
                if auto_exclude:
                    st.info(f"🔴 Auto-exclude ({auto_cold_count}): {sorted(auto_exclude)}")
        
        if exclude_mode in ["✍️ Manual (numere specifice)", "🔀 Ambele"]:
            manual_exclude_input = st.text_area(
                "Introduce numere de exclus manual (separate cu virgulă)",
                placeholder="Exemplu: 51, 2, 15",
                height=80
            )
            
            if manual_exclude_input.strip():
                try:
                    manual_exclude = set([int(x.strip()) for x in manual_exclude_input.split(",")])
                    if manual_exclude:
                        st.info(f"✋ Manual exclude: {sorted(manual_exclude)}")
                    exclude_numbers.update(manual_exclude)
                except:
                    st.error("❌ Format invalid")
        
        exclude_numbers.update(auto_exclude)
        
        if exclude_numbers:
            st.success(f"📌 Total excluse: {len(exclude_numbers)} numere")
    
    with col2:
        st.subheader("🔥 Numere pentru generare (top numere)")
        top_count = st.slider(
            "Câte numere din top?",
            min_value=10,
            max_value=66,
            value=50,
            step=1
        )
        
        if st.session_state.frequency:
            sorted_freq = sorted(st.session_state.frequency.items(), key=lambda x: x[1], reverse=True)
            top_numbers = [x[0] for x in sorted_freq[:top_count] if x[0] not in exclude_numbers]
            st.session_state.top_numbers = top_numbers
            st.success(f"✅ {len(top_numbers)} numere disponibile")
            st.write("Numere:", sorted(top_numbers))
    
    # --- Secțiunea 3: Strategii de generare ---
    st.subheader("🎲 3. Strategii de generare")
    
    strategy = st.radio(
        "Alege strategia:",
        [
            "🎯 Standard (4 numere aleatoare)",
            "🔥 Hot Numbers (3 din top 10 + 1 din rest)",
            "❄️ Cold-Hot Hybrid (2 din top 20 + 2 din 21-50)",
            "🔥❄️ Premium Hybrid (3 din top 25 + 1 din rest - TOATE POSIBILELE)",
            "🌀 Random Pairs (2 perechi aleatoare)",
            "⚡ Frecvență Ponderată (numere cu mai multă frecvență)",
            "🎪 Mix Strategy (combinație din toate)"
        ]
    )
    
    num_variants = st.number_input(
        "Câte variante?",
        min_value=100,
        max_value=5000,
        value=1000,
        step=100
    )
    
    if st.button("🚀 Generează variante"):
        if not st.session_state.top_numbers:
            st.error("❌ Încarcă datele și configurează filtrele")
        else:
            top_nums = st.session_state.top_numbers
            
            if strategy == "🔥❄️ Premium Hybrid (3 din top 25 + 1 din rest - TOATE POSIBILELE)":
                top25 = top_nums[:25]
                rest = top_nums[25:]
                
                if len(rest) > 0:
                    st.session_state.variants = []
                    for three in combinations(top25, 3):
                        for one in rest:
                            variant = tuple(sorted(list(three) + [one]))
                            st.session_state.variants.append(variant)
                    st.session_state.variants = sorted(list(set(st.session_state.variants)))
                    
                    st.success(f"✅ Generate {len(st.session_state.variants)} variante UNICE")
                    st.info(f"📊 Strategie: {strategy}")
                else:
                    st.error("❌ Nu sunt suficiente numere")
            
            else:
                variants = set()
                max_attempts = num_variants * 50
                attempts = 0
                
                while len(variants) < num_variants and attempts < max_attempts:
                    attempts += 1
                    
                    if strategy == "🎯 Standard (4 numere aleatoare)":
                        variant = tuple(sorted(random.sample(top_nums, 4)))
                    
                    elif strategy == "🔥 Hot Numbers (3 din top 10 + 1 din rest)":
                        top10 = top_nums[:10]
                        rest = top_nums[10:]
                        if len(rest) > 0:
                            three = random.sample(top10, min(3, len(top10)))
                            one = random.sample(rest, 1)
                            variant = tuple(sorted(three + one))
                        else:
                            variant = tuple(sorted(random.sample(top_nums, 4)))
                    
                    elif strategy == "❄️ Cold-Hot Hybrid (2 din top 20 + 2 din 21-50)":
                        top20 = top_nums[:20]
                        rest = top_nums[20:]
                        if len(rest) >= 2:
                            two_hot = random.sample(top20, min(2, len(top20)))
                            two_cold = random.sample(rest, min(2, len(rest)))
                            variant = tuple(sorted(two_hot + two_cold))
                        else:
                            variant = tuple(sorted(random.sample(top_nums, 4)))
                    
                    elif strategy == "🌀 Random Pairs (2 perechi aleatoare)":
                        if len(top_nums) >= 4:
                            pair1 = random.sample(top_nums, 2)
                            pair2 = random.sample(top_nums, 2)
                            variant = tuple(sorted(pair1 + pair2))
                        else:
                            variant = tuple(sorted(random.sample(top_nums, 4)))
                    
                    elif strategy == "⚡ Frecvență Ponderată":
                        weights = [st.session_state.frequency.get(n, 1) for n in top_nums]
                        variant = tuple(sorted(random.choices(top_nums, weights=weights, k=4)))
                    
                    elif strategy == "🎪 Mix Strategy (combinație din toate)":
                        choice = random.randint(1, 6)
                        if choice == 1:
                            variant = tuple(sorted(random.sample(top_nums, 4)))
                        elif choice == 2:
                            top10 = top_nums[:10]
                            rest = top_nums[10:]
                            variant = tuple(sorted(random.sample(top10, 3) + random.sample(rest, 1))) if len(rest) > 0 else tuple(sorted(random.sample(top_nums, 4)))
                        elif choice == 3:
                            top20 = top_nums[:20]
                            rest = top_nums[20:]
                            variant = tuple(sorted(random.sample(top20, 2) + random.sample(rest, 2))) if len(rest) >= 2 else tuple(sorted(random.sample(top_nums, 4)))
                        elif choice == 4:
                            variant = tuple(sorted(random.sample(top_nums, 2) + random.sample(top_nums, 2)))
                        elif choice == 5:
                            weights = [st.session_state.frequency.get(n, 1) for n in top_nums]
                            variant = tuple(sorted(random.choices(top_nums, weights=weights, k=4)))
                        else:
                            top25 = top_nums[:25]
                            rest = top_nums[25:]
                            variant = tuple(sorted(random.sample(top25, 3) + random.sample(rest, 1))) if len(rest) > 0 else tuple(sorted(random.sample(top_nums, 4)))
                    
                    variants.add(variant)
                
                st.session_state.variants = sorted(list(variants))
                st.success(f"✅ Generate {len(st.session_state.variants)} variante unice")
                st.info(f"📊 Strategie: {strategy}")
    
    # --- Preview variante ---
    if st.session_state.variants:
        st.subheader("📋 Preview Variante Generate")
        preview_count = st.slider("Câte variante să afișez?", 5, 50, 20)
        
        preview_df = pd.DataFrame(
            [[i+1, " ".join(map(str, v))] for i, v in enumerate(st.session_state.variants[:preview_count])],
            columns=["ID", "Combinație"]
        )
        st.dataframe(preview_df, use_container_width=True, hide_index=True)

# --- TAB 2: COORDONATE + EXPORT ---
with tab2:
    st.header("📍 Pasul 2: Adaugă Coordonate și Exportă")
    
    # --- Secțiunea 1: Coordonate ---
    st.subheader("1️⃣ Coordonate")
    
    uploaded_coords = st.file_uploader(
        "📂 Încarcă fișierul cu coordonate (acceptă CSV sau JSON)",
        type=["csv", "json"],
        key="coords_uploader"
    )
    
    coord_df = pd.DataFrame(columns=["numar", "x", "y"])
    
    if uploaded_coords:
        if uploaded_coords.name.endswith(".csv"):
            coord_df = pd.read_csv(uploaded_coords)
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
            placeholder="1,367,998\n2,408,998\n3,449,998",
            height=150
        )
        if manual_coords.strip():
            coord_df = pd.read_csv(io.StringIO(manual_coords), names=["numar", "x", "y"])
            coord_df["numar"] = pd.to_numeric(coord_df["numar"], errors="coerce")
            coord_df["x"] = pd.to_numeric(coord_df["x"], errors="coerce")
            coord_df["y"] = pd.to_numeric(coord_df["y"], errors="coerce")
            coord_df = coord_df.dropna()
    
    if not coord_df.empty:
        st.dataframe(coord_df.head(10))
    
    # --- Generare și Export ---
    st.subheader("2️⃣ Generare Coordonate și Export")
    
    if st.session_state.variants and not coord_df.empty:
        # Creare variants_df din session state
        variants_df = pd.DataFrame(
            [[i+1, " ".join(map(str, v))] for i, v in enumerate(st.session_state.variants)],
            columns=["id", "combinatie"]
        )
        
        # Procesare coordonate
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
        st.warning("⚠️ Generează variante și încarcă coordonatele pentru a continua.")
