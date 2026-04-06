import streamlit as st
import json
import os
from streamlit_autorefresh import st_autorefresh

# Veri tabanı dosyası (Basit bir JSON)
DB_FILE = "istekler.json"

def veri_yukle():
    if not os.path.exists(DB_FILE):
        return {"istekler": [], "aktif_kullanicilar": {}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def veri_kaydet(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# Sayfa Yapılandırması
st.set_page_config(page_title="Sahne İstek", layout="wide")

# URL'den kimlik al (Seyirciyi tanımak için)
if 'user_id' not in st.session_state:
    import uuid
    st.session_state.user_id = str(uuid.uuid4())

# Arayüz Seçimi (Bunu URL parametresiyle de yapabiliriz: ?rol=sanatci)
rol = st.sidebar.radio("Ekran Seçin:", ["Seyirci", "Sanatçı"])

# --- SEYİRCİ EKRANI ---
if rol == "Seyirci":
    st.title("🎵 İSTEK GÖNDER")
    repertuar = ["Şarkı 1", "Şarkı 2", "Şarkı 3", "Şarkı 4", "Şarkı 5"]
    
    data = veri_yukle()
    kullanici_istegi = data["aktif_kullanicilar"].get(st.session_state.user_id)

    secilen_sarki = st.radio("Repertuar Listesi:", repertuar, index=None)
    
    # Buton Durumu: Eğer kullanıcının henüz çalınmamış bir isteği varsa buton pasif olur
    buton_pasif = kullanici_istegi is not None

    if st.button("GÖNDER", disabled=buton_pasif):
        if not secilen_sarki:
            st.error("Lütfen önce bir seçim yapınız!")
        else:
            data["istekler"].append({"id": st.session_state.user_id, "sarki": secilen_sarki})
            data["aktif_kullanicilar"][st.session_state.user_id] = secilen_sarki
            veri_kaydet(data)
            st.success(f"'{secilen_sarki}' sıraya alındı!")
            st.rerun()
            
    if buton_pasif:
        st.info(f"İsteğiniz iletildi: **{kullanici_istegi}**. Sanatçı çaldığında tekrar isteyebilirsiniz.")

# --- SANATÇI EKRANI ---
else:
    # Ekranın sağ tarafında dikey sütun olması için sağa yaslıyoruz
    st_autorefresh(interval=3000, key="datarefresh") # 3 saniyede bir yeniler
    
    col1, col2 = st.columns([3, 1]) # Sol taraf (Asıl uygulamanız için), Sağ taraf (İstekler)
    
    with col2:
        st.markdown("<div style='background-color:#FDE992; padding:10px; text-align:center; font-weight:bold; color:black; border-radius:5px;'>İSTEKLER</div>", unsafe_allow_html=True)
        
        data = veri_yukle()
        
        for idx, item in enumerate(data["istekler"]):
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{item['sarki']}**")
            if c2.button("Sil", key=f"sil_{idx}"):
                # Listeden sil ve kullanıcının engelini kaldır
                user_id = item['id']
                data["istekler"].pop(idx)
                if user_id in data["aktif_kullanicilar"]:
                    del data["aktif_kullanicilar"][user_id]
                veri_kaydet(data)
                st.rerun()
