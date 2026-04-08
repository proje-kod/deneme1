# --- SANATÇI EKRANI ---
else:
    st_autorefresh(interval=3000, key="sanatci_refresh")
    st.markdown('<div class="istek-baslik">İSTEKLER</div>', unsafe_allow_html=True)
    
    # CSS'i daha spesifik ve sağlam hale getirdik
    st.markdown("""
        <style>
        .sarki-container {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            gap: 10px;
        }
        .sarki-metni {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: 16px;
            color: #FDE992; /* Daha okunaklı bir sarı tonu */
            flex-grow: 1;
        }
        /* SİL butonunun içindeki yazının görünmesi için zorlama */
        div[data-testid="column"] button {
            background-color: #dc3545 !important;
            color: white !important;
            border: 1px solid white !important;
            height: 35px !important;
            min-width: 50px !important;
            font-size: 12px !important;
            font-weight: bold !important;
            line-height: 1 !important;
            padding: 0px 5px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    data = veri_yukle()
    
    # İstekleri listeleyelim
    for idx, item in enumerate(data["istekler"]):
        # Sütun oranlarını biraz daha optimize ettik
        col1, col2 = st.columns([0.8, 3.2]) 
        
        # SİL Butonu (Sol Başta)
        with col1:
            if st.button("SİL", key=f"del_{idx}"):
                u_id = item['id']
                data["istekler"].pop(idx)
                if u_id in data["aktif_kullanicilar"]:
                    del data["aktif_kullanicilar"][u_id]
                veri_kaydet(data)
                st.rerun()
            
        # Şarkı Adı (Sağda)
        with col2:
            st.markdown(f'<div class="sarki-metni">{item["sarki"]}</div>', unsafe_allow_html=True)


