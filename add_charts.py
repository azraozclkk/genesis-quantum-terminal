import re
import ast

APP_PATH = "/Users/azraozcelik/Desktop/proje ödevi/btc_risk_terminal/app.py"

with open(APP_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Append yfinance to imports if not there
if "import yfinance as yf" not in content:
    content = content.replace("import streamlit as st", "import streamlit as st\nimport yfinance as yf\nfrom datetime import datetime, timedelta")

# The exact dates for the 20 events in order:
dates = [
    "2008-10-31", # Whitepaper
    "2009-01-03", # Genesis
    "2010-05-22", # Pizza
    "2011-06-19", # Mt Gox 1
    "2013-10-01", # Silk Road
    "2014-02-24", # Mt Gox 2
    "2015-07-30", # Ethereum
    "2016-08-02", # Bitfinex
    "2017-08-01", # SegWit
    "2017-12-17", # 20k
    "2018-11-15", # Hash War
    "2020-03-12", # Kara persembe
    "2020-08-11", # MicroStrategy
    "2021-05-19", # China Ban
    "2021-11-14", # Taproot
    "2022-05-09", # Terra LUNA
    "2022-11-11", # FTX
    "2023-03-11", # SVB
    "2024-01-10", # ETF
    "2024-04-19"  # Halving
]

# We must update HISTORY_DB to include these dates.
# Let's extract the current HISTORY_DB list.
history_match = re.search(r"HISTORY_DB = (\[.*?\])", content, flags=re.DOTALL)
if history_match:
    history_list = ast.literal_eval(history_match.group(1))
    
    new_history_str = "HISTORY_DB = [\n"
    for i, item in enumerate(history_list):
        item["date"] = dates[i]
        new_history_str += "    {\n"
        new_history_str += f'        "year": {item["year"]},\n'
        new_history_str += f'        "title": "{item["title"]}",\n'
        new_history_str += f'        "desc": "{item["desc"]}",\n'
        new_history_str += f'        "ana": "{item["ana"]}",\n'
        new_history_str += f'        "res": "{item["res"]}",\n'
        new_history_str += f'        "date": "{item["date"]}"\n'
        new_history_str += "    }"
        if i < len(history_list) - 1:
            new_history_str += ",\n"
        else:
            new_history_str += "\n"
    new_history_str += "]"
    
    content = content.replace(history_match.group(0), new_history_str)

# Inject the get_historical_data function right before render_history
func_def = """
@st.cache_data(ttl=86400)
def get_historical_data(event_index, date_str):
    if event_index == 0:
        dates = pd.date_range(start="2008-10-01", periods=60)
        return pd.DataFrame({"Date": dates, "Price": [0.0]*60})
    elif event_index == 1:
        dates = pd.date_range(start="2009-01-01", periods=60)
        return pd.DataFrame({"Date": dates, "Price": [0.0]*60})
    elif event_index == 2:
        dates = pd.date_range(start="2010-05-01", periods=60)
        prices = [0.003] * 21 + [0.0041] * 10 + [0.005] * 29
        return pd.DataFrame({"Date": dates, "Price": prices})
    elif event_index == 3:
        dates = pd.date_range(start="2011-06-01", periods=60)
        prices = np.linspace(10, 32, 18).tolist() + [0.01, 2.0, 5.0, 10.0, 15.0] + np.linspace(15, 14, 37).tolist()
        return pd.DataFrame({"Date": dates, "Price": prices})
    elif event_index == 4:
        dates = pd.date_range(start="2013-09-15", periods=60)
        prices = np.linspace(120, 140, 16).tolist() + [109.0, 115.0, 125.0] + np.linspace(130, 200, 41).tolist()
        return pd.DataFrame({"Date": dates, "Price": prices})
    elif event_index == 5:
        dates = pd.date_range(start="2014-01-24", periods=60)
        prices = np.linspace(800, 850, 31).tolist() + [400, 450, 500, 550, 500] + np.linspace(500, 450, 24).tolist()
        return pd.DataFrame({"Date": dates, "Price": prices})
    else:
        event_date = datetime.strptime(date_str, "%Y-%m-%d")
        start_date = event_date - timedelta(days=30)
        end_date = event_date + timedelta(days=90)
        df = yf.download("BTC-USD", start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"), progress=False)
        if df.empty:
            dates = pd.date_range(start=start_date, periods=120)
            return pd.DataFrame({"Date": dates, "Price": [1000.0]*120})
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df = df.reset_index()
        df = df.rename(columns={"index": "Date", "Datetime": "Date", "Close": "Price"})
        return df[["Date", "Price"]]

def render_history():"""

content = content.replace("def render_history():", func_def)

# Replace the body of render_history
old_render_history_body = """    st.markdown("<h2>TARİHSEL ARŞİV VE SİSTEMİK KRİZLER</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-color);'>2008'den günümüze Bitcoin ağını ve piyasasını şekillendiren yapısal dönüm noktaları.</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Vertical timeline style
    for item in HISTORY_DB:
        st.markdown(f\"\"\"
        <div style="display:flex; margin-bottom: 24px;">
            <div style="width: 120px; flex-shrink: 0;">
                <div style="font-size: 2rem; font-weight: 800; color: var(--border-color); line-height: 1;">{item['year']}</div>
                <div style="width: 2px; height: 100%; background-color: var(--border-color); margin-left: 20px; margin-top: 10px;"></div>
            </div>
            <div class="card" style="flex-grow: 1; margin-bottom: 0;">
                <h3 style="margin-top:0; color:white !important;">{item['title']}</h3>
                <p style="font-size:1.1rem; color:var(--text-color); border-left: 3px solid var(--highlight); padding-left: 10px;">{item['desc']}</p>
                <div style="margin-top: 16px; padding: 12px; background-color: rgba(0,0,0,0.3); border-radius: 4px;">
                    <strong style="color:var(--warning);">Forensic Analiz:</strong>
                    <p style="font-size:0.9rem; margin-bottom: 12px;">{item['ana']}</p>
                    <strong style="color:var(--success);">Sistemik Sonuç:</strong>
                    <p style="font-size:0.9rem; margin-bottom: 0;">{item['res']}</p>
                </div>
            </div>
        </div>\"\"\", unsafe_allow_html=True)"""

new_render_history_body = """    st.markdown("<h2>TARİHSEL ARŞİV VE SİSTEMİK KRİZLER</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-color);'>2008'den günümüze Bitcoin ağını ve piyasasını şekillendiren yapısal dönüm noktaları. Olayların piyasa etkisini görmek için kartlara tıklayın.</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    for idx, item in enumerate(HISTORY_DB):
        st.markdown(f'''
        <div style="display:flex; margin-bottom: 8px; align-items: center;">
            <div style="width: 120px; flex-shrink: 0;">
                <div style="font-size: 2rem; font-weight: 800; color: var(--border-color); line-height: 1;">{item["year"]}</div>
            </div>
            <div style="flex-grow: 1;">
                <h3 style="margin-top:0; color:white !important; margin-bottom:0;">{item["title"]}</h3>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.expander("Tarihsel Analizi ve Fiyat Etkisini Görüntüle"):
            st.markdown(f'''
            <p style="font-size:1.1rem; color:var(--text-color); border-left: 3px solid var(--highlight); padding-left: 10px;">{item["desc"]}</p>
            <div style="margin-top: 16px; padding: 12px; background-color: rgba(0,0,0,0.3); border-radius: 4px;">
                <strong style="color:var(--warning);">Forensic Analiz:</strong>
                <p style="font-size:0.9rem; margin-bottom: 12px;">{item["ana"]}</p>
                <strong style="color:var(--success);">Sistemik Sonuç:</strong>
                <p style="font-size:0.9rem; margin-bottom: 0;">{item["res"]}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f"<div style='margin-top: 20px; color: var(--highlight); font-weight: bold;'>Piyasa Fiyatı Üzerindeki Etkisi ({item['date']})</div>", unsafe_allow_html=True)
            try:
                df = get_historical_data(idx, item["date"])
                if not df.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df["Date"], y=df["Price"], 
                        mode='lines',
                        line=dict(color="#f85149", width=2),
                        fill='tozeroy',
                        fillcolor='rgba(248, 81, 73, 0.1)'
                    ))
                    
                    event_date_ts = pd.to_datetime(item["date"])
                    fig.add_vline(x=event_date_ts, line_width=2, line_dash="dash", line_color="#58a6ff")
                    fig.add_annotation(
                        x=event_date_ts,
                        y=df["Price"].max() if df["Price"].max() > 0 else 0.01,
                        text="Olay Günü",
                        showarrow=True,
                        arrowhead=1,
                        ax=-40,
                        ay=-40,
                        font=dict(color="#58a6ff")
                    )
                    
                    fig.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#c9d1d9"),
                        margin=dict(l=0, r=0, t=10, b=10),
                        height=300,
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor="#1f2937", title="Fiyat (USD)")
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Grafik yüklenirken hata oluştu: {str(e)}")
        
        st.markdown("<br>", unsafe_allow_html=True)"""

content = content.replace(old_render_history_body, new_render_history_body)

with open(APP_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Charts successfully added to app.py")
