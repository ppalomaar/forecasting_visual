import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Dashboard Forecast Nilai Tukar", layout="wide")

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
# SIDEBAR
# ======================
with st.sidebar:
    selected = option_menu("Main Menu", ["Home", "Nilai Tukar Rupiah", "Harga Minyak Mentah", "Forecast", "Evaluasi"],
        icons=["house", "currency-exchange", "fuel-pump", "graph-up-arrow", "clipboard-data"], menu_icon="cast", default_index=0)

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
    st.write("Dashboard ini menampilkan peramalan nilai tukar Rupiah terhadap USD menggunakan model ARIMAX.")

elif selected == "Nilai Tukar Rupiah":
    st.subheader("Grafik Nilai Tukar Rupiah")
    fig = go.Figure(go.Scatter(x=kurs.index, y=kurs['Terakhir'], mode='lines', name='Nilai Tukar'))
    fig.update_layout(title="Pergerakan Nilai Tukar Rupiah", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

elif selected == "Harga Minyak Mentah":
    st.subheader("Grafik Harga Minyak Mentah")
    fig = go.Figure(go.Scatter(x=minyak.index, y=minyak['Harga'], mode='lines', name='Harga Minyak', line=dict(color='orange')))
    fig.update_layout(title="Pergerakan Harga Minyak Mentah Dunia", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

elif selected == "Forecast":
    st.subheader("Visualisasi Forecast")
           
    # 1. Menyiapkan data grouping mingguan untuk label dropdown
    df_weekly = forecast.copy()
    df_weekly['Month'] = df_weekly.index.strftime('%B')
    # Membuat index minggu per bulan
    df_weekly['Week_Num'] = df_weekly.index.to_series().dt.to_period('W').factorize()[0] 
    # Label kustom: "Oktober Minggu ke-1"
    df_weekly['Label'] = df_weekly.index.strftime('%B') + " Minggu ke-" + (df_weekly.groupby('Month')['Week_Num'].transform('dense')).astype(str)
    
    # Dropdown untuk pilih minggu
    selected_week = st.selectbox("Pilih Periode Mingguan:", df_weekly['Label'].unique())
    
    # Filter data berdasarkan label yang dipilih
    filtered_df = df_weekly[df_weekly['Label'] == selected_week]
    
    # 2. Grafik Garis Forecast (Harian)
    fig1 = go.Figure(go.Scatter(
        x=filtered_df.index.strftime('%d %b'), # Format tanggal harian (1 Okt, 2 Okt, dst)
        y=filtered_df['Forecast_ARIMAX'], 
        mode='lines+markers', 
        name='Forecast',
        line=dict(width=3, color='#636EFA')
    ))
    
    fig1.update_layout(
        title=f"Tren Forecast Harian: {selected_week}", 
        xaxis_title="Tanggal",
        yaxis_title="Nilai Tukar (Rp)", 
        template="plotly_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")
    
    # 3. Grafik Perbandingan & Tabel tetap sama seperti sebelumnya...
    # 2. Grafik Perbandingan (Aktual vs Forecast)
    st.subheader("Perbandingan Actual vs Forecast (Keseluruhan)")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=forecast.index, y=forecast['Actual'], name='Actual', line=dict(color='gray')))
    fig2.add_trace(go.Scatter(x=forecast.index, y=forecast['Forecast_ARIMAX'], name='Forecast', line=dict(dash='dash', color='#636EFA')))
    fig2.update_layout(template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)
    
    # 3. Tabel
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