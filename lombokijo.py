import streamlit as st
import matplotlib.pyplot as plt
import os
import requests
import pandas as pd
import time

# ----------------------------
# Konfigurasi halaman
# ----------------------------
st.set_page_config(
    page_title="Live Sensor Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------
# Styling kustom (background putih, font besar, dll.)
# ----------------------------
st.markdown("""
    <style>
    body, .main, .block-container {
        background-color: white !important;
    }
    .big-title {
        font-size: 60px;
        font-weight: 800;
        margin-bottom: 0.5rem;
        color: #111;
    }
    .description {
        font-size: 26px;
        color: #333;
        margin-bottom: 2rem;
    }
    .metric-box {
        background-color: #4CD964;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 1.2rem;
    }
    .icon {
        font-size: 42px;
        margin-right: 12px;
        vertical-align: middle;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# URL Flask API
# ----------------------------
FLASK_URL = "http://10.75.5.234:5000/latest"

# ----------------------------
# Ambil data dari API
# ----------------------------
try:
    response = requests.get(FLASK_URL)
    if response.status_code == 200:
        data = response.json()
        suhu = data.get("Temperature", "N/A")
        kelembapan = data.get("Humidity", "N/A")
        uv = data.get("UV", 0)
        uv_data = data.get("UVIndex", [uv])  # Jika ada riwayat UV
        labels = data.get("Labels", [f"Data {i+1}" for i in range(len(uv_data))])
    else:
        suhu = kelembapan = "N/A"
        uv = 0
        uv_data = [0]
        labels = ["No Data"]
except Exception as e:
    suhu = kelembapan = "N/A"
    uv = 0
    uv_data = [0]
    labels = ["No Data"]

# ----------------------------
# Layout utama: dua kolom (kiri info, kanan metrik)
# ----------------------------
col_left, col_right = st.columns([6, 4])

# ----------------------------
# Kolom KIRI: Judul dan Penjelasan
# ----------------------------
with col_left:
    st.markdown('<div class="big-title">📡 Live Sensor Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="description">Menampilkan data suhu, kelembapan, dan UV dari ESP32 secara real-time.</div>', unsafe_allow_html=True)
    
    df = pd.DataFrame([{
        "Temperature (°C)": suhu,
        "Humidity (%)": kelembapan,
        "UV (V)": uv
    }])
    st.dataframe(df, use_container_width=True)

# ----------------------------
# Kolom KANAN: Metrik & Grafik UV
# ----------------------------
with col_right:
    st.markdown(f'<div class="metric-box"><span class="icon">🌡️</span>{suhu}°C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><span class="icon">💧</span>{kelembapan}%</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><span class="icon">🌞</span>{uv:.2f} V</div>', unsafe_allow_html=True)

    st.markdown("### UV Index Over Time")
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(labels, uv_data, marker='o', color='black')
    ax.set_ylim([0, 40])
    ax.set_ylabel("UV Index")
    ax.set_title("")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)

# ----------------------------
# Informasi pembaruan
# ----------------------------
st.markdown("---")
st.caption("Data diperbarui setiap 10 detik.")

# ----------------------------
# Auto-refresh (rerun)
# ----------------------------
time.sleep(10)
st.experimental_rerun()
