import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
from io import BytesIO
from PIL import Image

# Konfigurasi halaman
st.set_page_config(
    page_title="Smart Tableau - Dashboard Litbang",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Menampilkan logo di sidebar dari URL
logo_url = "https://www.gen3eng.com/images/Links_spin.gif"  # Ganti dengan URL gambar yang sesuai
st.sidebar.image(logo_url, width=150)  # Anda dapat menyesuaikan lebar gambar sesuai kebutuhan
)


# Desain Header
st.markdown("""
<style>
    .main {
        background-color: black;
    }
    h1 {
        font-size: 36px;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
    }
    p {
        font-size: 20px;
        text-align: center;
        color: black;
    }
    /* Warna teks tab normal & aktif jadi hitam */
div[role="tab"] {
    color: black !important;
}

div[role="tab"][aria-selected="true"] {
    color: black !important;
    font-weight: bold;
}

    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    /* Ubah warna teks sidebar header dan subheader */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, 
    [data-testid="stSidebar"] h5, 
    [data-testid="stSidebar"] h6,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {
        color: black;
    }
    
</style>
<h1>📊 Smart Dashboard</h1>
<p>Visualisasi Data dan Analisis Statistik</p>
<hr>
""", unsafe_allow_html=True)

# Sidebar - Upload & Opsi
st.sidebar.header("📁 Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload file", type=["csv", "xlsx"])

st.sidebar.subheader("🧹 Cleane Data")
missing_option = st.sidebar.radio("Pilih cara menangani data kosong:", ["Abaikan", "Hapus Baris", "Isi Rata-rata"])

st.sidebar.subheader("🎛️ Filter Data")
filter_option = st.sidebar.checkbox("Aktifkan filter data")


