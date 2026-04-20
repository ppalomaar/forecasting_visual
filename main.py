import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="Dashboard Forecast Nilai Tukar",
    layout="wide"
)

# ======================
# LOAD DATA 
# ======================
kurs = pd.read_csv("kurs.csv")
minyak = pd.read_csv("minyak.csv")
forecast = pd.read_csv("hasil_forecast_arimax_finall.csv")

# Preprocessing
kurs['Tanggal'] = pd.to_datetime(kurs['Tanggal'])
minyak['Date'] = pd.to_datetime(minyak['Date'])
forecast['Tanggal'] = pd.to_datetime(forecast['Tanggal'])

minyak = minyak.rename(columns={'Date': 'Tanggal', 'Price': 'Harga'})
kurs['Terakhir'] = kurs['Terakhir'].astype(str).str.replace(',', '').astype(float)
minyak['Harga'] = minyak['Harga'].astype(str).str.replace(',', '').astype(float)

kurs = kurs.sort_values("Tanggal").set_index("Tanggal")
minyak = minyak.sort_values("Tanggal").set_index("Tanggal")
forecast = forecast.sort_values("Tanggal").set_index("Tanggal")

# ======================
# SIDEBAR NAVIGATION
# ======================
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "Nilai Tukar Rupiah", "Harga Minyak Mentah", "Forecast", "Evaluasi"],
        icons=["house", "currency-exchange", "fuel-pump", "graph-up-arrow", "clipboard-data"],
        menu_icon="cast",
        default_index=0,
    )

# ======================
# LOGIC NAVIGATION
# ======================

if selected == "Home":
    st.write("##")
    st.markdown("""
        <h1 style='text-align: center; font-size: 50px;'>Advanced Forecasting,<br>for Currency Analysis.</h1>
        <p style='text-align: center; font-size: 20px; color: #666;'>
            Get access to state-of-the-art ARIMAX machine learning engines <br> 
            that forecast USD to IDR time-series data.
        </p>
    """, unsafe_allow_html=True)
    
    st.write("##")
    st.markdown("---")
    
    st.subheader("Tentang Proyek Ini")
    st.write("""
    Dashboard ini dikembangkan sebagai alat bantu analisis untuk melakukan peramalan 
    **Nilai Tukar Rupiah terhadap USD** dengan mengintegrasikan variabel eksternal berupa **Harga Minyak Mentah Dunia**. 
    
    **Fitur Utama:**
    * **Analisis Data Historis:** Memantau tren pergerakan nilai tukar dan harga minyak dari tahun 2019-2025.
    * **Model ARIMAX:** Menggunakan teknik statistik tingkat lanjut untuk memprediksi nilai tukar dengan akurasi tinggi.
    * **Evaluasi Akurasi:** Transparansi perhitungan error model menggunakan metrik RMSE dan MAPE.
    """)

elif selected == "Nilai Tukar Rupiah":
    st.subheader("Grafik Nilai Tukar Rupiah")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=kurs.index, y=kurs['Terakhir'], mode='lines', name='Nilai Tukar'))
    fig.update_layout(title="Pergerakan Nilai Tukar Rupiah", xaxis_title="Tanggal", yaxis_title="Rp/USD", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

elif selected == "Harga Minyak Mentah":
    st.subheader("Grafik Harga Minyak Mentah")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=minyak.index, y=minyak['Harga'], mode='lines', name='Harga Minyak', line=dict(color='orange')))
    fig.update_layout(title="Pergerakan Harga Minyak Mentah Dunia", xaxis_title="Tanggal", yaxis_title="Harga", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

elif selected == "Forecast":
    st.subheader("Perbandingan Actual vs Forecast")
    
    # Filter Tampilan
    mode = st.radio("Pilih Tampilan Grafik:", ["Harian", "Mingguan"], horizontal=True)
    
    plot_df = forecast.copy()
    if mode == "Mingguan":
        plot_df = plot_df.resample('W').mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df['Actual'], mode='lines+markers', name='Actual'))
    fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df['Forecast_ARIMAX'], mode='lines', name='Forecast', line=dict(dash='dash')))
    fig.update_layout(title=f"Perbandingan Nilai Aktual dan Forecast ({mode})", template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tabel Actual")
        st.dataframe(forecast[['Actual']], use_container_width=True)
    with col2:
        st.subheader("Tabel Forecast")
        st.dataframe(forecast[['Forecast_ARIMAX']], use_container_width=True)

elif selected == "Evaluasi":
    st.subheader("Evaluasi Model")
    rmse = ((forecast['Actual'] - forecast['Forecast_ARIMAX'])**2).mean()**0.5
    mape = (abs((forecast['Actual'] - forecast['Forecast_ARIMAX']) / forecast['Actual']).mean()) * 100
    
    col1, col2 = st.columns(2)
    col1.metric("RMSE", f"{rmse:.2f}")
    col2.metric("MAPE", f"{mape:.2f}%")
    st.markdown("---")
    st.write("Semakin kecil nilai RMSE dan MAPE, semakin akurat model yang dibangun.")