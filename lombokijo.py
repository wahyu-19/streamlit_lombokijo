import streamlit as st
import matplotlib.pyplot as plt
import os
import paho.mqtt.client as mqtt

# ----------------------------
# Konfigurasi halaman
# ----------------------------
st.set_page_config(
    page_title="Blow n Glow",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------
# Styling kustom (termasuk background putih)
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
# MQTT Setup
# ----------------------------
import time

# Global variable to store temperature value
if "latest_suhu" not in st.session_state:
    st.session_state.latest_suhu = "0"

def on_message(client, userdata, msg):
    st.session_state.latest_suhu = msg.payload.decode()

# Initialize MQTT client (only once)
if "mqtt_client_initialized" not in st.session_state:
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883)
    client.subscribe("suhu/rumah")
    client.loop_start()
    st.session_state.mqtt_client_initialized = True

# ----------------------------
# Layout: 2 kolom besar (6:4)
# ----------------------------
col_left, col_right = st.columns([6, 4])

# ----------------------------
# Kolom KIRI: Judul, Deskripsi, Gambar
# ----------------------------
with col_left:
    st.markdown('<div class="big-title">Blow n Glow</div>', unsafe_allow_html=True)
    st.markdown('<div class="description">Know when to reapply your sunscreen — and don\'t forget to care for the Earth while you\'re at it.</div>', unsafe_allow_html=True)

    image_path = "Blow n Glow.png"
    if os.path.exists(image_path):
        st.image(image_path, width=500)
    else:
        st.warning(f"⚠️ Gambar tidak ditemukan di path: {image_path}")

# ----------------------------
# Kolom KANAN: Metrik + Grafik UV
# ----------------------------
with col_right:
    # Metrik suhu real-time dari MQTT
    st.markdown(f'<div class="metric-box"><span class="icon">🌡️</span> {st.session_state.latest_suhu}°C</div>', unsafe_allow_html=True)

    # Metrik kelembapan statis (atau bisa juga pakai MQTT jika tersedia)
    st.markdown('<div class="metric-box"><span class="icon">💧</span> 70%</div>', unsafe_allow_html=True)

    # Grafik UV
    st.markdown("### UV Index Over Time")
    uv_data = [18, 26, 24, 34, 36]
    labels = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]

    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(labels, uv_data, marker='o', color='black')
    ax.set_ylim([0, 40])
    ax.set_ylabel("UV Index")
    ax.set_title("")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)
