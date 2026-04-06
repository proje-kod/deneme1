import streamlit as st
import json
import os
from streamlit_autorefresh import st_autorefresh

# Veritabanı dosyası
DB_FILE = "istekler.json"

def veri_yukle():
    if not os.path.exists(DB_FILE):
        return {"istekler": [], "aktif_kullanicilar": {}}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"istekler": [], "aktif_kullanicilar": {}}

def veri_kaydet(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# Sayfa Ayarları
st.set_page_config(page_title="Sahne İstek Paneli", layout="wide")

# Kullanıcı Kimliği (Session ID)
if 'user_id' not in st.session_state:
    import uuid
    st.session_state.user_id = str(uuid.uuid4())

# Sidebar'da Rol Seçimi
rol = st.sidebar.radio("Ekran Seçimi:", ["Seyirci", "Sanatçı"])

# --- SEYİRCİ EKRANI ---
if rol == "Seyirci":
    st.markdown("<h2 style='text-align: center; background-color:#FDE992; color:black; padding:10px;'>İSTEK GÖNDER</h2>", unsafe_allow_html=True)
    
    repertuar = ["Şarkı 1", "Şarkı 2", "Şarkı 3", "Şarkı 4", "Şarkı 5", "Şarkı 6", "Şarkı 7"]
    
    data = veri_yukle()
    kullanici_istegi = data["aktif_kullanicilar"].get(st.session_state.user_id)

    # Seçim Alanı
    secilen_sarki = st.radio("Lütfen bir şarkı seçiniz:", repertuar, index=None)
    
    # Buton Durumu Kontrolü
    buton_pasif = kullanici_istegi is not None

    if st.button("GÖNDER", use_container_width=True, disabled=buton_pasif):
        if not secilen_sarki:
            st.error("Lütfen önce bir seçim yapınız!")
        else:
            data["istekler"].append({"id": st.session_state.user_id, "sarki": secilen_sarki})
            data["aktif_kullanicilar"][st.session_state.user_id] = secilen_sarki
            veri_kaydet(data)
            st.success(f"'{secilen_sarki}' isteğiniz sanatçıya iletildi!")
            st.rerun()
            
    if buton_pasif:
        st.info(f"İsteğiniz iletildi: **{kullanici_istegi}**. Sanatçı şarkınızı çaldığında yeni bir istek gönderebilirsiniz.")

# --- SANATÇI EKRANI ---
else:
    # 1. Aşama: Şifre Kontrolü
    st.markdown("### Sanatçı Paneli Girişi")
    sifre = st.text_input("Giriş Şifresi:", type="password")
    
    # Sizin belirlediğiniz özel şifre (Örn: Hüzzam2026)
    if sifre == "Hüzzam2026":
        st.success("Giriş Başarılı!")
        
        # Ekranı ikiye bölüyoruz: Sol (Boş/Asıl Uygulama Alanı), Sağ (İstek Listesi)
        col_sol, col_sag = st.columns([3, 1])
        
        with col_sag:
            st_autorefresh(interval=3000, key="sanatci_refresh") # 3 saniyede bir yeniler
            st.markdown("<div style='background-color:#FDE992; padding:10px; text-align:center; font-weight:bold; color:black;'>İSTEKLER</div>", unsafe_allow_html=True)
            
            data = veri_yukle()
            
            if not data["istekler"]:
                st.write("Henüz istek yok...")
            
            # İstekleri Listeleyelim
            for idx, item in enumerate(data["istekler"]):
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{item['sarki']}**")
                # "Çalındı/Sil" Butonu
                if c2.button("❌", key=f"sil_{idx}"):
                    user_id = item['id']
                    data["istekler"].pop(idx)
                    # Seyircinin engelini kaldır
                    if user_id in data["aktif_kullanicilar"]:
                        del data["aktif_kullanicilar"][user_id]
                    veri_kaydet(data)
                    st.rerun()
    elif sifre != "":
        st.error("Hatalı şifre! Lütfen tekrar deneyiniz.")

