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

st.set_page_config(page_title="Sahne", layout="centered")

# Oturum Kimliği
if 'user_id' not in st.session_state:
    import uuid
    st.session_state.user_id = str(uuid.uuid4())

data = veri_yukle()
kullanici_istegi = data["aktif_kullanicilar"].get(st.session_state.user_id)

# DURUMA GÖRE RENK VE METİN BELİRLEME
btn_color = "#dc3545" if kullanici_istegi else "#28a745" # Kırmızı : Yeşil
btn_text = "İSTEK İLETİLDİ" if kullanici_istegi else "İSTEK GÖNDER"

st.markdown(f"""
    <style>
    /* Butonun üstten kesilmemesi için konteyner ayarı */
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
        margin-top: 10px; /* Butonu biraz daha aşağı iter */
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
    </style>
    """, unsafe_allow_html=True)

params = st.query_params
mod = params.get("mod", "seyirci")

# --- SEYİRCİ EKRANI ---
if mod == "seyirci":
    # Seyirci ekranı da 5 saniyede bir kontrol etsin ki buton yeşile dönebilsin
    st_autorefresh(interval=5000, key="seyirci_refresh")
    
    # İSTEK GÖNDER / İSTEK İLETİLDİ BUTONU
    if st.button(btn_text, disabled=(kullanici_istegi is not None)):
        if "secilen_sarki" not in st.session_state or st.session_state.secilen_sarki is None:
            st.error("Lütfen önce bir seçim yapınız!")
        else:
            data["istekler"].append({"id": st.session_state.user_id, "sarki": st.session_state.secilen_sarki})
            data["aktif_kullanicilar"][st.session_state.user_id] = st.session_state.secilen_sarki
            veri_kaydet(data)
            st.rerun()

    # Eğer seyirci zaten bir istek göndermişse bu mesajı görsün
    if kullanici_istegi:
        st.warning("LÜTFEN YEŞİL BUTONU BEKLEYİNİZ")
        st.info(f"Sıradaki isteğiniz: **{kullanici_istegi}**")

    # REPERTUAR LİSTESİ
    repertuar = [f"Şarkı {i}" for i in range(1, 21)]
    st.session_state.secilen_sarki = st.radio("", repertuar, index=None, label_visibility="collapsed")

# --- SANATÇI EKRANI ---
else:
    st_autorefresh(interval=3000, key="sanatci_refresh")
    st.markdown('<div class="istek-baslik">İSTEKLER</div>', unsafe_allow_html=True)
    
    # CSS ile metinlerin taşmasını engelliyoruz ve SİL butonunu özelleştiriyoruz
    st.markdown("""
        <style>
        .sarki-metni {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            display: block;
            font-size: 16px;
            color: white;
            padding-top: 5px;
        }
        /* SİL butonunu daha küçük ve kırmızı yapalım */
        div[data-testid="column"] button {
            background-color: #dc3545 !important;
            color: white !important;
            height: 35px !important;
            font-size: 14px !important;
            padding: 0px !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    data = veri_yukle()
    
    for idx, item in enumerate(data["istekler"]):
        # SİL butonunu sol başa (1. sütun) alıyoruz, şarkıyı sağa (2. sütun)
        col1, col2 = st.columns([1.2, 4]) 
        
        # SİL Butonu (Sol Başta)
        if col1.button("SİL", key=f"del_{idx}"):
            u_id = item['id']
            data["istekler"].pop(idx)
            if u_id in data["aktif_kullanicilar"]:
                del data["aktif_kullanicilar"][u_id]
            veri_kaydet(data)
            st.rerun()
            
        # Şarkı Adı (Sağda ve Kesilebilir)
        # HTML 'ellipsis' sayesinde uzun isimler 'Akşam oldu hüzünlend...' şeklinde görünür
        col2.markdown(f'<span class="sarki-metni">{item["sarki"]}</span>', unsafe_allow_html=True)


