import streamlit as st
import json
import os
from streamlit_autorefresh import st_autorefresh

# Veritabanı
DB_FILE = "istekler.json"

def veri_yukle():
    if not os.path.exists(DB_FILE): return {"istekler": [], "aktif_kullanicilar": {}}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {"istekler": [], "aktif_kullanicilar": {}}

def veri_kaydet(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

# Sayfa Genişlik Ayarı (Sanatçı için daraltılabilir yapı)
st.set_page_config(page_title="Sahne", layout="centered")

# CSS ile butonları ve başlıkları gönderdiğiniz taslağa benzetiyoruz
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #FDE992 !important;
        color: black !important;
        font-weight: bold !important;
        border: 2px solid #1d3311 !important;
        height: 50px;
        font-size: 20px;
    }
    .istek-baslik {
        background-color: #FDE992;
        color: black;
        text-align: center;
        font-weight: bold;
        padding: 10px;
        border: 2px solid #1d3311;
        margin-bottom: 10px;
    }
    .main { background-color: #314d1c; } /* Arka plan yeşili */
    div[data-testid="stVerticalBlock"] { gap: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

if 'user_id' not in st.session_state:
    import uuid
    st.session_state.user_id = str(uuid.uuid4())

# URL Parametresi ile Mod Seçimi (?mod=sanatci)
params = st.query_params
mod = params.get("mod", "seyirci")

# --- SEYİRCİ EKRANI ---
if mod == "seyirci":
    data = veri_yukle()
    kullanici_istegi = data["aktif_kullanicilar"].get(st.session_state.user_id)
    
    # EN ÜSTTEKİ GÖNDER BUTONU (Aynı zamanda başlık görevi görüyor)
    if st.button("İSTEK GÖNDER", disabled=(kullanici_istegi is not None)):
        if "secilen_sarki" not in st.session_state or st.session_state.secilen_sarki is None:
            st.error("Lütfen önce bir seçim yapınız!")
        else:
            data["istekler"].append({"id": st.session_state.user_id, "sarki": st.session_state.secilen_sarki})
            data["aktif_kullanicilar"][st.session_state.user_id] = st.session_state.secilen_sarki
            veri_kaydet(data)
            st.rerun()

    # REPERTUAR LİSTESİ
    repertuar = [f"Şarkı {i}" for i in range(1, 21)] # Örnek liste
    st.session_state.secilen_sarki = st.radio("", repertuar, index=None, label_visibility="collapsed")
    
    if kullanici_istegi:
        st.info(f"İletildi: {kullanici_istegi}")

# --- SANATÇI EKRANI ---
else:
    st_autorefresh(interval=3000, key="refresh")
    st.markdown('<div class="istek-baslik">İSTEKLER</div>', unsafe_allow_html=True)
    
    data = veri_yukle()
    
    for idx, item in enumerate(data["istekler"]):
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{item['sarki']}**")
        if col2.button("SİL", key=f"del_{idx}"):
            u_id = item['id']
            data["istekler"].pop(idx)
            if u_id in data["aktif_kullanicilar"]:
                del data["aktif_kullanicilar"][u_id]
            veri_kaydet(data)
            st.rerun()


