"""
Streamlit dashboard: Passenger car industry — Germany vs. China, Japan and South Korea, 2019–2025
Streamlit-Dashboard: Pkw-Industrie — Deutschland im Vergleich mit China, Japan und Südkorea, 2019–2025

Three languages (Deutsch / English / 中文); language switch at the top of the sidebar.
Direct links: <app-url>/?lang=en and <app-url>/?lang=zh

Reads the star schema exported by autoindustrie_analysis.ipynb from data/clean/
(dim_country.csv, fact_country_year.csv, country_summary.csv).

Start: streamlit run dashboard.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------
# 1. Page settings (must be the first Streamlit command -> title is multilingual)
# ------------------------------------------------------------
st.set_page_config(
    page_title="Pkw-Industrie · Car industry — DE vs. CN, JP, KR",
    layout="wide",
)

DATA_DIR = Path(__file__).parent / "data" / "clean"
REFERENCE = "DEU"  # reference country (is_reference in dim_country)
COUNTRY_ORDER = ["DEU", "CHN", "JPN", "KOR"]

# One fixed colour per country in every chart; Germany is drawn thicker.
COUNTRY_COLORS = {"DEU": "#2a78d6", "CHN": "#eb6834", "JPN": "#1baf7a", "KOR": "#e34948"}
POWERTRAIN_COLORS = {"BEV": "#34495e", "PHEV": "#a3b1bf"}

COUNTRY_NAMES = {
    "de": {"DEU": "Deutschland", "CHN": "China", "JPN": "Japan", "KOR": "Südkorea"},
    "en": {"DEU": "Germany", "CHN": "China", "JPN": "Japan", "KOR": "South Korea"},
    "zh": {"DEU": "德国", "CHN": "中国", "JPN": "日本", "KOR": "韩国"},
}

# ------------------------------------------------------------
# 2. Texts (Deutsch / English)
# ------------------------------------------------------------
TEXTE = {
    "de": {
        "language": "Sprache / Language / 语言",
        "title": "Pkw-Industrie: Deutschland im Vergleich mit China, Japan und Südkorea",
        "source": "Datenquellen: OICA (Produktion, Verkäufe) und IEA Global EV Outlook 2026 (Elektroautos) · 2019–2025",
        "filters": "Filter",
        "countries": "Länder",
        "period": "Zeitraum",
        "mode": "Darstellung (Produktion, Verkäufe)",
        "mode_abs": "Absolute Werte",
        "mode_idx": "Index (2019 = 100)",
        "no_country": "Bitte mindestens ein Land in der Sidebar auswählen.",
        "kpi_header": "Deutschland (Referenzland), {year}",
        "kpi_prod": "Produktion",
        "kpi_sales": "Verkäufe",
        "kpi_share": "E-Auto-Anteil an Neuwagenverkäufen",
        "kpi_charge": "Öffentliche Ladepunkte",
        "vs": "ggü. {year}",
        "pp": "Prozentpunkte",
        "tab_overview": "Produktion & Verkäufe",
        "tab_ev": "Elektroautos",
        "tab_data": "Daten & Hinweise",
        "h_prod": "Pkw-Produktion",
        "h_sales": "Pkw-Verkäufe",
        "h_ratio": "Produktion ÷ Verkäufe",
        "h_share": "Anteil der Elektroautos an den Neuwagenverkäufen",
        "h_evsales": "Verkäufe von Elektroautos: BEV und PHEV",
        "h_stock": "Elektroauto-Bestand",
        "h_charge": "Öffentliche Ladepunkte",
        "ax_cars": "Pkw",
        "ax_index": "Index (2019 = 100)",
        "ax_ratio": "Gebaute Pkw je verkauftem Pkw",
        "ax_share": "Anteil an Neuwagenverkäufen",
        "cap_prod": "Quelle: OICA, Personenkraftwagen.",
        "cap_index": "Der Index hat immer 2019 als Basis, unabhängig vom gewählten Zeitraum.",
        "cap_sales": "Quelle: OICA. Die Zahl für China enthält Exporte (siehe „Daten & Hinweise“).",
        "cap_ratio": "Produktion eines Landes geteilt durch die Verkäufe im selben Land. 1 = Produktion gleich Verkäufe (gestrichelte Linie). Das ist keine Exportzahl.",
        "cap_share": "Quelle: IEA. Elektroautos = batterie-elektrische Autos (BEV) und Plug-in-Hybride (PHEV). Die IEA rundet alle Werte auf zwei signifikante Stellen.",
        "cap_evsales": "Quelle: IEA. BEV und PHEV sind einzeln gerundet, ihre Summe kann deshalb von der IEA-Gesamtzahl abweichen. Jedes Teildiagramm hat eine eigene Achse.",
        "cap_stock": "Quelle: IEA. Bestand = Elektroautos im Verkehr.",
        "cap_charge": "Quelle: IEA. Gezählt werden Ladepunkte (Steckdosen), nicht Ladestationen. Die IEA rundet langsame, schnelle und ultraschnelle Ladepunkte einzeln auf zwei signifikante Stellen; die Summe kann deshalb mehr Stellen haben.",
        "bev": "Batterie-elektrisch (BEV)",
        "phev": "Plug-in-Hybrid (PHEV)",
        "snapshot": "{what} im Jahr {year}",
        "h_summary": "Kennzahlen 2019 und 2025",
        "cap_summary": "Fest für 2019 und 2025, unabhängig vom Zeitraumfilter. Quelle: Tabelle country_summary aus dem Notebook.",
        "h_raw": "Daten pro Land und Jahr",
        "cap_raw": "Gefiltert nach Ländern und Zeitraum aus der Sidebar. Anteile und Veränderungen sind Brüche (0,30 = 30 %).",
        "download": "Gefilterte Daten als CSV herunterladen",
        "h_check": "OICA-Verkäufe außerhalb des IEA-Rundungsbands",
        "cap_check": (
            "Marktgröße laut IEA (E-Verkäufe ÷ E-Anteil) geteilt durch die OICA-Verkäufe. Gezeigt sind die Länder und Jahre, "
            "in denen die OICA-Zahl außerhalb des Bereichs liegt, den die IEA-Rundung zulässt. Nur nach Ländern gefiltert."
        ),
        "no_deviation": "Keine Abweichungen für die gewählten Länder.",
        "h_notes": "Hinweise",
        "notes": [
            "**Quellen:** OICA (Produktion; Verkäufe „Registrations or sales of new vehicles – passenger cars“) und IEA Global EV Outlook 2026 (Verkäufe, Anteil, Bestand und Ladepunkte von Elektroautos).",
            "**Elektroautos** sind batterie-elektrische Autos (BEV) und Plug-in-Hybride (PHEV), ohne Brennstoffzellenfahrzeuge (IEA-Definition).",
            "**China:** Die OICA-Verkaufszahl für China entspricht den Pkw-Verkäufen des chinesischen Herstellerverbands CAAM und enthält Exporte. 2025 waren es 30,103 Mio., davon 6,038 Mio. Exporte ([Gasgoo](https://autonews.gasgoo.com/articles/news/chinas-2025-auto-market-hits-new-highs-in-both-annual-sales-output-2011438280283627520)). Die Linie ist also keine Inlandsmarkt-Zahl.",
            "**Abweichungen OICA/IEA:** Für China (2022–2025) erklärt der Export-Anteil die Abweichung. Für Japan 2025 und Südkorea 2021, 2024 und 2025 wurde keine Erklärung gefunden. Belege und Rechnungen stehen in Abschnitt 12 des Notebooks.",
            "**Produktion ÷ Verkäufe** vergleicht die Produktion eines Landes mit den Verkäufen im selben Land. Die Daten enthalten keine Handelszahlen, es ist also keine Exportzahl.",
        ],
        "not_reached": "nicht erreicht",
        "col_country": "Land",
        "col_year": "Jahr",
        "col_oica": "OICA-Verkäufe",
        "col_ratio": "IEA-Marktgröße ÷ OICA",
        "rows": {
            "production_2019": "Produktion 2019",
            "production_2025": "Produktion 2025",
            "production_change": "Veränderung der Produktion 2019 → 2025",
            "production_change_2020": "Veränderung der Produktion 2020 gegenüber 2019",
            "production_recovery_year": "Produktion wieder über dem Niveau von 2019 seit",
            "sales_2019": "Verkäufe 2019",
            "sales_2025": "Verkäufe 2025",
            "sales_change": "Veränderung der Verkäufe 2019 → 2025",
            "production_to_sales_ratio_2025": "Produktion ÷ Verkäufe 2025",
            "ev_sales_share_2019": "E-Auto-Anteil 2019",
            "ev_sales_share_2025": "E-Auto-Anteil 2025",
            "ev_sales_2025": "E-Auto-Verkäufe 2025",
            "ev_stock_2025": "E-Auto-Bestand 2025",
            "public_charging_points_2025": "Öffentliche Ladepunkte 2025",
        },
    },
    "en": {
        "language": "Sprache / Language / 语言",
        "title": "Passenger car industry: Germany compared with China, Japan and South Korea",
        "source": "Data sources: OICA (production, sales) and IEA Global EV Outlook 2026 (electric cars) · 2019–2025",
        "filters": "Filters",
        "countries": "Countries",
        "period": "Period",
        "mode": "View (production, sales)",
        "mode_abs": "Absolute values",
        "mode_idx": "Index (2019 = 100)",
        "no_country": "Please select at least one country in the sidebar.",
        "kpi_header": "Germany (reference country), {year}",
        "kpi_prod": "Production",
        "kpi_sales": "Sales",
        "kpi_share": "EV share of new car sales",
        "kpi_charge": "Public charging points",
        "vs": "vs. {year}",
        "pp": "percentage points",
        "tab_overview": "Production & sales",
        "tab_ev": "Electric cars",
        "tab_data": "Data & notes",
        "h_prod": "Passenger car production",
        "h_sales": "Passenger car sales",
        "h_ratio": "Production ÷ sales",
        "h_share": "Electric cars as a share of new car sales",
        "h_evsales": "Electric car sales: BEV and PHEV",
        "h_stock": "Electric car stock",
        "h_charge": "Public charging points",
        "ax_cars": "Cars",
        "ax_index": "Index (2019 = 100)",
        "ax_ratio": "Cars built per car sold",
        "ax_share": "Share of new car sales",
        "cap_prod": "Source: OICA, passenger cars.",
        "cap_index": "The index always uses 2019 as its base, regardless of the selected period.",
        "cap_sales": "Source: OICA. The figure for China includes exports (see “Data & notes”).",
        "cap_ratio": "A country's production divided by its sales in the same country. 1 = production equals sales (dashed line). This is not an export figure.",
        "cap_share": "Source: IEA. Electric cars = battery-electric cars (BEV) and plug-in hybrids (PHEV). The IEA rounds all values to two significant figures.",
        "cap_evsales": "Source: IEA. BEV and PHEV are rounded separately, so their sum can differ from the IEA total. Each panel has its own axis.",
        "cap_stock": "Source: IEA. Stock = electric cars in operation.",
        "cap_charge": "Source: IEA. Counts charging points (power sockets), not charging stations. The IEA rounds slow, fast and ultra-fast charging points separately to two significant figures, so their sum can have more digits.",
        "bev": "Battery-electric (BEV)",
        "phev": "Plug-in hybrid (PHEV)",
        "snapshot": "{what} in {year}",
        "h_summary": "Key figures 2019 and 2025",
        "cap_summary": "Fixed for 2019 and 2025, independent of the period filter. Source: country_summary table from the notebook.",
        "h_raw": "Data by country and year",
        "cap_raw": "Filtered by the countries and period in the sidebar. Shares and changes are fractions (0.30 = 30 %).",
        "download": "Download filtered data as CSV",
        "h_check": "OICA sales outside the IEA rounding band",
        "cap_check": (
            "Market size implied by the IEA (EV sales ÷ EV share) divided by OICA sales. Shown are the countries and years "
            "in which the OICA figure lies outside the range that the IEA rounding allows. Filtered by country only."
        ),
        "no_deviation": "No deviations for the selected countries.",
        "h_notes": "Notes",
        "notes": [
            "**Sources:** OICA (production; sales “Registrations or sales of new vehicles – passenger cars”) and IEA Global EV Outlook 2026 (electric car sales, share, stock and charging points).",
            "**Electric cars** are battery-electric cars (BEV) and plug-in hybrids (PHEV), excluding fuel cell vehicles (IEA definition).",
            "**China:** The OICA sales figure for China equals the passenger vehicle sales of the China Association of Automobile Manufacturers (CAAM) and includes exports. In 2025 it was 30.103 million, of which 6.038 million were exports ([Gasgoo](https://autonews.gasgoo.com/articles/news/chinas-2025-auto-market-hits-new-highs-in-both-annual-sales-output-2011438280283627520)). The line is therefore not a domestic-market figure.",
            "**OICA/IEA differences:** For China (2022–2025) the export share explains the difference. For Japan 2025 and South Korea 2021, 2024 and 2025 no explanation was found. Sources and calculations are in Section 12 of the notebook.",
            "**Production ÷ sales** compares a country's production with its sales in the same country. The data contain no trade figures, so it is not an export figure.",
        ],
        "not_reached": "not reached",
        "col_country": "Country",
        "col_year": "Year",
        "col_oica": "OICA sales",
        "col_ratio": "IEA market size ÷ OICA",
        "rows": {
            "production_2019": "Production 2019",
            "production_2025": "Production 2025",
            "production_change": "Change in production 2019 → 2025",
            "production_change_2020": "Change in production 2020 vs. 2019",
            "production_recovery_year": "Production back above the 2019 level since",
            "sales_2019": "Sales 2019",
            "sales_2025": "Sales 2025",
            "sales_change": "Change in sales 2019 → 2025",
            "production_to_sales_ratio_2025": "Production ÷ sales 2025",
            "ev_sales_share_2019": "EV share 2019",
            "ev_sales_share_2025": "EV share 2025",
            "ev_sales_2025": "EV sales 2025",
            "ev_stock_2025": "EV stock 2025",
            "public_charging_points_2025": "Public charging points 2025",
        },
    },
    "zh": {
        "language": "Sprache / Language / 语言",
        "title": "乘用车行业：德国与中国、日本、韩国的比较",
        "source": "数据来源：OICA（产量、销量）和 IEA《2026年全球电动汽车展望》（电动汽车）· 2019–2025年",
        "filters": "筛选条件",
        "countries": "国家",
        "period": "时间范围",
        "mode": "显示方式（产量、销量）",
        "mode_abs": "绝对值",
        "mode_idx": "指数（2019年 = 100）",
        "no_country": "请在侧边栏至少选择一个国家。",
        "kpi_header": "德国（参考国家），{year}年",
        "kpi_prod": "产量",
        "kpi_sales": "销量",
        "kpi_share": "电动汽车占新车销量的比例",
        "kpi_charge": "公共充电接口",
        "vs": "较{year}年",
        "pp": "个百分点",
        "tab_overview": "产量与销量",
        "tab_ev": "电动汽车",
        "tab_data": "数据与说明",
        "h_prod": "乘用车产量",
        "h_sales": "乘用车销量",
        "h_ratio": "产量 ÷ 销量",
        "h_share": "电动汽车占新车销量的比例",
        "h_evsales": "电动汽车销量：BEV 与 PHEV",
        "h_stock": "电动汽车保有量",
        "h_charge": "公共充电接口",
        "ax_cars": "数量（辆）",
        "ax_index": "指数（2019年 = 100）",
        "ax_ratio": "每售出1辆对应生产的车辆数",
        "ax_share": "占新车销量的比例",
        "cap_prod": "来源：OICA，乘用车。",
        "cap_index": "指数始终以2019年为基准，与所选时间范围无关。",
        "cap_sales": "来源：OICA。中国的数据包含出口（见“数据与说明”）。",
        "cap_ratio": "一国的产量除以该国的销量。1 = 产量等于销量（虚线）。这不是出口数据。",
        "cap_share": "来源：IEA。电动汽车 = 纯电动汽车（BEV）和插电式混合动力汽车（PHEV）。IEA 将所有数值四舍五入到两位有效数字。",
        "cap_evsales": "来源：IEA。BEV 和 PHEV 分别四舍五入，因此两者之和可能与 IEA 的总数不一致。每个子图使用各自的坐标轴。",
        "cap_stock": "来源：IEA。保有量 = 在用的电动汽车数量。",
        "cap_charge": "来源：IEA。统计的是充电接口（插座），而不是充电站。IEA 将慢充、快充和超快充接口分别四舍五入到两位有效数字，因此总数的有效数字可能多于两位。",
        "bev": "纯电动（BEV）",
        "phev": "插电式混合动力（PHEV）",
        "snapshot": "{year}年{what}",
        "h_summary": "2019年与2025年关键数据",
        "cap_summary": "固定为2019年和2025年，不受时间范围筛选影响。来源：笔记本中的 country_summary 表。",
        "h_raw": "各国各年数据",
        "cap_raw": "按侧边栏中的国家和时间范围筛选。占比和变化为小数（0.30 = 30 %）。",
        "download": "下载筛选后的数据（CSV）",
        "h_check": "OICA 销量超出 IEA 舍入区间的情况",
        "cap_check": (
            "IEA 推算的市场规模（电动汽车销量 ÷ 电动汽车占比）除以 OICA 销量。表中列出 OICA 数值超出 IEA 舍入所允许范围的国家和年份。"
            "仅按国家筛选。"
        ),
        "no_deviation": "所选国家没有差异。",
        "h_notes": "说明",
        "notes": [
            "**数据来源：** OICA（产量；销量为“Registrations or sales of new vehicles – passenger cars”，即新车注册或销售——乘用车）以及 IEA《2026年全球电动汽车展望》（电动汽车销量、占比、保有量和充电接口）。",
            "**电动汽车**指纯电动汽车（BEV）和插电式混合动力汽车（PHEV），不含燃料电池汽车（IEA 定义）。",
            "**中国：** OICA 的中国销量数据与中国汽车工业协会（CAAM）的乘用车销量一致，并且包含出口。2025年为3010.3万辆，其中出口603.8万辆（[Gasgoo](https://autonews.gasgoo.com/articles/news/chinas-2025-auto-market-hits-new-highs-in-both-annual-sales-output-2011438280283627520)）。因此这条曲线不是国内市场数据。",
            "**OICA 与 IEA 的差异：** 中国（2022–2025年）的差异可以由出口解释。日本2025年以及韩国2021、2024、2025年的差异未找到解释。依据和计算见笔记本第12节。",
            "**产量 ÷ 销量**是将一国的产量与该国的销量相比。数据中没有贸易数据，因此它不是出口数据。",
            "**关于中文版本：** 本页中文由 AI 翻译，尚未经过母语者审校。",
        ],
        "not_reached": "尚未达到",
        "col_country": "国家",
        "col_year": "年份",
        "col_oica": "OICA 销量",
        "col_ratio": "IEA 推算市场规模 ÷ OICA",
        "rows": {
            "production_2019": "2019年产量",
            "production_2025": "2025年产量",
            "production_change": "产量变化 2019 → 2025",
            "production_change_2020": "2020年产量较2019年的变化",
            "production_recovery_year": "产量重新超过2019年水平的起始年份",
            "sales_2019": "2019年销量",
            "sales_2025": "2025年销量",
            "sales_change": "销量变化 2019 → 2025",
            "production_to_sales_ratio_2025": "2025年产量 ÷ 销量",
            "ev_sales_share_2019": "2019年电动汽车占比",
            "ev_sales_share_2025": "2025年电动汽车占比",
            "ev_sales_2025": "2025年电动汽车销量",
            "ev_stock_2025": "2025年电动汽车保有量",
            "public_charging_points_2025": "2025年公共充电接口数",
        },
    },
}


# ------------------------------------------------------------
# 3. Load data (star schema from the notebook)
# ------------------------------------------------------------
@st.cache_data
def load_data():
    dim_country = pd.read_csv(DATA_DIR / "dim_country.csv")
    fact = pd.read_csv(DATA_DIR / "fact_country_year.csv")
    summary = pd.read_csv(DATA_DIR / "country_summary.csv")
    return dim_country, fact, summary


if not (DATA_DIR / "fact_country_year.csv").exists():
    st.error(
        f"Data not found / Daten nicht gefunden: {DATA_DIR}. "
        "Run the notebook first / Bitte zuerst das Notebook ausführen (autoindustrie_analysis.ipynb)."
    )
    st.stop()

dim_country, fact, summary = load_data()

# ------------------------------------------------------------
# 4. Language switch (top of the sidebar); ?lang=en preselects English
# ------------------------------------------------------------
SPRACHEN = {"Deutsch": "de", "English": "en", "中文": "zh"}
gewuenscht = str(st.query_params.get("lang", "de")).lower()[:2]
startsprache = list(SPRACHEN.values()).index(gewuenscht) if gewuenscht in SPRACHEN.values() else 0
lang = SPRACHEN[
    st.sidebar.radio(TEXTE["de"]["language"], list(SPRACHEN), index=startsprache, horizontal=True)
]
T = TEXTE[lang]


def country_name(code: str) -> str:
    return COUNTRY_NAMES[lang].get(code, code)


def fmt_num(value: float, decimals: int = 0) -> str:
    """Number with thousands separator; German uses '.' for thousands and ',' for decimals."""
    if pd.isna(value):
        return "–"
    text = f"{value:,.{decimals}f}"
    if lang == "de":
        text = text.replace(",", "\0").replace(".", ",").replace("\0", ".")
    return text


def fmt_pct_change(value: float, decimals: int = 1) -> str:
    """Signed percentage change, e.g. '-11,0 %' (ASCII minus so Streamlit colours it red)."""
    if pd.isna(value):
        return "–"
    return f"{'+' if value >= 0 else '-'}{fmt_num(abs(value) * 100, decimals)} %"


def fmt_share(value: float) -> str:
    """Share as a percentage with at most two significant figures (the IEA precision)."""
    if pd.isna(value):
        return "–"
    text = f"{value * 100:.2g}"
    if "e" in text:
        text = f"{value * 100:.0f}"
    return text.replace(".", ",") + " %" if lang == "de" else text + " %"


def fmt_delta_pp(diff: float) -> str:
    text = f"{diff * 100:+.1f}"
    if text.endswith(".0"):
        text = text[:-2]
    return (text.replace(".", ",") if lang == "de" else text) + " " + T["pp"]


# ------------------------------------------------------------
# 5. Sidebar filters
# ------------------------------------------------------------
st.sidebar.header(T["filters"])

country_codes = [c for c in COUNTRY_ORDER if c in set(fact["country_code"])]
selected = st.sidebar.multiselect(
    T["countries"], country_codes, default=country_codes, format_func=country_name
)

years = sorted(fact["year"].unique())
year_start, year_end = st.sidebar.slider(
    T["period"], min_value=int(years[0]), max_value=int(years[-1]), value=(int(years[0]), int(years[-1])), step=1
)

mode = st.sidebar.radio(
    T["mode"], ["abs", "idx"], format_func=lambda m: T["mode_abs"] if m == "abs" else T["mode_idx"]
)

st.title(T["title"])
st.caption(T["source"])

if not selected:
    st.info(T["no_country"])
    st.stop()

view = fact[fact["country_code"].isin(selected) & fact["year"].between(year_start, year_end)].copy()
view["country_name"] = view["country_code"].map(country_name)

# ------------------------------------------------------------
# 6. KPI tiles (reference country Germany; independent of the country filter)
# ------------------------------------------------------------
st.subheader(T["kpi_header"].format(year=year_end))
de = fact[fact["country_code"] == REFERENCE].set_index("year")


def kpi_delta_pct(column: str, decimals: int = 1):
    start, end = de.loc[year_start, column], de.loc[year_end, column]
    if year_start == year_end or pd.isna(start) or pd.isna(end):
        return None
    return f"{fmt_pct_change(end / start - 1, decimals)} {T['vs'].format(year=year_start)}"


k1, k2, k3, k4 = st.columns(4)
k1.metric(T["kpi_prod"], fmt_num(de.loc[year_end, "production"]), kpi_delta_pct("production"))
k2.metric(T["kpi_sales"], fmt_num(de.loc[year_end, "sales"]), kpi_delta_pct("sales"))

share_start, share_end = de.loc[year_start, "ev_sales_share"], de.loc[year_end, "ev_sales_share"]
share_delta = None
if year_start != year_end and pd.notna(share_start) and pd.notna(share_end):
    share_delta = f"{fmt_delta_pp(share_end - share_start)} {T['vs'].format(year=year_start)}"
k3.metric(T["kpi_share"], fmt_share(share_end), share_delta)
k4.metric(T["kpi_charge"], fmt_num(de.loc[year_end, "public_charging_points"]), kpi_delta_pct("public_charging_points", decimals=0))

st.write("")
tab_overview, tab_ev, tab_data = st.tabs([T["tab_overview"], T["tab_ev"], T["tab_data"]])


# ------------------------------------------------------------
# 7. Chart helpers
# ------------------------------------------------------------
def style(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
        separators=",." if lang == "de" else ".,",
    )
    return fig


def line_chart(column: str, y_title: str, tickformat: str, hover_format: str, hline: float | None = None,
               from_zero: bool = False):
    fig = go.Figure()
    for code in selected:
        sub = view[view["country_code"] == code]
        reference = code == REFERENCE
        fig.add_trace(go.Scatter(
            x=sub["year"], y=sub[column], mode="lines+markers", name=country_name(code),
            line=dict(color=COUNTRY_COLORS[code], width=4 if reference else 2),
            marker=dict(size=8 if reference else 6),
            hovertemplate=f"%{{x}}: %{{y:{hover_format}}}<extra>{country_name(code)}</extra>",
        ))
    if hline is not None:
        fig.add_hline(y=hline, line_dash="dash", line_color="grey", line_width=1)
    fig.update_xaxes(dtick=1, title_text="")
    fig.update_yaxes(title_text=y_title, tickformat=tickformat, rangemode="tozero" if from_zero else "normal")
    return style(fig)


def snapshot_bar(column: str, tick_format: str):
    snap = fact[fact["country_code"].isin(selected) & (fact["year"] == year_end)][["country_code", column]].dropna()
    snap = snap.sort_values(column)
    fig = go.Figure(go.Bar(
        x=snap[column], y=[country_name(c) for c in snap["country_code"]], orientation="h",
        marker_color=[COUNTRY_COLORS[c] for c in snap["country_code"]],
        text=snap[column], texttemplate="%{text:" + tick_format + "}", textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x:,.0f}<extra></extra>",
    ))
    fig.update_xaxes(visible=False, range=[0, snap[column].max() * 1.25] if len(snap) else None)
    fig.update_yaxes(title_text="")
    return style(fig, height=300)


# ------------------------------------------------------------
# 8. Tab 1: production and sales
# ------------------------------------------------------------
with tab_overview:
    left, right = st.columns(2)
    suffix = "" if mode == "abs" else "_index"
    y_title = T["ax_cars"] if mode == "abs" else T["ax_index"]
    tickformat = "~s" if mode == "abs" else ".0f"
    hover_format = ",.0f" if mode == "abs" else ".1f"
    hline = None if mode == "abs" else 100

    with left:
        st.subheader(T["h_prod"])
        st.plotly_chart(line_chart(f"production{suffix}", y_title, tickformat, hover_format, hline, from_zero=(mode == "abs")), width="stretch")
        st.caption(T["cap_prod"] + (" " + T["cap_index"] if mode == "idx" else ""))
    with right:
        st.subheader(T["h_sales"])
        st.plotly_chart(line_chart(f"sales{suffix}", y_title, tickformat, hover_format, hline, from_zero=(mode == "abs")), width="stretch")
        st.caption(T["cap_sales"] + (" " + T["cap_index"] if mode == "idx" else ""))

    st.divider()
    st.subheader(T["h_ratio"])
    st.plotly_chart(line_chart("production_to_sales_ratio", T["ax_ratio"], ".1f", ".2f", hline=1, from_zero=True), width="stretch")
    st.caption(T["cap_ratio"])


# ------------------------------------------------------------
# 9. Tab 2: electric cars
# ------------------------------------------------------------
with tab_ev:
    st.subheader(T["h_share"])
    st.plotly_chart(line_chart("ev_sales_share", T["ax_share"], ".0%", ".2~%", from_zero=True), width="stretch")
    st.caption(T["cap_share"])

    st.divider()
    st.subheader(T["h_evsales"])
    long = view.melt(
        id_vars=["country_code", "country_name", "year"],
        value_vars=["ev_sales_bev", "ev_sales_phev"],
        var_name="powertrain", value_name="value",
    )
    long["powertrain"] = long["powertrain"].map({"ev_sales_bev": T["bev"], "ev_sales_phev": T["phev"]})
    fig = px.bar(
        long, x="year", y="value", color="powertrain", facet_col="country_name", facet_col_wrap=2,
        facet_col_spacing=0.1, facet_row_spacing=0.16,
        color_discrete_map={T["bev"]: POWERTRAIN_COLORS["BEV"], T["phev"]: POWERTRAIN_COLORS["PHEV"]},
        category_orders={
            "country_name": [country_name(c) for c in selected],
            "powertrain": [T["bev"], T["phev"]],
        },
        labels={"powertrain": "", "value": "", "year": ""},
    )
    fig.update_yaxes(matches=None, showticklabels=True, tickformat="~s", title_text="")
    fig.update_xaxes(dtick=1, title_text="")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_traces(hovertemplate="%{x}: %{y:,.0f}<extra>%{fullData.name}</extra>")
    style(fig, height=320 if len(selected) <= 2 else 600)
    fig.update_layout(margin=dict(l=0, r=0, t=60, b=0), legend=dict(y=1.12))
    st.plotly_chart(fig, width="stretch")
    st.caption(T["cap_evsales"])

    st.divider()
    left, right = st.columns(2)
    with left:
        st.subheader(T["snapshot"].format(what=T["h_stock"], year=year_end))
        st.plotly_chart(snapshot_bar("ev_stock", ".2~s"), width="stretch")
        st.caption(T["cap_stock"])
    with right:
        st.subheader(T["snapshot"].format(what=T["h_charge"], year=year_end))
        st.plotly_chart(snapshot_bar("public_charging_points", ".3~s"), width="stretch")
        st.caption(T["cap_charge"])


# ------------------------------------------------------------
# 10. Tab 3: tables and notes
# ------------------------------------------------------------
def fmt_summary(key: str, value) -> str:
    if key == "production_recovery_year":
        return T["not_reached"] if pd.isna(value) else str(int(value))
    if pd.isna(value):
        return "–"
    if key.endswith("_change") or key == "production_change_2020":
        return fmt_pct_change(value)
    if key.startswith("ev_sales_share"):
        return fmt_share(value)
    if key.startswith("production_to_sales_ratio"):
        return fmt_num(value, 2)
    return fmt_num(value)


with tab_data:
    st.subheader(T["h_summary"])
    sel_summary = summary[summary["country_code"].isin(selected)].set_index("country_code").loc[selected]
    table = pd.DataFrame(
        {country_name(code): [fmt_summary(key, sel_summary.loc[code, key]) for key in T["rows"]] for code in selected},
        index=list(T["rows"].values()),
    )
    st.dataframe(table, width="stretch", height=35 * (len(table) + 1) + 3)
    st.caption(T["cap_summary"])

    st.divider()
    st.subheader(T["h_raw"])
    raw = view.drop(columns=["country_name"])
    raw = raw.sort_values(
        ["country_code", "year"], key=lambda col: col.map({c: i for i, c in enumerate(COUNTRY_ORDER)}) if col.name == "country_code" else col
    )
    count_columns = ["production", "sales", "ev_sales_bev", "ev_sales_phev", "ev_sales", "ev_stock", "public_charging_points"]
    st.dataframe(
        raw, width="stretch", hide_index=True,
        column_config={c: st.column_config.NumberColumn(format="localized") for c in count_columns},
    )
    st.caption(T["cap_raw"])
    st.download_button(T["download"], raw.to_csv(index=False).encode("utf-8"), "fact_country_year_filtered.csv", "text/csv")

    st.divider()
    st.subheader(T["h_check"])
    outside = fact[
        fact["country_code"].isin(selected) & ~fact["oica_within_iea_band"].fillna(True).astype(bool)
    ].copy()
    if outside.empty:
        st.info(T["no_deviation"])
    else:
        check = pd.DataFrame({
            T["col_country"]: outside["country_code"].map(country_name),
            T["col_year"]: outside["year"],
            T["col_oica"]: outside["sales"].map(fmt_num),
            T["col_ratio"]: outside["iea_vs_oica_market_ratio"].map(lambda v: fmt_num(v, 2)),
        })
        st.dataframe(check, width="stretch", hide_index=True)
    st.caption(T["cap_check"])

    st.divider()
    st.subheader(T["h_notes"])
    for note in T["notes"]:
        st.markdown(f"- {note}")
