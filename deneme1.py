import streamlit as st
import json
import os
from streamlit_autorefresh import st_autorefresh

# --- VERİTABANI İŞLEMLERİ ---
DB_FILE = "istekler.json"

def veri_yukle():
    if not os.path.exists(DB_FILE): return {"istekler": [], "aktif_kullanicilar": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {"istekler": [], "aktif_kullanicilar": {}}

def veri_kaydet(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False)

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Sahne İstek", layout="centered")

if 'user_id' not in st.session_state:
    import uuid
    st.session_state.user_id = str(uuid.uuid4())

data = veri_yukle()
kullanici_istegi = data["aktif_kullanicilar"].get(st.session_state.user_id)

# --- TASARIM (CSS) ---
st.markdown(f"""
    <style>
    .block-container {{ padding-top: 2rem !important; }}
    .istek-baslik {{
        background-color: #FDE992; color: black; text-align: center;
        font-weight: bold; padding: 10px; border: 2px solid #1d3311; margin-bottom: 20px;
    }}
    /* Sanatçı Listesi Yazı Tipi */
    .stCheckbox label p {{
        font-size: 18px !important;
        color: 	#000000 !important;
        font-weight: bold;
    }}
    /* Onay kutusunu biraz büyütelim */
    .stCheckbox div[data-testid="stMarkdownContainer"] {{
        margin-top: -2px;
    }}
    </style>
    """, unsafe_allow_html=True)

params = st.query_params
mod = params.get("mod", "seyirci")

# --- SEYİRCİ EKRANI ---
if mod == "seyirci":
    st_autorefresh(interval=5000, key="seyirci_refresh")
    
    # Buton Renk Ayarı
    btn_color = "#dc3545" if kullanici_istegi else "#28a745"
    btn_text = "İSTEK GÖNDERİLDİ" if kullanici_istegi else "İSTEK GÖNDER"
    
    st.markdown(f"<style>.stButton>button {{ background-color: {btn_color} !important; color: white !important; width:100%; height:60px; font-size:22px; border-radius:10px; }}</style>", unsafe_allow_html=True)

    if st.button(btn_text, disabled=(kullanici_istegi is not None)):
        if "secilen_sarki" not in st.session_state or st.session_state.secilen_sarki is None:
            st.error("Lütfen önce bir seçim yapınız!")
        else:
            data["istekler"].append({"id": st.session_state.user_id, "sarki": st.session_state.secilen_sarki})
            data["aktif_kullanicilar"][st.session_state.user_id] = st.session_state.secilen_sarki
            veri_kaydet(data)
            st.rerun()

    if kullanici_istegi:
        st.warning(f"YEŞİL BUTONU BEKLEYİNİZ\n\nGönderdiğiniz: {kullanici_istegi}")
    
    # --- REPERTUAR YÜKLEME ---
def repertuar_yukle():
    if os.path.exists("denemelistesi.txt"):
        with open("denemelistesi.txt", "r", encoding="utf-8") as f:
            # Boş satırları temizleyerek listeye alıyoruz
            return [line.strip() for line in f.readlines() if line.strip()]
    else:
        # Eğer dosya yoksa hata vermemesi için örnek bir liste döndürelim
        return ["Repertuar dosyası bulunamadı!"]

    repertuar = repertuar_yukle()
    st.session_state.secilen_sarki = st.radio("", repertuar, index=None, label_visibility="collapsed")

# --- SANATÇI EKRANI ---
else:
    st_autorefresh(interval=3000, key="sanatci_refresh")
    st.markdown('<div class="istek-baslik">İSTEKLER</div>', unsafe_allow_html=True)
    
    data = veri_yukle()
    
    # İstekleri işaretleme kutusu (checkbox) olarak gösteriyoruz
    for idx, item in enumerate(data["istekler"]):
        # Checkbox işaretlendiği anda (True olduğunda) silme işlemi tetiklenir
        if st.checkbox(f"{item['sarki']}", key=f"check_{idx}"):
            u_id = item['id']
            data["istekler"].pop(idx)
            if u_id in data["aktif_kullanicilar"]:
                del data["aktif_kullanicilar"][u_id]
            veri_kaydet(data)
            st.rerun()


