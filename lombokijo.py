import streamlit as st
import requests
import os
import base64
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objs as go
from datetime import datetime

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
        # Encode gambar ke base64
        with open(image_path, "rb") as img_file:
            b64_image = base64.b64encode(img_file.read()).decode()

        # Tampilkan dengan HTML dan align center
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
    st.markdown(f'<div class="metric-box"><div class="icon">🌡️</div>{suhu}°C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><div class="icon">💧</div>{kelembapan}%</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><div class="icon">☀️</div>{uv_now}</div>', unsafe_allow_html=True)

import pandas as pd
import plotly.express as px

# Fungsi ambil data historis
def get_variable_series(variable, limit=20):
    try:
        url = f"{UBIDOTS_ENDPOINT}{variable}/values?limit={limit}"
        response = requests.get(url, headers=header_ubidots)
        if response.status_code == 200:
            data = response.json().get('results', [])
            df = pd.DataFrame(data)
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['value'] = df['value'].astype(float)
            return df[['datetime', 'value']]
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error fetching {variable}: {e}")
        return pd.DataFrame()

# Ambil data historis
df_temp = get_variable_series("temperature")
df_humid = get_variable_series("humidity")
df_uv = get_variable_series("uv")

# Tampilkan grafik
st.markdown("<h3 style='text-align: center;'>📊 Trend Cuaca Terkini</h3>", unsafe_allow_html=True)

col3, col4, col5 = st.columns(3)

with col3:
    if not df_temp.empty:
        fig = px.line(df_temp, x='datetime', y='value', title='Suhu (°C)', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Data suhu tidak tersedia.")

with col4:
    if not df_humid.empty:
        fig = px.line(df_humid, x='datetime', y='value', title='Kelembapan (%)', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Data kelembapan tidak tersedia.")

with col5:
    if not df_uv.empty:
        fig = px.line(df_uv, x='datetime', y='value', title='Intensitas UV', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Data UV tidak tersedia.")

