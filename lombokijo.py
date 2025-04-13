import streamlit as st
import matplotlib.pyplot as plt
import os
import json
from collections import deque
import threading
import paho.mqtt.client as mqtt
from streamlit_autorefresh import st_autorefresh  # ✅ tambahan

# ----------------------------
# Auto-refresh setiap 10 detik
# ----------------------------
st_autorefresh(interval=10_000, key="refresh")  # ✅ ganti time.sleep + rerun

# ----------------------------
# Buffer data untuk grafik
# ----------------------------
uv_data = deque(maxlen=20)
labels = deque(maxlen=20)
suhu = kelembapan = "N/A"

# ----------------------------
# Konfigurasi halaman
# ----------------------------
st.set_page_config(
    page_title="Blow n Glow",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
# Fungsi Callback MQTT
# ----------------------------
def on_message(client, userdata, msg):
    global suhu, kelembapan
    try:
        data = json.loads(msg.payload.decode())
        suhu = data.get("temperature", "N/A")
        kelembapan = data.get("humidity", "N/A")
        uv = data.get("uv", 0)
        uv_data.append(uv)
        labels.append(f"Data {len(uv_data)}")
    except Exception as e:
        print("❌ MQTT Error:", e)

# ----------------------------
# Setup MQTT Client
# ----------------------------
def start_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("broker.mqtt-dashboard.com", 1883, 60)
    client.subscribe("tugas/sic6/stage3")
    client.loop_forever()

# Jalankan MQTT di thread terpisah agar tidak memblokir UI Streamlit
if "mqtt_started" not in st.session_state:
    threading.Thread(target=start_mqtt, daemon=True).start()
    st.session_state["mqtt_started"] = True  # ✅ agar thread tidak dobel saat refresh

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
        st.warning("⚠️ Gambar tidak ditemukan!")

# ----------------------------
# Kolom KANAN: Metrik + Grafik UV
# ----------------------------
with col_right:
    st.markdown(f'<div class="metric-box"><span class="icon">🌡️</span>{suhu}°C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><span class="icon">💧</span>{kelembapan}%</div>', unsafe_allow_html=True)

    st.markdown("### UV Index Over Time")
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(list(labels), list(uv_data), marker='o', color='black')
    ax.set_ylim([0, 40])
    ax.set_ylabel("UV Index")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)
