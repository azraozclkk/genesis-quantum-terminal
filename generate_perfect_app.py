import ast

# 1. Get GLOSSARY_DB dict
glossary_db_dict = {}
extra_terms = []
with open("update_data.py", "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == "GLOSSARY_DB":
                        glossary_db_dict = ast.literal_eval(node.value)
                    elif target.id == "extra_terms":
                        extra_terms = ast.literal_eval(node.value)

glossary_str = "GLOSSARY_DB = {\n"
for k, v in glossary_db_dict.items():
    glossary_str += f'    "{k}": "{v.replace('"', '\\"')}",\n'

for i in range(0, len(extra_terms), 2):
    k = extra_terms[i]
    v = extra_terms[i+1]
    glossary_str += f'    "{k}": "{v.replace('"', '\\"')}",\n'
glossary_str += "}"

# 2. Get HISTORY_DB and render_history from apply_30_events.py (variable 'middle')
history_code = ""
with open("apply_30_events.py", "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "middle":
                    history_code = node.value.value

# 3. Assemble full app
part1 = """import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta

# --- Configuration & Styling ---
st.set_page_config(page_title="Bitcoin Sovereign & Risk Intelligence Terminal", layout="wide", initial_sidebar_state="expanded")

st.markdown('''
<style>
    :root {
        --bg-color: #05070a;
        --card-bg: #0d1117;
        --border-color: #1f2937;
        --text-color: #c9d1d9;
        --highlight: #58a6ff;
        --danger: #f85149;
        --success: #3fb950;
        --warning: #d29922;
    }
    
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
    }
    
    .stSidebar, [data-testid="stSidebar"] {
        background-color: var(--card-bg) !important;
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    .card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 16px;
    }
    
    .intel-tag {
        display: inline-block;
        padding: 2px 8px;
        font-size: 0.75rem;
        font-weight: 600;
        line-height: 1.5;
        border-radius: 20px;
        border: 1px solid var(--border-color);
        background-color: rgba(31, 41, 55, 0.5);
        color: var(--highlight);
        margin-right: 8px;
        margin-bottom: 8px;
    }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    
    .status-live {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: var(--danger);
        border-radius: 50%;
        margin-right: 8px;
        animation: blink 1.5s infinite;
        vertical-align: middle;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: white;
    }
</style>
''', unsafe_allow_html=True)

"""

part2 = """
SELLER_INTEL = [
    {
        "name": "Mt. Gox Rehabilitation Trust",
        "volume": "142,000 BTC",
        "status": "Dağıtım Aşamasında",
        "heat": "Kritik",
        "slippage": "%4.2 - %6.5 (Ani Satış)",
        "routes": "Kraken, Bitstamp, Bitbank",
        "trigger": "Alacaklıların %60'ının aynı hafta içinde itibari para çıkışı yapması."
    },
    {
        "name": "US DOJ (Silk Road)",
        "volume": "210,000 BTC",
        "status": "Parçalı OTC Satışı",
        "heat": "Yüksek",
        "slippage": "%2.1 - %3.5",
        "routes": "Coinbase Prime, OTC Masaları",
        "trigger": "Adalet Bakanlığı'nın transfer onayı ve 10,000+ BTC on-chain hareketi."
    },
    {
        "name": "Miner Capitulation Index",
        "volume": "Dalgalı (~50,000 BTC)",
        "status": "Baskı Altında",
        "heat": "Orta-Yüksek",
        "slippage": "%1.5 - %2.5",
        "routes": "Binance, B2B OTC",
        "trigger": "Hash fiyatının üretim maliyetinin %15 altına düşmesi."
    },
    {
        "name": "GBTC (Grayscale)",
        "volume": "Sürekli Çıkış",
        "status": "ETF Çıkışları",
        "heat": "Orta",
        "slippage": "%0.5 - %1.2",
        "routes": "Coinbase Prime",
        "trigger": "Piyasa açılışlarında yüksek prim/iskonto arbitrajı."
    }
]

# --- Stochastic Simulation Engine ---
def run_quantum_sim(v, w, d, a_total, a_active_set):
    ticks = 120
    prices = [60000.0]
    agents_active = [a_active_set]
    low_liquidity_flags = [False]
    
    np.random.seed(42)
    
    for t in range(1, ticks):
        prev_price = prices[-1]
        prev_agents = agents_active[-1]
        
        shock = np.random.normal(0, v)
        whale_impact = np.random.normal(-w, w * 0.5) if np.random.random() < 0.1 else 0
        
        resistance = d / 100.0
        
        price_change = (shock + whale_impact) * (1 - resistance) * 1000
        new_price = max(1000, prev_price + price_change)
        
        if price_change < -500:
            new_agents = max(0, prev_agents - np.random.randint(5, 20))
        elif price_change > 500:
            new_agents = min(a_total, prev_agents + np.random.randint(1, 10))
        else:
            new_agents = prev_agents
            
        is_low_liq = new_agents < (a_total * 0.3)
        if is_low_liq:
            new_price = new_price * 0.85
            new_agents = int(new_agents * 0.9)
            
        prices.append(new_price)
        agents_active.append(new_agents)
        low_liquidity_flags.append(is_low_liq)
        
    return pd.DataFrame({
        'Tick': range(ticks),
        'Price': prices,
        'ActiveAgents': agents_active,
        'LowLiquidity': low_liquidity_flags
    })

def render_stress_analysis():
    st.markdown("<h2>STRES ANALİZİ VE SİSTEMİK RİSKLER</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-color);'>Kuantum Stokastik Simülasyon Motoru.</p><hr>", unsafe_allow_html=True)
    
    col_params, col_metrics = st.columns([1, 2])
    
    with col_params:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>Simülasyon Parametreleri</h3>", unsafe_allow_html=True)
        v = st.slider("Volatilite Çarpanı (v)", 0.1, 5.0, 1.5, 0.1)
        w = st.slider("Balina Satış Baskısı (w)", 0.0, 10.0, 3.5, 0.1)
        d = st.slider("Piyasa Derinliği (d)", 10, 100, 40, 5)
        a_total = 1000
        a_active = st.slider("Başlangıç Aktif Ajanlar", 100, 1000, 800, 50)
        st.markdown("</div>", unsafe_allow_html=True)
        
    df = run_quantum_sim(v, w, d, a_total, a_active)
    
    with col_metrics:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='card'><div style='color:var(--text-color);'>Son Fiyat</div><div class='metric-value'>${df['Price'].iloc[-1]:,.0f}</div></div>", unsafe_allow_html=True)
        with m2:
            min_agents = df['ActiveAgents'].min()
            color = "var(--danger)" if min_agents < 300 else "var(--success)"
            st.markdown(f"<div class='card'><div style='color:var(--text-color);'>Minimum Ajan</div><div class='metric-value' style='color:{color};'>{min_agents}</div></div>", unsafe_allow_html=True)
        with m3:
            liq_events = df['LowLiquidity'].sum()
            st.markdown(f"<div class='card'><div style='color:var(--text-color);'>Likitide Krizi (Tick)</div><div class='metric-value' style='color:var(--warning);'>{liq_events}</div></div>", unsafe_allow_html=True)
            
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=df['Tick'], y=df['Price'], name="Fiyat", line=dict(color="#58a6ff", width=2)),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=df['Tick'], y=df['ActiveAgents'], name="Aktif Ajanlar", line=dict(color="#3fb950", width=2, dash="dot")),
        secondary_y=True,
    )
    
    low_liq_ticks = df[df['LowLiquidity']]['Tick'].tolist()
    if low_liq_ticks:
        fig.add_vrect(
            x0=low_liq_ticks[0], x1=low_liq_ticks[-1],
            fillcolor="#f85149", opacity=0.2,
            layer="below", line_width=0,
            annotation_text="DÜŞÜK LİKİDİTE ALANI", annotation_position="top left",
            annotation_font_color="#f85149"
        )
        
    fig.update_layout(
        title="Fiyat Trendleri ve Ajan Tasfiyeleri Ortak Sapması",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d1d9"),
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_yaxes(title_text="Fiyat (USD)", secondary_y=False, gridcolor="#1f2937")
    fig.update_yaxes(title_text="Aktif Ajan Sayısı", secondary_y=True, showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True)

def render_seller_intel():
    st.markdown("<h2>SATICI İSTİHBARATI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-color);'>Kurumsal ve Egemen satış tehditlerinin on-chain izlemesi.</p><hr>", unsafe_allow_html=True)
    
    for intel in SELLER_INTEL:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f'''
            <div class='card' style='height: 100%;'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <h3 style='margin-top:0;'><span class='status-live'></span>{intel["name"]}</h3>
                    <span style='color:var(--danger); font-weight:bold; font-size:1.2rem;'>{intel["volume"]}</span>
                </div>
                <div style='margin-top: 15px;'>
                    <div style='margin-bottom:8px;'><strong style='color:var(--text-color);'>Durum:</strong> <span style='color:white;'>{intel["status"]}</span></div>
                    <div style='margin-bottom:8px;'><strong style='color:var(--text-color);'>Isı:</strong> <span style='color:var(--warning);'>{intel["heat"]}</span></div>
                    <div style='margin-bottom:8px;'><strong style='color:var(--text-color);'>Slippage:</strong> <span style='color:var(--danger);'>{intel["slippage"]}</span></div>
                    <div style='margin-bottom:8px;'><strong style='color:var(--text-color);'>Rota:</strong> <span style='color:white;'>{intel["routes"]}</span></div>
                </div>
                <div style='margin-top: 15px; padding: 10px; background-color: rgba(0,0,0,0.3); border-radius: 4px;'>
                    <strong style='color:var(--text-color);'>Algoritmik Tetikleyici:</strong><br>
                    <span style='font-size:0.9rem;'>{intel["trigger"]}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
        with col2:
            ticks = np.arange(0, 30)
            base_risk = np.random.uniform(20, 40)
            risk = base_risk + np.cumsum(np.random.normal(0, 5, 30))
            risk = np.clip(risk, 0, 100)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=ticks, y=risk,
                mode='lines',
                line=dict(color="#f85149", width=2, shape='spline'),
                fill='tozeroy',
                fillcolor='rgba(248, 81, 73, 0.1)'
            ))
            
            fig.update_layout(
                title="30 Günlük Risk Projeksiyonu",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#c9d1d9"),
                margin=dict(l=0, r=0, t=30, b=10),
                height=250,
                xaxis=dict(showgrid=False, visible=False),
                yaxis=dict(showgrid=True, gridcolor="#1f2937", range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)

def render_glossary():
    st.markdown("<h2>TEKNİK SÖZLÜK</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-color);'>Kripto para ve blok zinciri ekosisteminin temel terminolojisi.</p><hr>", unsafe_allow_html=True)
    
    search_query = st.text_input("Terim Ara...", "").lower()
    
    count = 0
    col1, col2 = st.columns(2)
    cols = [col1, col2]
    
    for term, definition in sorted(GLOSSARY_DB.items()):
        if search_query in term.lower() or search_query in definition.lower():
            with cols[count % 2]:
                st.markdown(f'''
                <div class='card' style='padding: 16px; margin-bottom: 16px; height: 120px; overflow-y: auto;'>
                    <strong style='color:var(--highlight); font-size:1.1rem;'>{term}</strong>
                    <p style='margin-bottom:0; margin-top:8px; font-size:0.95rem;'>{definition}</p>
                </div>
                ''', unsafe_allow_html=True)
            count += 1
            
    if count == 0:
        st.info("Arama kriterlerine uygun terim bulunamadı.")
    else:
        st.markdown(f"<p style='color:var(--text-color); font-size:0.8rem; text-align:right;'>Toplam {count} terim listelendi.</p>", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.markdown("<h2 style='color:white; text-align:center;'>Sovereign Terminal</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border-color:var(--border-color);'>", unsafe_allow_html=True)

nav_selection = st.sidebar.radio("Navigasyon", ["Stres Analizi", "Satıcı İstihbaratı", "Teknik Sözlük", "Tarihsel Arşiv"])

# --- Main App Execution ---
if nav_selection == "Stres Analizi":
    render_stress_analysis()
elif nav_selection == "Satıcı İstihbaratı":
    render_seller_intel()
elif nav_selection == "Teknik Sözlük":
    render_glossary()
elif nav_selection == "Tarihsel Arşiv":
    render_history()
"""

full_code = part1 + glossary_str + "\n\n" + history_code + "\n\n" + part2

with open("app.py", "w", encoding="utf-8") as f:
    f.write(full_code)

print("Final App Generated Successfully!")
