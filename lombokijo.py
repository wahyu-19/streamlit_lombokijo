import streamlit as st
import matplotlib.pyplot as plt
import requests
import os
from streamlit_autorefresh import st_autorefresh

# ----------------------------
# HARUS PALING ATAS: Konfigurasi halaman
# ----------------------------
st.set_page_config(
    page_title="Blow n Glow",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------
# Auto-refresh setiap 10 detik
# ----------------------------
st_autorefresh(interval=10_000, key="refresh")  # ✅ ganti time.sleep + rerun

# ----------------------------
# Styling kustom
# ----------------------------
st.markdown("""
    <style>
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

# ----------------------------
# Konfigurasi Ubidots
# ----------------------------
UBIDOTS_ENDPOINT = "http://industrial.api.ubidots.com/api/v1.6/devices/esp32/"
header_ubidots = {
    "Content-Type": "application/json",
    "X-Auth-Token": "BBUS-GoISeXoa4YzzhmEgmoKUVgiv2Y3n9H"
}

# ----------------------------
# Fungsi Ambil Data
# ----------------------------
def get_variable_value(variable):
    try:
        url = f"{UBIDOTS_ENDPOINT}{variable}/lv"
        response = requests.get(url, headers=header_ubidots)
        if response.status_code == 200:
            return float(response.text)
        else:
            return "N/A"
    except Exception as e:
        print("❌ Ubidots Error:", e)
        return "N/A"

def get_uv_history(limit=20):
    try:
        url = f"{UBIDOTS_ENDPOINT}uv/values?page_size={limit}"
        response = requests.get(url, headers=header_ubidots)
        if response.status_code == 200:
            results = response.json().get("results", [])
            uv_values = [item["value"] for item in results][::-1]  # dibalik biar urut
            labels = [f"Data {i+1}" for i in range(len(uv_values))]
            return uv_values, labels
        else:
            return [], []
    except Exception as e:
        print("❌ Ubidots History Error:", e)
        return [], []

# ----------------------------
# Ambil data dari Ubidots
# ----------------------------
suhu = get_variable_value("temperature")
kelembapan = get_variable_value("humidity")
uv_data, labels = get_uv_history()

# ----------------------------
# Layout: 2 kolom besar (6:4)
# ----------------------------
col_left, col_right = st.columns([6, 4])

# ----------------------------
# Kolom KIRI: Judul, Deskripsi, Video dinamis
# ----------------------------
with col_left:
    st.markdown('<div class="big-title">Blow n Glow</div>', unsafe_allow_html=True)
    st.markdown('<div class="description">Know when to reapply your sunscreen — and don\'t forget to care for the Earth while you\'re at it.</div>', unsafe_allow_html=True)

    # Pilih video berdasarkan UV index
    video_path = "Animasi Dingin.mp4"  # default

    if uv_data:
        uv_now = uv_data[-1]
        if 3 <= uv_now <= 5:
            video_path = "Animasi Sedang.mp4"
        elif uv_now >= 6:
            video_path = "Animasi Panas.mp4"

    # Tampilkan video
    if os.path.exists(video_path):
        video_html = f"""
        <video autoplay loop muted playsinline style="width: 100%; height: auto; background: none; outline: none;">
            <source src="{video_path}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        """
        st.markdown(video_html, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Video {video_path} tidak ditemukan!")

# ----------------------------
# Kolom KANAN: Metrik + Grafik UV
# ----------------------------
with col_right:
    st.markdown(f'<div class="metric-box"><span class="icon">🌡️</span>{suhu}°C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><span class="icon">💧</span>{kelembapan}%</div>', unsafe_allow_html=True)

    st.markdown("### UV Index")
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(list(labels), list(uv_data), marker='o', color='black')
    ax.set_ylim([0, 15])
    ax.set_ylabel("UV Index")
    ax.set_xlabel("Waktu")
    ax.tick_params(axis='x', rotation=45)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)
