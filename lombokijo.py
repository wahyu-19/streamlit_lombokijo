import streamlit as st
import requests
import os
import base64
import pandas as pd
import matplotlib.pyplot as plt
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
    html, body, .main, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        background-color: white !important;
        overflow-x: hidden;
    }
    .big-title {
        font-size: 64px;
        font-weight: 900;
        color: #111;
        margin-bottom: 0.25rem;
        text-align: center;
    }
    .description {
        font-size: 18px;
        color: #333;
        margin-top: -5px;
        margin-bottom: 2rem;
        text-align: center;
        padding: 0 10px;
    }
    .metric-box {
        background-color: white;
        width: 100%;
        max-width: 300px;
        height: 140px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-radius: 24px;
        color: #4CD964;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 1rem;
        box-shadow: 0 0 15px rgba(76, 217, 100, 0.4);
        border: none;
        margin-left: auto;
        margin-right: auto;
    }
    .icon {
        font-size: 36px;
        margin-bottom: 8px;
    }

    @media (max-width: 768px) {
        .big-title {
            font-size: 42px;
        }
        .description {
            font-size: 16px;
        }
        .metric-box {
            height: 120px;
            font-size: 22px;
        }
        .icon {
            font-size: 30px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Ambil data dari Ubidots
# ----------------------------
UBIDOTS_DEVICE = "esp32"
UBIDOTS_TOKEN = "BBUS-GoISeXoa4YzzhmEgmoKUVgiv2Y3n9H"
UBIDOTS_ENDPOINT = f"http://industrial.api.ubidots.com/api/v1.6/devices/{UBIDOTS_DEVICE}/"
HEADERS = {
    "Content-Type": "application/json",
    "X-Auth-Token": UBIDOTS_TOKEN
}

def get_latest_value(variable):
    try:
        url = f"{UBIDOTS_ENDPOINT}{variable}/lv"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return float(response.text)
        else:
            return "N/A"
    except Exception as e:
        print("❌ Latest Value Error:", e)
        return "N/A"

def get_historical_values(variable, limit=30):
    try:
        url = f"{UBIDOTS_ENDPOINT}{variable}/values?limit={limit}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()["results"]
            df = pd.DataFrame(data)
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        print("❌ Historical Value Error:", e)
        return pd.DataFrame()

# ----------------------------
# Ambil nilai terbaru dan historis
# ----------------------------
suhu = get_latest_value("temperature")
kelembapan = get_latest_value("humidity")
uv_now = get_latest_value("uv")
uv_hist = get_historical_values("uv", limit=24)  # Ambil 24 data terakhir

if isinstance(suhu, (int, float)):
    suhu = f"{suhu:.2f}"
if isinstance(kelembapan, (int, float)):
    kelembapan = f"{kelembapan:.2f}"
if isinstance(uv_now, (int, float)):
    uv_now = f"{uv_now:.2f}"

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
        with open(image_path, "rb") as img_file:
            b64_image = base64.b64encode(img_file.read()).decode()

        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="data:image/png;base64,{b64_image}" width="450"/>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("⚠️ Gambar tidak ditemukan!")

    # Grafik UV historis
    if not uv_hist.empty:
        st.subheader("Grafik Tren UV (24 Data Terakhir)")
        fig, ax = plt.subplots()
        ax.plot(uv_hist["timestamp"], uv_hist["value"], marker='o', color="#f39c12")
        ax.set_xlabel("Waktu")
        ax.set_ylabel("Indeks UV")
        ax.set_title("Perubahan Indeks UV")
        ax.grid(True)
        fig.autofmt_xdate()
        st.pyplot(fig)
    else:
        st.warning("⚠️ Data historis UV tidak tersedia.")

with col2:
    # Format nilai UV ke dua angka di belakang koma jika berupa angka
    formatted_uv = f"{uv_now:.2f}" if isinstance(uv_now, (int, float)) else uv_now
    formatted_suhu = f"{suhu:.1f}" if isinstance(suhu, (int, float)) else suhu
    formatted_kelembapan = f"{kelembapan:.1f}" if isinstance(kelembapan, (int, float)) else kelembapan

    st.markdown(f'<div class="metric-box"><div class="icon">🌡️</div>{formatted_suhu}°C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><div class="icon">💧</div>{formatted_kelembapan}%</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><div class="icon">☀️</div>{formatted_uv}</div>', unsafe_allow_html=True)
