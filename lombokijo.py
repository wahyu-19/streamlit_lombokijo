import streamlit as st
import matplotlib.pyplot as plt
import requests
import os
from streamlit_autorefresh import st_autorefresh

# Konfigurasi
st.set_page_config(page_title="Blow n Glow", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=10_000, key="refresh")

# Styling
st.markdown("""
    <style>
    video::-webkit-media-controls {
        display: none !important;
    }
    video::-moz-media-controls {
        display: none !important;
    }
    video {
        background-color: transparent !important;
        width: 100% !important;
        height: auto !important;
    }
    body, .main, .block-container {
        background-color: white !important;
    }
    .big-title {
        font-size: 72px;
        font-weight: 900;
        margin-bottom: 0.5rem;
        color: #111;
    }
    .description {
        font-size: 28px;
        color: #333;
        margin-bottom: 2.5rem;
    }
    .metric-box {
        background-color: #4CD964;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
    .icon {
        font-size: 42px;
        margin-right: 12px;
        vertical-align: middle;
    }
    </style>
""", unsafe_allow_html=True)

# API Setup
UBIDOTS_ENDPOINT = "http://industrial.api.ubidots.com/api/v1.6/devices/esp32/"
header_ubidots = {
    "Content-Type": "application/json",
    "X-Auth-Token": "BBUS-GoISeXoa4YzzhmEgmoKUVgiv2Y3n9H"
}

# Fungsi ambil data
def get_variable_value(variable):
    try:
        url = f"{UBIDOTS_ENDPOINT}{variable}/lv"
        response = requests.get(url, headers=header_ubidots)
        return float(response.text) if response.status_code == 200 else "N/A"
    except:
        return "N/A"

def get_uv_history(limit=20):
    try:
        url = f"{UBIDOTS_ENDPOINT}uv/values?page_size={limit}"
        response = requests.get(url, headers=header_ubidots)
        results = response.json().get("results", []) if response.status_code == 200 else []
        uv_values = [item["value"] for item in results][::-1]
        labels = [f"Data {i+1}" for i in range(len(uv_values))]
        return uv_values, labels
    except:
        return [], []

# Ambil data
suhu = get_variable_value("temperature")
kelembapan = get_variable_value("humidity")
uv_data, labels = get_uv_history()

# Layout
col_left, col_right = st.columns([6, 4])

# === KIRI ===
with col_left:
    st.markdown('<div class="big-title">Blow n Glow</div>', unsafe_allow_html=True)
    st.markdown('<div class="description">Know when to reapply your sunscreen — and don\'t forget to care for the Earth while you\'re at it.</div>', unsafe_allow_html=True)

    # Pilih video
    video_file = "Animasi Dingin.mp4"  # default
    if uv_data:
        uv_now = uv_data[-1]
        if 3 <= uv_now <= 5:
            video_file = "Animasi Sedang.mp4"
        elif uv_now >= 6:
            video_file = "Animasi Panas.mp4"

    # Tampilkan video (st.video dengan autoplay loop muted pakai HTML wrapper)
    if os.path.exists(video_file):
        with open(video_file, "rb") as f:
            video_bytes = f.read()
        st.markdown(
            f"""
            <video autoplay loop muted playsinline style="width: 100%; height: auto;" id="bgvid">
                <source src="data:video/mp4;base64,{video_bytes.encode('base64').decode()}" type="video/mp4" />
            </video>
            """, unsafe_allow_html=True
        )
    else:
        st.warning(f"⚠️ Video {video_file} tidak ditemukan!")

# === KANAN ===
with col_right:
    st.markdown(f'<div class="metric-box"><span class="icon">🌡️</span>{suhu}°C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><span class="icon">💧</span>{kelembapan}%</div>', unsafe_allow_html=True)

    st.markdown("### UV Index")
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(labels, uv_data, marker='o', color='black')
    ax.set_ylim([0, 15])
    ax.set_ylabel("UV Index")
    ax.set_xlabel("Waktu")
    ax.tick_params(axis='x', rotation=45)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)
