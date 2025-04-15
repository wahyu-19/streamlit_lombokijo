import streamlit as st
import requests
import os
import base64
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
from io import BytesIO

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

def get_historical_values(variable, limit=24):
    try:
        url = f"{UBIDOTS_ENDPOINT}{variable}/values?limit={limit}&order=desc"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()["results"]
            df = pd.DataFrame(data)
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df = df.sort_values("timestamp")  # urutkan dari lama ke baru
            return df
        else:
            st.error("❌ Gagal mengambil data historis.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error mengambil histori: {e}")
        return pd.DataFrame()

# ----------------------------
# Ambil nilai terbaru dan historis
# ----------------------------
suhu = get_latest_value("temperature")
kelembapan = get_latest_value("humidity")
uv_now = get_latest_value("uv")
uv_hist = get_historical_values("uv", limit=24)

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

    if not uv_hist.empty:
        st.subheader("Grafik Tren UV (24 Titik Terakhir)")

        max_uv = uv_hist["value"].max()
        min_uv = uv_hist["value"].min()
        max_time = uv_hist.loc[uv_hist["value"].idxmax(), "timestamp"]
        min_time = uv_hist.loc[uv_hist["value"].idxmin(), "timestamp"]

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(uv_hist["timestamp"], uv_hist["value"], marker='o', color="#f39c12", linewidth=2, label='Indeks UV')
        ax.fill_between(uv_hist["timestamp"], uv_hist["value"], color="#f39c12", alpha=0.1)

        ax.set_xlabel("Waktu", fontsize=10)
        ax.set_ylabel("Indeks UV", fontsize=10)
        ax.set_title("Perubahan Indeks UV", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)

        ax.annotate(f'Max: {max_uv:.1f}', xy=(max_time, max_uv),
                    xytext=(0, 15), textcoords="offset points",
                    ha='center', color="red", fontsize=9,
                    arrowprops=dict(arrowstyle="->", color="red"))

        ax.annotate(f'Min: {min_uv:.1f}', xy=(min_time, min_uv),
                    xytext=(0, -20), textcoords="offset points",
                    ha='center', color="blue", fontsize=9,
                    arrowprops=dict(arrowstyle="->", color="blue"))

        fig.autofmt_xdate(rotation=45)
        st.pyplot(fig)

        # Tambahkan tombol download
        csv = uv_hist.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download UV Data (CSV)",
            data=csv,
            file_name="uv_data.csv",
            mime="text/csv"
        )

    else:
        st.warning("⚠️ Data historis UV tidak tersedia.")


with col2:
    st.markdown(f'<div class="metric-box"><div class="icon">🌡️</div>{suhu}°C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><div class="icon">💧</div>{kelembapan}%</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box"><div class="icon">☀️</div>{uv_now}</div>', unsafe_allow_html=True)

    # Tampilkan info risiko UV
    def get_uv_risk_info(uv_value):
        if uv_value == "N/A":
            return "Data UV tidak tersedia."
        elif uv_value <= 2:
            return "🌤️ Rendah – Aman untuk aktivitas luar ruangan."
        elif 3 <= uv_value <= 5:
            return "🌥️ Sedang – Gunakan sunscreen saat beraktivitas di luar."
        elif 6 <= uv_value <= 7:
            return "☀️ Tinggi – Gunakan pelindung, hindari sinar matahari langsung."
        elif 8 <= uv_value <= 10:
            return "🔥 Sangat Tinggi – Hindari keluar ruangan terlalu lama!"
        else:
            return "☠️ Ekstrem – Tetap di dalam ruangan jika memungkinkan."

    if isinstance(uv_now, (int, float)):
        risk_message = get_uv_risk_info(uv_now)
        st.markdown(f"<p style='text-align:center; font-size:16px; color:#f39c12; font-weight:bold'>{risk_message}</p>", unsafe_allow_html=True)

