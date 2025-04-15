import streamlit as st
import requests
import os
from streamlit_autorefresh import st_autorefresh

# ----------------------------
# Konfigurasi halaman
# ----------------------------
st.set_page_config(
    page_title="Blow n Glow",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------
# Auto-refresh
# ----------------------------
st_autorefresh(interval=10_000, key="refresh")

# ----------------------------
# Styling CSS responsif
# ----------------------------
st.markdown("""
    <style>
    /* Base styles */
    body, .main, .block-container {
        background-color: white !important;
    }
    .big-title {
        font-size: 7vw;
        font-weight: 900;
        margin-bottom: 1rem;
        color: #111;
        text-align: center;
    }
    .description {
        font-size: 1.25rem;
        color: #333;
        text-align: center;
        margin-top: -0.5rem;
        margin-bottom: 2rem;
        padding: 0 1rem;
    }
    .metric-box {
        background-color: white;
        width: 90%;
        max-width: 500px;
        height: 150px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-radius: 24px;
        color: #4CD964;
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        box-shadow: 0 0 15px rgba(76, 217, 100, 0.4);
        border: none;
        margin-left: auto;
        margin-right: auto;
    }
    .icon {
        font-size: 2rem;
        margin-right: 0.5rem;
        vertical-align: middle;
    }

    /* Responsive adjustments */
    @media screen and (max-width: 768px) {
        .big-title {
            font-size: 10vw;
        }
        .description {
            font-size: 1rem;
        }
        .metric-box {
            height: 130px;
            font-size: 1.5rem;
        }
        .icon {
            font-size: 1.75rem;
        }
    }

    @media screen and (max-width: 480px) {
        .metric-box {
            height: 120px;
            font-size: 1.25rem;
        }
        .icon {
            font-size: 1.5rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Ambil data dari Ubidots
# ----------------------------
UBIDOTS_ENDPOINT = "http://industrial.api.ubidots.com/api/v1.6/devices/esp32/"
header_ubidots = {
    "Content-Type": "application/json",
    "X-Auth-Token": "BBUS-GoISeXoa4YzzhmEgmoKUVgiv2Y3n9H"
}

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

suhu = get_variable_value("temperature")
kelembapan = get_variable_value("humidity")
uv_now = get_variable_value("uv")

# ----------------------------
# TAMPILAN UTAMA
# ----------------------------
st.markdown('<div class="big-title">Blow n Glow</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Know when to reapply your sunscreen — and don\'t forget to care for the Earth while you\'re at it.</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    image_path = ""
    if isinstance(uv_now, (int, float)):
        if uv_now <= 2:
            image_path = "Sejuk.png"
        elif 3 <= uv_now <= 5:
            image_path = "sedang.png"
        else:
            image_path = "panas banget.png"
    else:
        image_path = "Sejuk.png"
    
    if os.path.exists(image_path):
        st.image(image_path, use_column_width=True)
    else:
        st.warning("⚠️ Gambar tidak ditemukan!")

with col2:
    st.markdown(f'<div class="metric-box"><div class="icon">🌡️</div>{suhu}°C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><div class="icon">💧</div>{kelembapan}%</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><div class="icon">☀️</div>{uv_now}</div>', unsafe_allow_html=True)
