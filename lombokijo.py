import streamlit as st
import matplotlib.pyplot as plt
import os

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
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    .icon {
        font-size: 40px;
        margin-right: 12px;
        vertical-align: middle;
    }
    </style>
""", unsafe_allow_html=True)

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
        st.image(image_path, width=450)  # Ukuran lebih besar dan proporsional
    else:
        st.warning(f"⚠️ Gambar tidak ditemukan di path: {image_path}")

# ----------------------------
# Kolom KANAN: Metrik + Grafik UV
# ----------------------------
with col_right:
    st.markdown('<div class="metric-box"><span class="icon">🌡️</span> 30°C</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-box"><span class="icon">💧%</span> 70 %</div>', unsafe_allow_html=True)

    st.markdown("### UV Index Over Time")
    uv_data = [18, 26, 24, 34, 36]
    labels = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]

    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.plot(labels, uv_data, marker='o', color='black')
    ax.set_ylim([0, 40])
    ax.set_title("")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)
