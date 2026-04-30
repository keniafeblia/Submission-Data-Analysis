import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Beijing Air Quality Dashboard",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border-left: 4px solid #e63946;
    }
    .stSelectbox label { font-weight: 600; }
    h1 { color: #1d3557; }
    .insight-box {
        background-color: #f0f4ff;
        border-left: 4px solid #457b9d;
        padding: 12px 16px;
        border-radius: 6px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    DATA_DIR = "./PRSA_Data_20130301-20170228/"
    files = [f for f in os.listdir(DATA_DIR) if f.startswith("PRSA_Data_") and f.endswith(".csv")]
    dfs = []
    for fname in sorted(files):
        df_temp = pd.read_csv(os.path.join(DATA_DIR, fname))
        dfs.append(df_temp)
    df = pd.concat(dfs, ignore_index=True)

    # Clean
    df = df.drop_duplicates(subset=['year','month','day','hour','station'])
    num_cols = ['PM2.5','PM10','SO2','NO2','CO','O3','TEMP','PRES','DEWP','RAIN','WSPM']
    for col in num_cols:
        df[col] = df.groupby(['station','month'])[col].transform(lambda x: x.fillna(x.median()))
    df['wd'] = df.groupby('station')['wd'].transform(
        lambda x: x.fillna(x.mode()[0] if not x.mode().empty else 'N'))
    df['datetime'] = pd.to_datetime(df[['year','month','day','hour']])
    season_map = {12:'Winter',1:'Winter',2:'Winter',3:'Spring',4:'Spring',5:'Spring',
                  6:'Summer',7:'Summer',8:'Summer',9:'Autumn',10:'Autumn',11:'Autumn'}
    df['season'] = df['month'].map(season_map)
    return df

df = load_data()

STATIONS = sorted(df['station'].unique())
YEARS = sorted(df['year'].unique())

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/air-quality.png", width=80)
    st.title("🌫️ Filter Data")
    st.markdown("---")
    selected_stations = st.multiselect(
        "Pilih Stasiun", options=STATIONS,
        default=STATIONS,
        help="Pilih satu atau lebih stasiun pemantauan"
    )
    year_range = st.slider(
        "Rentang Tahun", min_value=2013, max_value=2017,
        value=(2013, 2017), step=1
    )
    selected_pollutant = st.selectbox(
        "Polutan Utama", options=['PM2.5','PM10','SO2','NO2','CO','O3'],
        index=0
    )
    st.markdown("---")
    st.caption("📊 Data: PRSA Beijing Air Quality\n2013–2017 | 12 Stasiun")

# ── FILTER ────────────────────────────────────────────────────────────────────
df_f = df[
    (df['station'].isin(selected_stations)) &
    (df['year'] >= year_range[0]) &
    (df['year'] <= year_range[1])
]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🌫️ Beijing Air Quality Dashboard")
st.markdown("**Analisis Kualitas Udara Beijing (2013–2017) | 12 Stasiun Pemantauan**")
st.markdown("---")

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
pm25_avg = df_f['PM2.5'].mean()
pm10_avg = df_f['PM10'].mean()
who_exceed = (df_f['PM2.5'] > 35).mean() * 100
worst_station = df_f.groupby('station')['PM2.5'].mean().idxmax() if not df_f.empty else "-"
best_station = df_f.groupby('station')['PM2.5'].mean().idxmin() if not df_f.empty else "-"

col1.metric("Rata-rata PM2.5", f"{pm25_avg:.1f} µg/m³", delta=f"{pm25_avg-35:.1f} vs WHO limit")
col2.metric("Rata-rata PM10", f"{pm10_avg:.1f} µg/m³")
col3.metric("Jam Melampaui WHO", f"{who_exceed:.1f}%", delta="target: <50%", delta_color="inverse")
col4.metric("🔴 Terpolusi", worst_station)
col5.metric("🟢 Terbersih", best_station)

st.markdown("---")

# ── TAB LAYOUT ────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 Tren & Musiman", "🗺️ Perbandingan Stasiun", "🕐 Pola Harian & Klaster"])

# ═══ TAB 1: Tren Bulanan & Musiman ═══════════════════════════════════════════
with tab1:
    st.subheader(f"Tren {selected_pollutant} Bulanan & Pola Musiman")

    monthly = df_f.groupby(['year','month'])[selected_pollutant].mean().reset_index()
    monthly['period'] = pd.to_datetime(monthly[['year','month']].assign(day=1))
    monthly = monthly.sort_values('period')

    col_a, col_b = st.columns([2, 1])

    with col_a:
        fig1, ax = plt.subplots(figsize=(10, 4))
        ax.plot(monthly['period'], monthly[selected_pollutant],
                color='#E63946', linewidth=2, marker='o', markersize=3)
        ax.fill_between(monthly['period'], monthly[selected_pollutant], alpha=0.15, color='#E63946')
        ax.axhline(y=monthly[selected_pollutant].mean(), color='#457B9D',
                   linestyle='--', linewidth=1.5, label=f"Rata-rata ({monthly[selected_pollutant].mean():.1f})")
        if selected_pollutant == 'PM2.5':
            ax.axhline(y=35, color='green', linestyle=':', linewidth=1.5, label='Batas WHO (35)')
        ax.set_title(f'Tren Bulanan {selected_pollutant}', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'{selected_pollutant} (µg/m³)')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close()

    with col_b:
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        season_order = ['Winter','Spring','Summer','Autumn']
        season_colors = {'Winter':'#AED9E0','Spring':'#B7E4C7','Summer':'#FFD166','Autumn':'#F4845F'}
        data_seasons = [df_f[df_f['season']==s][selected_pollutant].dropna().values for s in season_order]
        bp = ax2.boxplot(data_seasons, labels=season_order, patch_artist=True,
                         medianprops=dict(color='black', linewidth=2),
                         flierprops=dict(marker='o', markersize=2, alpha=0.3))
        for patch, s in zip(bp['boxes'], season_order):
            patch.set_facecolor(season_colors[s]); patch.set_alpha(0.85)
        ax2.set_title(f'{selected_pollutant} per Musim', fontsize=11, fontweight='bold')
        ax2.set_ylabel(f'{selected_pollutant} (µg/m³)')
        ax2.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

    st.markdown("""<div class='insight-box'>
    💡 <b>Insight:</b> Polusi PM2.5 paling tinggi di musim <b>Winter (Des–Feb)</b> karena pemanasan ruangan & inversi termal.
    Musim Panas memiliki kualitas udara terbaik. Hampir semua periode melampaui batas WHO 35 µg/m³.
    </div>""", unsafe_allow_html=True)

# ═══ TAB 2: Perbandingan Stasiun ══════════════════════════════════════════════
with tab2:
    st.subheader("Perbandingan Rata-rata Polutan Antar Stasiun")

    station_avg_tab = df_f.groupby('station')[selected_pollutant].mean().sort_values(ascending=False)

    fig3, ax3 = plt.subplots(figsize=(10, 6))
    colors = []
    for v in station_avg_tab.values:
        q33 = station_avg_tab.quantile(0.33)
        q66 = station_avg_tab.quantile(0.66)
        if v >= q66: colors.append('#E63946')
        elif v >= q33: colors.append('#FFB703')
        else: colors.append('#2DC653')
    bars = ax3.barh(station_avg_tab.index, station_avg_tab.values, color=colors, edgecolor='white', height=0.65)
    for bar, val in zip(bars, station_avg_tab.values):
        ax3.text(val + 0.3, bar.get_y() + bar.get_height()/2, f'{val:.1f}', va='center', fontsize=9)
    if selected_pollutant == 'PM2.5':
        ax3.axvline(x=35, color='green', linestyle='--', linewidth=1.5, label='Batas WHO')
        ax3.legend()
    ax3.set_title(f'Rata-rata {selected_pollutant} per Stasiun', fontsize=13, fontweight='bold')
    ax3.set_xlabel(f'{selected_pollutant} (µg/m³)')
    ax3.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

    # Heatmap per tahun
    st.subheader(f"Heatmap {selected_pollutant} per Stasiun & Tahun")
    pivot = df_f.groupby(['year','station'])[selected_pollutant].mean().unstack('station')
    fig4, ax4 = plt.subplots(figsize=(12, 4))
    sns.heatmap(pivot, cmap='YlOrRd', annot=True, fmt='.0f', linewidths=0.5,
                cbar_kws={'label': f'{selected_pollutant} (µg/m³)'}, ax=ax4)
    ax4.set_title(f'Heatmap Rata-rata {selected_pollutant} per Stasiun & Tahun', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Stasiun'); ax4.set_ylabel('Tahun')
    plt.xticks(rotation=30, ha='right', fontsize=8)
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close()

    st.markdown("""<div class='insight-box'>
    💡 <b>Insight:</b> Stasiun di pusat kota (Wanliu, Gucheng, Guanyuan) secara konsisten lebih terpolusi
    dibanding stasiun pinggiran (Dingling, Huairou). Penurunan nilai terlihat bertahap di seluruh stasiun
    mulai 2015–2016.
    </div>""", unsafe_allow_html=True)

# ═══ TAB 3: Pola Harian & Clustering ══════════════════════════════════════════
with tab3:
    st.subheader("Pola Harian & Clustering Kualitas Udara")

    col_c, col_d = st.columns(2)

    # Pola harian
    with col_c:
        st.markdown(f"**Pola Harian {selected_pollutant} per Stasiun**")
        hourly_all = df_f.groupby(['station','hour'])[selected_pollutant].mean().reset_index()
        fig5, ax5 = plt.subplots(figsize=(7, 5))
        palette = sns.color_palette("tab20", len(selected_stations))
        for i, s in enumerate(selected_stations):
            data = hourly_all[hourly_all['station'] == s]
            if not data.empty:
                ax5.plot(data['hour'], data[selected_pollutant], linewidth=1.8,
                         label=s, marker='o', markersize=3, color=palette[i % len(palette)])
        ax5.set_title(f'Rata-rata {selected_pollutant} per Jam', fontsize=11, fontweight='bold')
        ax5.set_xlabel('Jam ke-'); ax5.set_ylabel(f'{selected_pollutant} (µg/m³)')
        ax5.set_xticks(range(0, 24, 2))
        ax5.legend(fontsize=6.5, loc='upper right', ncol=2)
        ax5.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig5)
        plt.close()

    # Clustering
    with col_d:
        st.markdown("**Clustering Stasiun Berdasarkan PM2.5 (Manual Binning)**")
        station_stats = df.groupby('station')['PM2.5'].mean().reset_index()
        station_stats.columns = ['station', 'pm25_mean']
        bins = [0, 60, 80, float('inf')]
        labels = ['🟢 Rendah', '🟡 Sedang', '🔴 Tinggi']
        station_stats['kategori'] = pd.cut(station_stats['pm25_mean'], bins=bins, labels=labels)
        station_stats = station_stats.sort_values('pm25_mean', ascending=True)

        fig6, ax6 = plt.subplots(figsize=(7, 5))
        cat_colors = {'🟢 Rendah': '#2DC653', '🟡 Sedang': '#FFB703', '🔴 Tinggi': '#E63946'}
        for _, row in station_stats.iterrows():
            ax6.barh(row['station'], row['pm25_mean'],
                     color=cat_colors[row['kategori']], edgecolor='white', height=0.65)
            ax6.text(row['pm25_mean'] + 0.3, row['station'],
                     f"{row['pm25_mean']:.1f} | {row['kategori']}", va='center', fontsize=8)
        ax6.axvline(x=35, color='green', linestyle='--', linewidth=1.5, label='WHO (35)')
        ax6.axvline(x=60, color='#FFB703', linestyle=':', linewidth=1.5, label='Batas Sedang')
        ax6.axvline(x=80, color='#E63946', linestyle=':', linewidth=1.5, label='Batas Tinggi')
        ax6.set_title('Clustering Kualitas Udara per Stasiun', fontsize=11, fontweight='bold')
        ax6.set_xlabel('Rata-rata PM2.5 (µg/m³)')
        ax6.legend(fontsize=8)
        ax6.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        st.pyplot(fig6)
        plt.close()

    # Tabel clustering
    st.subheader("Tabel Ringkasan Clustering")
    st.dataframe(
        station_stats[['station','pm25_mean','kategori']].rename(
            columns={'station':'Stasiun','pm25_mean':'Avg PM2.5 (µg/m³)','kategori':'Kategori'}
        ).sort_values('Avg PM2.5 (µg/m³)', ascending=False).reset_index(drop=True),
        use_container_width=True
    )

    st.markdown("""<div class='insight-box'>
    💡 <b>Insight:</b> Pola harian menunjukkan dua puncak polusi di <b>pagi (07:00–09:00)</b> dan
    <b>malam (21:00–23:00)</b> — bersamaan jam sibuk lalu lintas. Clustering membagi 12 stasiun menjadi
    3 kelompok: Rendah (pinggiran), Sedang, dan Tinggi (pusat kota).
    </div>""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("📊 Dashboard ini dibuat untuk Proyek Akhir Analisis Data | Dataset: PRSA Beijing Air Quality 2013–2017")
