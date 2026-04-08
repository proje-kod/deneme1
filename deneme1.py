import streamlit as st
import json
import os
from streamlit_autorefresh import st_autorefresh

# --- VERİTABANI İŞLEMLERİ ---
DB_FILE = "istekler.json"

def veri_yukle():
    if not os.path.exists(DB_FILE): 
        return {"istekler": [], "aktif_kullanicilar": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: 
            return json.load(f)
    except: 
        return {"istekler": [], "aktif_kullanicilar": {}}

def veri_kaydet(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(data, f, ensure_ascii=False)

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Sahne İstek", layout="centered")

if 'user_id' not in st.session_state:
    import uuid
    st.session_state.user_id = str(uuid.uuid4())

data = veri_yukle()
kullanici_istegi = data["aktif_kullanicilar"].get(st.session_state.user_id)

# DURUMA GÖRE RENK VE METİN BELİRLEME
btn_color = "#dc3545" if kullanici_istegi else "#28a745" # Kırmızı : Yeşil
btn_text = "İSTEK İLETİLDİ" if kullanici_istegi else "İSTEK GÖNDER"

# --- GENEL CSS ---
st.markdown(f"""
    <style>
    .block-container {{
        padding-top: 3rem !important; 
        padding-bottom: 0rem !important;
    }}
    .stButton>button {{
        width: 100%;
        background-color: {btn_color} !important;
        color: white !important;
        font-weight: bold !important;
        border: 2px solid #1d3311 !important;
        height: 60px;
        font-size: 22px;
        border-radius: 10px;
        margin-top: 10px;
    }}
    .istek-baslik {{
        background-color: #FDE992;
        color: black;
        text-align: center;
        font-weight: bold;
        padding: 10px;
        border: 2px solid #1d3311;
        margin-bottom: 20px;
    }}
    /* Sanatçı Paneli İçin Özel Ayarlar */
    .sarki-metni {{
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 16px;
        color: #FDE992;
        padding-top: 5px;
        display: block;
    }}
    div[data-testid="column"] button {{
        background-color: #dc3545 !important;
        color: white !important;
        border: 1px solid white !important;
        height: 35px !important;
        min-width: 60px !important;
        font-size: 12px !important;
        font-weight: bold !important;
        line-height: 1 !important;
        padding: 0px 5px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# URL parametresinden mod kontrolü
params = st.query_params
mod = params.get("mod", "seyirci")

# --- MODLARA GÖRE EKRANLAR ---
if mod == "seyirci":
    # Seyirci ekranı 5 saniyede bir yenilenir (Sanatçı silince butonun yeşile dönmesi için)
    st_autorefresh(interval=5000, key="seyirci_refresh")
    
    # Gönder Butonu
    if st.button(btn_text, disabled=(kullanici_istegi is not None)):
        if "secilen_sarki" not in st.session_state or st.session_state.secilen_sarki is None:
            st.error("Lütfen önce bir seçim yapınız!")
        else:
            data["istekler"].append({"id": st.session_state.user_id, "sarki": st.session_state.secilen_sarki})
            data["aktif_kullanicilar"][st.session_state.user_id] = st.session_state.secilen_sarki
            veri_kaydet(data)
            st.rerun()

    if kullanici_istegi:
        st.warning("LÜTFEN YEŞİL BUTONU BEKLEYİNİZ")
        st.info(f"Sıradaki isteğiniz: **{kullanici_istegi}**")

    # Repertuar Listesi
    repertuar = [f"Şarkı {i}" for i in range(1, 21)] # Burayı kendi listenizle güncelleyebilirsiniz
    st.session_state.secilen_sarki = st.radio("", repertuar, index=None, label_visibility="collapsed")

    else:
    # SANATÇI EKRANI
    st_autorefresh(interval=3000, key="sanatci_refresh")
    st.markdown('<div class="istek-baslik">İSTEKLER</div>', unsafe_allow_html=True)
    
    # CSS: Satırları yan yana tutmaya zorla
    st.markdown("""
        <style>
        /* Sütunların alt alta binmesini engelle */
        [data-testid="column"] {
            width: fit-content !important;
            flex: unset !important;
            min-width: 0px !important;
        }
        /* Şarkı satırını esnek yap (Yan yana diz) */
        div.row-widget.stHorizontal {
            flex-direction: row !important;
            display: flex !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
        }
        .sarki-metni {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: 16px;
            color: #FDE992;
            margin-left: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    data = veri_yukle()
    
    for idx, item in enumerate(data["istekler"]):
        # gap='small' ile aradaki boşluğu daraltıyoruz
        col1, col2 = st.columns([1, 4], gap="small") 
        
        with col1:
            if st.button("SİL", key=f"del_{idx}"):
                u_id = item['id']
                data["istekler"].pop(idx)
                if u_id in data["aktif_kullanicilar"]:
                    del data["aktif_kullanicilar"][u_id]
                veri_kaydet(data)
                st.rerun()
        
        with col2:
            # Markdown yerine doğrudan metin yazdırarak hizayı koruyalım
            st.markdown(f'<div class="sarki-metni">{item["sarki"]}</div>', unsafe_allow_html=True)


