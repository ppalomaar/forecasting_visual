import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Dashboard Forecast Nilai Tukar", layout="wide")

# ======================
# LOAD & PREPROCESSING DATA 
# ======================
kurs = pd.read_csv("kurs.csv")
minyak = pd.read_csv("minyak.csv")
forecast = pd.read_csv("hasil_forecast_arimax_finall.csv")

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
        <h1 style='text-align: center; font-size: 50px;'>Peramalan Nilai Tukar IDR-USD,<br>Oktober - Desember 2025.</h1>
        <p style='text-align: center; font-size: 20px; color: #666;'>
            Menyediakan layanan peramalan nilai tukar USD ke Rupiah <br> 
            menggunakan model ARIMAX berdasarkan data hsitoris.
        </p>
    """, unsafe_allow_html=True)
    st.write("##")
    st.markdown("---")
    st.subheader("Tentang Proyek Ini")
    st.write("""
    Dashboard ini dikembangkan sebagai alat bantu analisis untuk melakukan peramalan 
    **Nilai Tukar Rupiah terhadap USD** dengan mengintegrasikan variabel eksternal berupa **Harga Minyak Mentah Dunia**. 
    """)

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
    st.subheader("Visualisasi Forecast Harian per Minggu")
    
    # Logic Label Mingguan
    df_weekly = forecast.copy()
    df_weekly['Month'] = df_weekly.index.strftime('%B')
    
    # Fungsi untuk menghitung minggu ke-berapa dalam bulan
    def get_week_of_month(date):
        first_day = date.replace(day=1)
        dom = date.day
        adjusted_dom = dom + first_day.weekday()
        return int((adjusted_dom - 1) / 7) + 1

    df_weekly['Week_Num'] = [get_week_of_month(d) for d in df_weekly.index]
    df_weekly['Label'] = df_weekly['Month'] + " Minggu ke-" + df_weekly['Week_Num'].astype(str)
    
    # Dropdown Filter
    selected_week = st.selectbox("Pilih Periode Mingguan:", df_weekly['Label'].unique())
    filtered_df = df_weekly[df_weekly['Label'] == selected_week]
    
    # Grafik Garis (Harian)
    fig1 = go.Figure(go.Scatter(
        x=filtered_df.index.strftime('%d %b'), 
        y=filtered_df['Forecast_ARIMAX'], 
        mode='lines+markers', 
        name='Forecast',
        line=dict(width=3, color='#636EFA')
    ))
    fig1.update_layout(title=f"Tren Forecast Harian: {selected_week}", template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")
    
    # Perbandingan
    st.subheader("Perbandingan Actual vs Forecast")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=forecast.index, y=forecast['Actual'], name='Actual', line=dict(color='#636EFA')))
    fig2.add_trace(go.Scatter(x=forecast.index, y=forecast['Forecast_ARIMAX'], name='Forecast', line=dict(dash='dash', color="#FF2D2D")))
    fig2.update_layout(template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)
    
    col1, col2 = st.columns(2)
    col1.subheader("Tabel Actual")
    col1.dataframe(forecast[['Actual']], use_container_width=True)
    col2.subheader("Tabel Forecast")
    col2.dataframe(forecast[['Forecast_ARIMAX']], use_container_width=True)

elif selected == "Evaluasi":
    st.subheader("Evaluasi Model")
    rmse = ((forecast['Actual'] - forecast['Forecast_ARIMAX'])**2).mean()**0.5
    mape = (abs((forecast['Actual'] - forecast['Forecast_ARIMAX']) / forecast['Actual']).mean()) * 100
    col1, col2 = st.columns(2)
    col1.metric("RMSE", f"{rmse:.2f}")
    col2.metric("MAPE", f"{mape:.2f}%")