# Proses file jika ada
if uploaded_file:
    try:
        # Baca data
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        df.columns = [col.strip() for col in df.columns]  # Bersihkan kolom
        if df.columns.duplicated().any():
            counts = {}
            df.columns = [f"{col}_{counts[col]}" if counts.setdefault(col, 0) else col for col in df.columns]

        df.drop_duplicates(inplace=True)

        # Ubah string ke datetime jika memungkinkan
        for col in df.select_dtypes(include='object'):
            try:
                converted = pd.to_datetime(df[col], errors='coerce')
                if converted.notna().sum() > 0:
                    df[col] = converted
            except:
                pass

        # Identifikasi tipe kolom
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        categorical_cols = df.select_dtypes(include='object').columns.tolist()
        datetime_cols = df.select_dtypes(include='datetime').columns.tolist()

        # Tangani data kosong
        if missing_option == "Hapus Baris":
            df.dropna(inplace=True)
        elif missing_option == "Isi Rata-rata":
            for col in numeric_cols:
                df[col].fillna(df[col].mean(), inplace=True)

        # Tab Navigasi
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Visualisasi", "📊 Statistik", "📌 Perbandingan", "🔗 Korelasi", "📝 Narasi Otomatis"])

        # === Tab 1: Visualisasi ===
        with tab1:
            st.subheader("📈 Buat Visualisasi")
            chart_type = st.selectbox("Jenis Grafik", ["Bar", "Line", "Area", "Scatter", "Box", "Pie", "Histogram"])
            if not numeric_cols:
                st.warning("⚠️ Tidak ada kolom numerik untuk divisualisasikan.")
            else:
                col_x = st.selectbox("Kolom X", df.columns)
                col_y = st.selectbox("Kolom Y", numeric_cols + datetime_cols)
                fig = None

                try:
                    if chart_type == "Bar":
                        fig = px.bar(df, x=col_x, y=col_y, color=col_x)
                    elif chart_type == "Line" and col_x in datetime_cols:
                        fig = px.line(df, x=col_x, y=col_y)
                    elif chart_type == "Area" and col_x in datetime_cols:
                        fig = px.area(df, x=col_x, y=col_y)
                    elif chart_type == "Scatter":
                        fig = px.scatter(df, x=col_x, y=col_y, color=col_x)
                    elif chart_type == "Box":
                        fig = px.box(df, x=col_x, y=col_y)
                    elif chart_type == "Pie" and col_x in categorical_cols and col_y in numeric_cols:
                        fig = px.pie(df, names=col_x, values=col_y)
                    elif chart_type == "Histogram" and col_y in numeric_cols:
                        bin_size = st.slider("Ukuran Bin", 1, 100, 10)
                        fig = px.histogram(df, x=col_y, nbins=bin_size)

                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Gagal menampilkan grafik: {e}")

        # === Tab 2: Statistik Deskriptif ===
        with tab2:
            st.subheader("📊 Statistik Deskriptif")
            st.dataframe(df.describe(include='all').transpose(), use_container_width=True)

            st.subheader("🔍 Uji Normalitas")
            for col in numeric_cols:
                data = df[col].dropna()
                if len(data) < 50:
                    stat, p = stats.shapiro(data)
                    method = "Shapiro-Wilk"
                else:
                    stat, p = stats.kstest(data, 'norm')
                    method = "Kolmogorov-Smirnov"
                st.write(f"**{col}** ({method}): p-value = {p:.4f}")
                st.markdown("✅ Terdistribusi normal." if p >= 0.05 else "❌ Tidak terdistribusi normal.")

        # === Tab 3: Perbandingan Dua Kolom ===
        with tab3:
            st.subheader("📌 Bandingkan Dua Kolom")
            if len(numeric_cols) >= 2:
                col1 = st.selectbox("Kolom 1", numeric_cols)
                col2 = st.selectbox("Kolom 2", [col for col in numeric_cols if col != col1])
                trend = st.selectbox("Trendline", ["ols", "lowess"])
                try:
                    fig = px.scatter(df, x=col1, y=col2, trendline=trend)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Gagal menampilkan perbandingan: {e}")
            else:
                st.info("📉 Minimal 2 kolom numerik diperlukan.")

        # === Tab 4: Korelasi ===
        with tab4:
            st.subheader("🔗 Korelasi Antar Kolom")
            if len(numeric_cols) >= 2:
                corr = df[numeric_cols].corr()
                threshold = st.slider("Tampilkan korelasi di atas:", 0.0, 1.0, 0.5)
                filtered = corr[corr.abs() >= threshold]
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.heatmap(filtered, annot=True, cmap="Blues", fmt=".2f", ax=ax)
                st.pyplot(fig)
            else:
                st.info("📉 Minimal 2 kolom numerik diperlukan.")

        # === Tab 5: Narasi Otomatis ===
        with tab5:
            st.subheader("📝 Analisis Naratif Otomatis")
            st.markdown(f"**Jumlah data:** {df.shape[0]} baris")
            for col in numeric_cols:
                st.markdown(f"- **{col}** → Rata-rata: {df[col].mean():,.2f}, Median: {df[col].median():,.2f}, Modus: {df[col].mode().iat[0] if not df[col].mode().empty else 'N/A'}, Std Dev: {df[col].std():.2f}")
            for col in categorical_cols:
                st.markdown(f"- **{col}** → Kategori terbanyak: {df[col].value_counts().idxmax()}")
            for col in datetime_cols:
                st.markdown(f"- **{col}** → Rentang: {df[col].min().date()} - {df[col].max().date()}")

            st.subheader("⬇️ Unduh Data")
            csv_data = df.to_csv(index=False).encode('utf-8')
            xlsx_buffer = BytesIO()
            df.to_excel(xlsx_buffer, index=False)
            st.download_button("📥 Unduh Data (CSV)", data=csv_data, file_name="data_bersih.csv", mime="text/csv")
            st.download_button("📥 Unduh Data (Excel)", data=xlsx_buffer.getvalue(), file_name="data_bersih.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        st.error(f"❌ Gagal memproses file: {e}")
else:
    st.info("📂 Silakan unggah file CSV atau Excel untuk memulai.")
