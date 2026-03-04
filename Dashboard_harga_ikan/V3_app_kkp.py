import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard Harga Ikan KKP",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .kpi-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #003366;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        text-align: center;
    }
    .kpi-label { color: #64748B; font-size: 14px; font-weight: bold; text-transform: uppercase; }
    .kpi-value { color: #0F172A; font-size: 28px; font-weight: 800; }
    .header-style {
        background: linear-gradient(90deg, #003366, #005588);
        padding: 25px;
        border-bottom: 5px solid #00AEEF;
        margin-bottom: 25px;
        border-radius: 10px;
        color: white;
    }
    .stExpander { border: 1px solid #E2E8F0; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv('Dashboard_harga_ikan/Data_Ikan_Dashboard_Ready.csv')
    df['date'] = pd.to_datetime(df['date'])
    df['bulan_tahun'] = df['date'].dt.strftime('%Y-%m')
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("File 'Data_Ikan_Dashboard_Ready.csv' tidak ditemukan. Pastikan ada di folder yang sama.")
    st.stop()

# --- HEADER ---
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image("https://www.kkp.go.id/assets/images/logo-kkp.png", width=90)
with col_title:
    st.markdown("""
        <div class="header-style">
            <h2 style="margin: 0;">SISTEM INFORMASI HARGA PASAR IKAN</h2>
            <p style="margin: 8px 0 0; opacity: 0.9;">Market Intelligence - Kementerian Kelautan dan Perikanan RI</p>
        </div>
        """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.header("⚙️ Filter & Kontrol")

selected_komoditas = st.sidebar.selectbox(
    "Pilih Komoditas",
    options=sorted(df['Komoditas'].unique())
)

selected_year = st.sidebar.multiselect(
    "Pilih Tahun",
    options=sorted(df['Tahun'].unique()),
    default=[df['Tahun'].max()]
)

# Provinsi dengan Select All
prov_list = sorted(df['province_name'].unique())

select_all_prov = st.sidebar.checkbox("Pilih Semua Provinsi", value=True)

if select_all_prov:
    selected_prov = prov_list
else:
    selected_prov = st.sidebar.multiselect(
        "Pilih Provinsi",
        options=prov_list,
        default=["DKI Jakarta"]
    )

st.sidebar.caption(f"Provinsi aktif: {len(selected_prov)} / {len(prov_list)}")

# Pilih periode untuk peta & ranking
df_temp = df[(df['Komoditas'] == selected_komoditas) & (df['Tahun'].isin(selected_year))]
bulan_list = sorted(df_temp['bulan_tahun'].unique())
selected_bulan = st.sidebar.selectbox(
    "Periode Peta & Ranking",
    options=bulan_list,
    index=len(bulan_list)-1 if bulan_list else 0
)

st.sidebar.markdown("---")
st.sidebar.subheader("📥 Unduh")

def convert_df(df_to_download):
    return df_to_download.to_csv(index=False).encode('utf-8')

st.sidebar.download_button(
    label="Unduh Data Terfilter (CSV)",
    data=convert_df(df_temp),
    file_name=f"data_{selected_komoditas.lower().replace(' ', '_')}.csv",
    mime='text/csv'
)

# --- FILTER UTAMA ---
mask = (
    (df['Komoditas'] == selected_komoditas) &
    (df['Tahun'].isin(selected_year)) &
    (df['province_name'].isin(selected_prov))
)
df_filtered = df[mask]

df_selected = df_filtered[df_filtered['bulan_tahun'] == selected_bulan]

# --- GAMBAR KOMODITAS ---
komoditas_img = {
    'Ikan_Tongkol': 'https://cdn.hellosehat.com/wp-content/uploads/2019/02/Manfaat-Ikan-Tongkol-yang-Bergizi-dan-Menyehatkan.jpg?w=3840&q=100',
    'Ikan_Bandeng': 'https://asset.kompas.com/crops/fdc37U1TGWYw20TeUCQTfk_FX4s=/105x3:945x563/750x500/data/photo/2018/06/23/479016390.jpg',
    'Ikan_Kembung': 'https://asset.kompas.com/crops/pQNktADtLBolXSD0QgK9QlOy1xw=/61x0:906x563/750x500/data/photo/2021/01/21/600942b282255.jpg'
}

if selected_komoditas in komoditas_img:
    st.image(komoditas_img[selected_komoditas], width=180, caption=selected_komoditas)

# --- KPI ---
col1, col2, col3, col4 = st.columns(4)

avg_price = df_filtered['rata_rata_geometrik'].mean() if not df_filtered.empty else 0
max_val = df_filtered['rata_rata_geometrik'].max() if not df_filtered.empty else 0
min_val = df_filtered['rata_rata_geometrik'].min() if not df_filtered.empty else 0
prov_count = df_filtered['province_name'].nunique()

with col1:
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Rata-rata Nasional</div><div class='kpi-value'>Rp {avg_price:,.0f}</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='kpi-card' style='border-left-color: #EF4444;'><div class='kpi-label'>Harga Tertinggi</div><div class='kpi-value' style='color:#EF4444;'>Rp {max_val:,.0f}</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='kpi-card' style='border-left-color: #10B981;'><div class='kpi-label'>Harga Terendah</div><div class='kpi-value' style='color:#10B981;'>Rp {min_val:,.0f}</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Jumlah Provinsi</div><div class='kpi-value'>{prov_count}</div></div>", unsafe_allow_html=True)

# --- PETA FULL LANDSCAPE ---
st.markdown("---")
st.subheader(f"🗺️ Sebaran Harga {selected_komoditas} — {selected_bulan}")

if not df_selected.empty:
    fig_map = px.scatter_mapbox(
        df_selected,
        lat="latitude",
        lon="longitude",
        color="rata_rata_geometrik",
        size="rata_rata_geometrik",
        hover_name="province_name",
        hover_data={'rata_rata_geometrik': ':,.0f'},
        color_continuous_scale=px.colors.sequential.YlOrRd_r,
        zoom=3.6,
        height=680,               # landscape lebih lebar & tinggi
        mapbox_style="carto-positron"
    )

    fig_map.update_layout(
        margin={"r":0, "t":40, "l":0, "b":0},
        coloraxis_colorbar=dict(
            title="Harga (Rp)",
            thickness=20,
            len=0.7,
            yanchor="middle",
            y=0.5
        )
    )

    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("Tidak ada data untuk filter yang dipilih.")

# --- DIVIDER UNTUK RANKING TABEL ---
st.markdown("---")  # Divider baru untuk tabel ranking

st.subheader("🏆 Tabel Ranking Harga Provinsi")

if not df_selected.empty:
    ranking = df_selected[['province_name', 'rata_rata_geometrik']].sort_values('rata_rata_geometrik', ascending=False)
    st.dataframe(
        ranking.style.format({"rata_rata_geometrik": "Rp {:,.0f}"})
                   .background_gradient(cmap='YlOrRd', subset=['rata_rata_geometrik']),
        use_container_width=True,
        height=400
    )
    st.download_button(
        "Unduh Ranking",
        convert_df(ranking),
        f"ranking_{selected_komoditas.lower()}_{selected_bulan}.csv",
        "text/csv"
    )
else:
    st.info("Tidak ada data ranking.")

# --- DIVIDER UNTUK PERBANDINGAN ANTAR KOMODITAS ---
st.markdown("---")  # Divider baru untuk perbandingan antar komoditas

st.subheader("🔍 Perbandingan Antar Komoditas")

# Slicer provinsi khusus untuk section ini
komoditas_list = sorted(df['Komoditas'].unique())
selected_komoditas_compare = st.multiselect(
    "Pilih Komoditas untuk Dibandingkan",
    options=komoditas_list,
    default=komoditas_list[:2]  # Default 2 komoditas pertama
)

prov_list_compare = sorted(df['province_name'].unique())

select_all_prov_compare = st.checkbox("Pilih Semua Provinsi (Perbandingan)", value=True)

if select_all_prov_compare:
    selected_prov_compare = prov_list_compare
else:
    selected_prov_compare = st.multiselect(
        "Pilih Provinsi (Perbandingan)",
        options=prov_list_compare,
        default=["DKI Jakarta"]
    )

st.caption(f"Provinsi untuk perbandingan: {len(selected_prov_compare)} / {len(prov_list_compare)}")

# Filter data untuk perbandingan
mask_compare = (
    df['Komoditas'].isin(selected_komoditas_compare) &
    (df['Tahun'].isin(selected_year)) &
    (df['province_name'].isin(selected_prov_compare))
)
df_compare = df[mask_compare]

if not df_compare.empty:
    # Grafik perbandingan: Line chart tren harga antar komoditas
    df_trend_compare = df_compare.groupby(['date', 'Komoditas'])['rata_rata_geometrik'].mean().reset_index()
    fig_compare = px.line(
        df_trend_compare,
        x='date',
        y='rata_rata_geometrik',
        color='Komoditas',
        title="Tren Harga Rata-rata Antar Komoditas",
        labels={'rata_rata_geometrik': 'Harga (Rp)', 'date': 'Periode'},
        template='plotly_white'
    )
    fig_compare.update_layout(hovermode="x unified")
    st.plotly_chart(fig_compare, use_container_width=True)

    # Tabel perbandingan: Pivot rata-rata per komoditas & provinsi
    with st.expander("📊 Tabel Rata-rata Harga per Komoditas & Provinsi", expanded=False):
        pivot_compare = df_compare.pivot_table(
            index='province_name',
            columns='Komoditas',
            values='rata_rata_geometrik',
            aggfunc='mean'
        ).round(0).style.format("Rp {:,}")
        st.dataframe(pivot_compare, use_container_width=True)

    st.download_button(
        "Unduh Data Perbandingan",
        convert_df(df_compare),
        f"perbandingan_{'_'.join(selected_komoditas_compare).lower()}.csv",
        "text/csv"
    )
else:
    st.info("Tidak ada data untuk perbandingan. Pilih komoditas dan provinsi.")

# --- TREND UTAMA ---
st.markdown("---")
st.subheader(f"📈 Tren Harga Nasional {selected_komoditas}")

if not df_filtered.empty:
    df_trend = df_filtered.groupby('date')['rata_rata_geometrik'].mean().reset_index()
    fig_trend = px.area(
        df_trend,
        x='date',
        y='rata_rata_geometrik',
        labels={'rata_rata_geometrik': 'Harga (Rp)', 'date': 'Periode'},
        template='plotly_white',
        color_discrete_sequence=['#00AEEF']
    )
    fig_trend.update_layout(hovermode="x unified")
    st.plotly_chart(fig_trend, use_container_width=True)

# --- DIVIDER UNTUK TABEL PIVOT UTAMA ---
st.markdown("---")  # Divider baru untuk tabel pivot utama

st.subheader("📊 Tabel Perbandingan Bulanan (Komoditas Utama)")

if not df_filtered.empty:
    pivot = df_filtered.pivot_table(
        index='province_name',
        columns='bulan_tahun',
        values='rata_rata_geometrik',
        aggfunc='mean'
    ).round(0).style.format("Rp {:,}")
    st.dataframe(pivot, use_container_width=True)
else:
    st.info("Tidak ada data untuk pivot table.")

# --- FOOTER ---
st.markdown("---")
st.caption(
    f"Data terakhir: {df['date'].max().strftime('%d %b %Y')} • "
    f"Dashboard update: {datetime.now().strftime('%d %B %Y %H:%M WIB')} • "
    "Untuk keperluan analisis & presentasi"

)
