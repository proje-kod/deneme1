import streamlit as st

st.title("Merhaba Dünya!")
st.write("Eğer bu yazıyı telefonda görüyorsanız bağlantı başarılı demektir.")

if st.button("Tıkla"):
    st.balloons() # Ekranın altında balonlar uçar, test için eğlencelidir.
