import streamlit as st
import matplotlib.pyplot as plt
from collections import deque
import threading
import paho.mqtt.client as mqtt
import json

# ----------------------------
# Buffer data
# ----------------------------
temp1_data = deque(maxlen=20)
temp2_data = deque(maxlen=20)
hum1_data = deque(maxlen=20)
hum2_data = deque(maxlen=20)
labels = deque(maxlen=20)

latest_temp1 = latest_temp2 = "N/A"
latest_hum1 = latest_hum2 = "N/A"

# ----------------------------
# MQTT Callback
# ----------------------------
def on_message(client, userdata, msg):
    global latest_temp1, latest_temp2, latest_hum1, latest_hum2

    try:
        data = json.loads(msg.payload.decode())
        latest_temp1 = data.get("temp1", "N/A")
        latest_temp2 = data.get("temp2", "N/A")
        latest_hum1 = data.get("humidity1", "N/A")
        latest_hum2 = data.get("humidity2", "N/A")

        temp1_data.append(latest_temp1)
        temp2_data.append(latest_temp2)
        hum1_data.append(latest_hum1)
        hum2_data.append(latest_hum2)
        labels.append(f"Data {len(temp1_data)}")

    except Exception as e:
        print("❌ MQTT Error:", e)

# ----------------------------
# MQTT Setup
# ----------------------------
def start_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("broker.mqtt-dashboard.com", 1883, 60)
    client.subscribe("/UNI494/rhenaamelia/data_sensor")
    client.loop_forever()

threading.Thread(target=start_mqtt, daemon=True).start()

# ----------------------------
# Streamlit Layout
# ----------------------------
st.set_page_config(page_title="Data Sensor", layout="wide")

col1, col2 = st.columns(2)

with col1:
    st.metric("Temperature 1", f"{latest_temp1} °C")
    st.metric("Humidity 1", f"{latest_hum1} %")
with col2:
    st.metric("Temperature 2", f"{latest_temp2} °C")
    st.metric("Humidity 2", f"{latest_hum2} %")

# ----------------------------
# Chart
# ----------------------------
st.markdown("### Grafik Sensor")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(labels, temp1_data, label="Temp 1", marker='o')
ax.plot(labels, temp2_data, label="Temp 2", marker='x')
ax.plot(labels, hum1_data, label="Humidity 1", linestyle='--')
ax.plot(labels, hum2_data, label="Humidity 2", linestyle='--')

ax.set_ylim([0, 100])
ax.set_ylabel("Nilai Sensor")
ax.set_title("Perubahan Data Sensor")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# ----------------------------
# Auto Refresh
# ----------------------------
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=5000, key="sensor_autorefresh")
