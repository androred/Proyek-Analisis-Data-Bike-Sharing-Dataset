"""Dashboard interaktif analisis Bike Sharing Dataset.

Jalankan dengan:
    streamlit run dashboard.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Dashboard Penyewaan Sepeda",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#1E3A8A"
TEAL = "#0F766E"
ACCENT = "#D97706"
SLATE = "#64748B"
SEASON_COLORS = {
    "Semi": "#93C5FD",
    "Panas": "#F59E0B",
    "Gugur": "#D97706",
    "Dingin": "#1E3A8A",
}
YEAR_COLORS = {2011: "#94A3B8", 2012: PRIMARY}
MONTHS_ID = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]
MONTH_ABBR_ID = [m[:3] for m in MONTHS_ID]
SEASON_ORDER = ["Semi", "Panas", "Gugur", "Dingin"]
WEATHER_ORDER = ["Cerah/Berawan", "Berkabut/Mendung", "Hujan/Salju Ringan"]


st.markdown(
    f"""
    <style>
        [data-testid="stSidebar"] {{ background: #F1F5F9; }}
        [data-testid="stMetric"] {{
            background: #FFFFFF; border: 1px solid #E2E8F0;
            border-radius: 12px; padding: 14px 16px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, .05);
        }}
        .dashboard-subtitle {{ color: {SLATE}; margin-top: -12px; margin-bottom: 18px; }}
        .insight-box {{
            background: #F8FAFC; border: 1px solid #CBD5E1;
            border-left: 5px solid {ACCENT}; border-radius: 10px;
            padding: 16px 20px; margin-top: 8px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    """Membaca data lokal dengan beberapa lokasi fallback yang aman."""
    base_dir = Path(__file__).resolve().parent
    candidates = [
        base_dir / "Data" / "day.csv",
        base_dir / "data" / "day.csv",
        base_dir / "main_data.csv",
        base_dir / "Dashboard" / "all_data.csv",
    ]
    source = next((path for path in candidates if path.exists()), None)
    if source is None:
        raise FileNotFoundError("Data tidak ditemukan. Letakkan file day.csv di folder Data.")

    data = pd.read_csv(source)
    data["dteday"] = pd.to_datetime(data["dteday"], errors="coerce")
    data = data.dropna(subset=["dteday", "cnt"]).copy()

    season_map = {1: "Semi", 2: "Panas", 3: "Gugur", 4: "Dingin"}
    weather_map = {
        1: "Cerah/Berawan",
        2: "Berkabut/Mendung",
        3: "Hujan/Salju Ringan",
        4: "Hujan/Salju Ringan",
    }
    data["musim"] = data["season"].map(season_map)
    data["cuaca"] = data["weathersit"].map(weather_map).fillna("Tidak diketahui")
    data["tahun"] = data["dteday"].dt.year
    data["bulan"] = data["dteday"].dt.month
    data["jenis_hari"] = data["workingday"].map({1: "Hari Kerja", 0: "Akhir Pekan/Libur"})
    data["tanggal_label"] = data["dteday"].dt.strftime("%d %b %Y")
    return data.sort_values("dteday")


def format_number(value: float, decimals: int = 0) -> str:
    if pd.isna(value):
        return "—"
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def format_date_id(value) -> str:
    date = pd.Timestamp(value)
    return f"{date.day:02d} {MONTH_ABBR_ID[date.month - 1]} {date.year}"


def monthly_ticks(frame: pd.DataFrame):
    if frame.empty:
        return [], []
    dates = pd.date_range(frame["dteday"].min().replace(day=1), frame["dteday"].max(), freq="MS")
    labels = [f"{MONTH_ABBR_ID[d.month - 1]} {d.year}" for d in dates]
    return dates, labels


def aggregate_by(frame: pd.DataFrame, group: str, metric: str) -> pd.DataFrame:
    operation = {"Total": "sum", "Rata-rata": "mean", "Maksimum": "max", "Minimum": "min"}[metric]
    result = frame.groupby(group, as_index=False)["cnt"].agg(operation).rename(columns={"cnt": "nilai"})
    return result


data = load_data()

with st.sidebar:
    st.markdown("## Filter Data")
    date_min = data["dteday"].min().date()
    date_max = data["dteday"].max().date()
    date_range = st.date_input("Rentang tanggal", value=(date_min, date_max), min_value=date_min, max_value=date_max)

    tahun_options = ["Semua"] + sorted(data["tahun"].unique().tolist())
    tahun = st.selectbox("Tahun", tahun_options, format_func=lambda x: str(x))
    musim = st.multiselect("Musim", SEASON_ORDER, default=SEASON_ORDER)
    bulan = st.multiselect("Bulan", MONTHS_ID, default=MONTHS_ID)
    jenis_hari = st.selectbox("Jenis hari", ["Semua", "Hari Kerja", "Akhir Pekan/Libur"])
    cuaca = st.multiselect("Kondisi cuaca", WEATHER_ORDER, default=WEATHER_ORDER)
    metric = st.selectbox("Metrik grafik", ["Total", "Rata-rata", "Maksimum", "Minimum"])

    st.divider()
    st.markdown("### Tentang Dashboard")
    st.caption(
        "Dashboard ini menganalisis pola penyewaan sepeda selama 2011–2012 "
        "berdasarkan waktu, musim, cuaca, dan karakteristik hari. "
        "Sumber data: Bike Sharing Dataset dari UCI Machine Learning Repository."
    )
    st.caption("Dibuat oleh: Tim Analisis Data")


if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_date = end_date = pd.to_datetime(date_range)

filtered = data[data["dteday"].between(start_date, end_date)].copy()
if tahun != "Semua":
    filtered = filtered[filtered["tahun"] == int(tahun)]
filtered = filtered[filtered["musim"].isin(musim) & filtered["bulan"].map(lambda x: MONTHS_ID[x - 1]).isin(bulan)]
if jenis_hari != "Semua":
    filtered = filtered[filtered["jenis_hari"] == jenis_hari]
filtered = filtered[filtered["cuaca"].isin(cuaca)]


st.title("Dashboard Penyewaan Sepeda")
st.markdown("<p class='dashboard-subtitle'>Eksplorasi tren penyewaan berdasarkan waktu, musim, cuaca, dan karakteristik hari.</p>", unsafe_allow_html=True)

if filtered.empty:
    st.warning("Tidak ada data yang sesuai dengan kombinasi filter saat ini. Silakan ubah filter.")
    st.stop()

total_rental = filtered["cnt"].sum()
average_daily = filtered["cnt"].mean()
season_totals = filtered.groupby("musim")["cnt"].sum()
top_season = season_totals.idxmax()
top_season_value = season_totals.max()
record = filtered.loc[filtered["cnt"].idxmax()]

st.subheader("Ringkasan Performa")
metric_cols = st.columns(5)
with metric_cols[0]:
    st.metric("Total Penyewaan", format_number(total_rental))
with metric_cols[1]:
    st.metric("Rata-rata Harian", format_number(average_daily, 1))
with metric_cols[2]:
    st.metric("Musim Tertinggi", f"{top_season}", format_number(top_season_value))
with metric_cols[3]:
    st.metric("Rekor Harian", format_number(record["cnt"]), format_date_id(record["dteday"]))
with metric_cols[4]:
    st.metric("Data Dianalisis", f"{len(filtered)} Hari")

st.divider()
st.subheader("Tren Penyewaan Harian")
trend = filtered[["dteday", "cnt", "cuaca", "tanggal_label"]].sort_values("dteday")
tick_values, tick_labels = monthly_ticks(trend)
fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=trend["dteday"], y=trend["cnt"], mode="lines", name="Penyewaan",
    line=dict(color=PRIMARY, width=2.5), fill="tozeroy", fillcolor="rgba(30,58,138,.10)",
    customdata=trend[["tanggal_label", "cuaca"]],
    hovertemplate="Tanggal: %{customdata[0]}<br>Penyewaan: %{y:,.0f}<br>Cuaca: %{customdata[1]}<extra></extra>",
))
fig_trend.add_hline(y=average_daily, line_dash="dash", line_color=ACCENT,
                    annotation_text=f"Rata-rata: {format_number(average_daily, 1)}",
                    annotation_position="top left")
fig_trend.update_layout(
    template="plotly_white", height=420, margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(title="Tanggal", tickmode="array", tickvals=tick_values, ticktext=tick_labels),
    yaxis_title="Jumlah Penyewaan", hovermode="x unified", showlegend=False,
)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()
left_col, right_col = st.columns(2, gap="large")
with left_col:
    st.subheader(f"Penyewaan Berdasarkan Musim ({metric})")
    season_chart = aggregate_by(filtered, "musim", metric)
    season_chart["musim"] = pd.Categorical(season_chart["musim"], SEASON_ORDER, ordered=True)
    season_chart = season_chart.sort_values("musim")
    fig_season = px.bar(season_chart, x="musim", y="nilai", color="musim", color_discrete_map=SEASON_COLORS,
                        text="nilai", labels={"musim": "Musim", "nilai": metric})
    fig_season.update_traces(texttemplate="%{text:,.0f}", textposition="outside", hovertemplate="Musim: %{x}<br>Nilai: %{y:,.1f}<extra></extra>")
    fig_season.update_layout(template="plotly_white", height=390, showlegend=False, margin=dict(l=20, r=20, t=20, b=20), yaxis_title=metric)
    st.plotly_chart(fig_season, use_container_width=True)

with right_col:
    st.subheader(f"Perbandingan Tahunan per Musim ({metric})")
    annual = aggregate_by(filtered, ["tahun", "musim"], metric)
    annual["musim"] = pd.Categorical(annual["musim"], SEASON_ORDER, ordered=True)
    annual = annual.sort_values(["musim", "tahun"])
    fig_annual = px.bar(annual, x="musim", y="nilai", color="tahun", barmode="group", text="nilai",
                        color_discrete_map=YEAR_COLORS, labels={"musim": "Musim", "nilai": metric, "tahun": "Tahun"})
    fig_annual.update_traces(texttemplate="%{text:,.0f}", textposition="outside", hovertemplate="Tahun: %{fullData.name}<br>Musim: %{x}<br>Nilai: %{y:,.1f}<extra></extra>")
    fig_annual.update_layout(template="plotly_white", height=390, margin=dict(l=20, r=20, t=20, b=20), yaxis_title=metric, legend_title="Tahun")
    st.plotly_chart(fig_annual, use_container_width=True)

st.divider()
heat_col, explain_col = st.columns([1.35, 1], gap="large")
with heat_col:
    st.subheader("Korelasi Variabel")
    corr_columns = {"temp": "Suhu Aktual", "atemp": "Suhu Terasa", "hum": "Kelembaban", "windspeed": "Kecepatan Angin", "cnt": "Total Sewa"}
    corr = filtered[list(corr_columns)].rename(columns=corr_columns).corr()
    if len(filtered) >= 2:
        fig_heat = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu_r", aspect="auto")
        fig_heat.update_layout(template="plotly_white", height=390, margin=dict(l=20, r=20, t=20, b=20), coloraxis_colorbar_title="Korelasi")
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Heatmap membutuhkan setidaknya dua hari data aktif.")
with explain_col:
    st.subheader("Cara Membaca Korelasi")
    if len(filtered) >= 2 and corr["Total Sewa"].drop("Total Sewa").notna().any():
        strongest = corr["Total Sewa"].drop("Total Sewa").abs().idxmax()
        strongest_value = corr.loc[strongest, "Total Sewa"]
        arah = "positif" if strongest_value >= 0 else "negatif"
        st.info(
            f"Korelasi mendekati 1 menunjukkan hubungan positif, sedangkan nilai mendekati -1 "
            f"menunjukkan hubungan negatif. Pada data terfilter, hubungan paling menonjol dengan "
            f"Total Sewa adalah **{strongest}** dengan korelasi **{strongest_value:.2f}** ({arah})."
        )
    else:
        st.info("Belum cukup variasi data untuk menghitung korelasi yang bermakna.")
    st.metric("Rentang Data Aktif", f"{format_date_id(filtered['dteday'].min())} – {format_date_id(filtered['dteday'].max())}")
    st.metric("Cuaca Dominan", filtered["cuaca"].mode().iat[0])

st.divider()
st.subheader("Ringkasan & Insight Utama")
year_totals = filtered.groupby("tahun")["cnt"].sum().sort_index()
growth_text = "Perbandingan tahunan belum tersedia karena hanya satu tahun yang aktif."
if {2011, 2012}.issubset(set(year_totals.index)) and year_totals.loc[2011] != 0:
    growth = (year_totals.loc[2012] - year_totals.loc[2011]) / year_totals.loc[2011] * 100
    growth_text = f"Penyewaan tahun 2012 berubah {abs(growth):.1f}% {'naik' if growth >= 0 else 'turun'} dibandingkan tahun 2011."

season_avg = filtered.groupby("musim")["cnt"].mean().idxmax()
insights = [
    f"Total penyewaan pada periode terfilter mencapai **{format_number(total_rental)}**, dengan rata-rata **{format_number(average_daily, 1)} penyewaan per hari**.",
    f"Musim dengan total penyewaan tertinggi adalah **{top_season}** dengan **{format_number(top_season_value)} penyewaan**.",
    f"Rekor penyewaan terjadi pada **{format_date_id(record['dteday'])}**, yaitu sebanyak **{format_number(record['cnt'])} penyewaan**.",
    f"{growth_text} Rata-rata penyewaan tertinggi berdasarkan musim terdapat pada **{season_avg}**.",
]
st.markdown('<div class="insight-box">' + "\n".join(f"- {item}" for item in insights) + "</div>", unsafe_allow_html=True)
