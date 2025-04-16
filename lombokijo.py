import streamlit as st
import requests
import os
import base64
import pandas as pd
from datetime import datetime
import pytz
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
st_autorefresh(interval=60_000, key="refresh")

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

    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }

    .blink-time {
        animation: blink 1s infinite;
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

def get_historical_data(variable, limit=20):
    try:
        url = f"{UBIDOTS_ENDPOINT}{variable}/values?limit={limit}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            raw_data = response.json()["results"]
            df = pd.DataFrame(raw_data)
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms").dt.tz_localize("UTC").dt.tz_convert("Asia/Jakarta")
            df = df[["timestamp", "value"]].rename(columns={"timestamp": "Waktu", "value": variable.capitalize()})
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ Historical Data Error ({variable}):", e)
        return pd.DataFrame()

# ----------------------------
# Ambil nilai sensor terbaru
# ----------------------------
suhu = get_latest_value("temperature")
kelembapan = get_latest_value("humidity")
uv_now = get_latest_value("uv")

# ----------------------------
# Ambil data historis
# ----------------------------
df_suhu = get_historical_data("temperature")
df_kelembapan = get_historical_data("humidity")
df_uv = get_historical_data("uv")

# ----------------------------
# Waktu Sekarang (WIB)
# ----------------------------
wib = pytz.timezone('Asia/Jakarta')
tanggal = datetime.now(wib).strftime("%d %B %Y")
jam = datetime.now(wib).strftime("%H:%M:%S")


# ----------------------------
# TAMPILAN UTAMA
# ----------------------------
st.markdown('<div class="big-title">Blow n Glow</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Know when to reapply your sunscreen — and don\'t forget to care for the Earth while you\'re at it.</div>', unsafe_allow_html=True)

# 👉 Jam digital WIB
st.markdown(
    f'''
    <div style="
        text-align: center;
        font-size: 22px;
        font-weight: 600;
        color: #444;
        margin-top: -10px;
        margin-bottom: 20px;
        font-family: 'Courier New', monospace;
        line-height: 1.6;
    ">
        🕒<br>{tanggal}<br><span class="blink-time">{jam}</span>
    </div>
    ''',
    unsafe_allow_html=True
)

col1, col2 = st.columns([1, 1])

with col1:
    image_path = ""
    if isinstance(uv_now, (int, float)):
        if uv_now <= 2:
            image_path = "Sejuk.png"
        elif 3 <= uv_now <= 5:
            image_path = "Sedang.png"
        else:
            image_path = "Panas banget.png"
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

with col2:
    formatted_uv = f"{uv_now:.2f}" if isinstance(uv_now, (int, float)) else uv_now
    formatted_suhu = f"{suhu:.1f}" if isinstance(suhu, (int, float)) else suhu
    formatted_kelembapan = f"{kelembapan:.1f}" if isinstance(kelembapan, (int, float)) else kelembapan

    st.markdown(f'<div class="metric-box"><div class="icon">🌡️</div>{formatted_suhu}°C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><div class="icon">💧</div>{formatted_kelembapan}%</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><div class="icon">☀️</div>{formatted_uv}</div>', unsafe_allow_html=True)


# ----------------------------
# Grafik Historis Sensor (4 data terakhir)
# ----------------------------
st.markdown("<hr style='margin:30px 0;'>", unsafe_allow_html=True)
st.markdown("<div class='big-title' style='font-size:32px;'>📈 Grafik Sensor</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if not df_suhu.empty:
        st.line_chart(df_suhu.tail(4).set_index("Waktu"))
    else:
        st.warning("Data suhu tidak tersedia.")

with col2:
    if not df_kelembapan.empty:
        st.line_chart(df_kelembapan.tail(4).set_index("Waktu"))
    else:
        st.warning("Data kelembapan tidak tersedia.")

with col3:
    if not df_uv.empty:
        st.line_chart(df_uv.tail(4).set_index("Waktu"))
    else:
        st.warning("Data UV tidak tersedia.")
