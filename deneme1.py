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
btn_color = "#dc3545" if kullanici_istegi else "#28a745"
btn_text = "İSTEK İLETİLDİ" if kullanici_istegi else "İSTEK GÖNDER"

# --- GENEL CSS VE JAVASCRIPT ---
st.markdown(f"""
    <style>
    .block-container {{ padding-top: 3rem !important; }}
    .stButton>button {{
        width: 100%; background-color: {btn_color} !important;
        color: white !important; font-weight: bold !important;
        height: 60px; font-size: 22px; border-radius: 10px;
    }}
    .istek-baslik {{
        background-color: #FDE992; color: black; text-align: center;
        font-weight: bold; padding: 10px; border: 2px solid #1d3311; margin-bottom: 20px;
    }}
    .sarki-satiri {{
        padding: 12px;
        margin-bottom: 5px;
        background-color: #1d3311;
        border-radius: 5px;
        color: #FDE992;
        font-size: 18px;
        cursor: pointer;
        user-select: none; /* Metnin seçilmesini engeller, tıklamayı kolaylaştırır */
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .sarki-satiri:hover {{ background-color: #2a4a18; }}
    </style>
    """, unsafe_allow_html=True)

params = st.query_params
mod = params.get("mod", "seyirci")

# --- SEYİRCİ EKRANI ---
if mod == "seyirci":
    st_autorefresh(interval=5000, key="seyirci_refresh")
    
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
    
    repertuar = [f"Şarkı {i}" for i in range(1, 21)]
    st.session_state.secilen_sarki = st.radio("", repertuar, index=None, label_visibility="collapsed")

# --- SANATÇI EKRANI ---
else:
    st_autorefresh(interval=3000, key="sanatci_refresh")
    st.markdown('<div class="istek-baslik">İSTEKLER</div>', unsafe_allow_html=True)
    
    data = veri_yukle()
    
    for idx, item in enumerate(data["istekler"]):
        # Şarkı ismini bir div içinde gösteriyoruz. 
        # Çift tıklandığında (ondblclick) Streamlit'in butonuna basılmış gibi davranacak.
        st.markdown(f'''
            <div class="sarki-satiri" 
                 id="sarki_{idx}" 
                 ondblclick="document.getElementById('hidden_btn_{idx}').click();">
                {item["sarki"]}
            </div>
        ''', unsafe_allow_html=True)
        
        # Gizli Buton: JavaScript bunu tetikleyecek
        if st.button(f"Sil_{idx}", key=f"hidden_btn_{idx}", help="Görünmez silme butonu"):
            u_id = item['id']
            data["istekler"].pop(idx)
            if u_id in data["aktif_kullanicilar"]:
                del data["aktif_kullanicilar"][u_id]
            veri_kaydet(data)
            st.rerun()
            
        # Gizli butonu CSS ile tamamen saklıyoruz
        st.markdown(f"""
            <style>
            div[data-testid="stButton"] {{ display: none; }} 
            /* Sadece sanatçı modunda butonları gizle */
            </style>
            """, unsafe_allow_html=True)


