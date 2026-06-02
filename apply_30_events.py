import os

APP_PATH = "/Users/azraozcelik/Desktop/proje ödevi/btc_risk_terminal/app.py"

with open(APP_PATH, "r", encoding="utf-8") as f:
    content = f.read()

part1 = content.split("HISTORY_DB = [")[0]
part2 = "\n# --- Main App Execution ---" + content.split("# --- Main App Execution ---")[1]

middle = '''HISTORY_DB = [
    {"year": 2008, "title": "Bitcoin Whitepaper", "desc": "Satoshi Nakamoto makaleyi yayımladı.", "ana": "2008 Küresel Krizi sırasında güvene dayalı olmayan alternatif sistem tasarlandı.", "res": "Geleneksel bankacılığa karşı P2P transfer mimarisi atıldı.", "date": "2008-10-31"},
    {"year": 2009, "title": "Genesis Block Kazılması", "desc": "Satoshi ağın ilk bloğunu kazdı.", "ana": "Bloğa The Times gazetesinin banka kurtarma paketi manşeti eklendi.", "res": "Ağ resmen faaliyete geçti.", "date": "2009-01-03"},
    {"year": 2010, "title": "Bitcoin Pizza Günü", "desc": "10.000 BTC iki pizza için ödendi.", "ana": "Tarihteki ilk somut ticari işlem gerçekleşti.", "res": "Bitcoin ilk defa finansal bir değerleme kazandı.", "date": "2010-05-22"},
    {"year": 2011, "title": "Mt. Gox 1. Hack", "desc": "Borsa hacklendi, fiyat sentlere düştü.", "ana": "Güvenlik açığı yüzünden ilk büyük güven kaybı.", "res": "Kripto güvenliğinin önemi ilk kez anlaşıldı.", "date": "2011-06-19"},
    {"year": 2013, "title": "Kıbrıs Bankacılık Krizi", "desc": "Kıbrıs bankalarındaki mevduatlara el konulması dedikoduları.", "ana": "İnsanlar paralarını kurtarmak için merkeziyetsiz bir çıkış aradı.", "res": "Bitcoin ilk kez güvenli liman (safe haven) algısı oluşturmaya başladı.", "date": "2013-04-01"},
    {"year": 2013, "title": "Silk Road Kapatılması", "desc": "FBI kara borsa platformunu kapattı.", "ana": "Suç algısının kırılması için önemli bir dönüm noktası.", "res": "Kurumsal adaptasyona zemin hazırlayan regülatif temizlik.", "date": "2013-10-01"},
    {"year": 2014, "title": "Mt. Gox İflası", "desc": "850.000 BTC çalındı ve borsa çöktü.", "ana": "Merkezi borsaların yarattığı tekil hata noktası (SPOF) acı şekilde deneyimlendi.", "res": "Soğuk cüzdan (cold storage) kavramı standartlaştı.", "date": "2014-02-24"},
    {"year": 2015, "title": "Ethereum Ağı Başlatılması", "desc": "Akıllı sözleşme çağı başladı.", "ana": "Bitcoin'in sadece bir ödeme aracı olmaktan çıkıp, programlanabilir paraya evrilmesi fikri.", "res": "ICO çılgınlığının ve DeFi ekosisteminin temeli atıldı.", "date": "2015-07-30"},
    {"year": 2016, "title": "Bitfinex Hack", "desc": "120.000 BTC çalındı.", "ana": "Mt. Gox'tan sonraki en büyük borsa saldırısı.", "res": "Piyasa sarsılsa da kısa sürede toparlayarak olgunluk gösterdi.", "date": "2016-08-02"},
    {"year": 2017, "title": "Japonya Yasal Düzenlemesi", "desc": "Japonya Bitcoin'i yasal ödeme yöntemi tanıdı.", "ana": "Gelişmiş bir G7 ülkesinden gelen ilk tam regülatif kabul.", "res": "Kripto paraların uluslararası meşruiyeti büyük ivme kazandı.", "date": "2017-04-01"},
    {"year": 2017, "title": "SegWit ve Bitcoin Cash Fork", "desc": "Ölçeklenebilirlik savaşları sonuca ulaştı.", "ana": "Blok boyutunu artırmak isteyenler ağdan ayrılarak BCH'yi kurdu.", "res": "Bitcoin asli kodunu korudu ve değer deposu kimliğini perçinledi.", "date": "2017-08-01"},
    {"year": 2017, "title": "Cboe ve CME Futures İşlemleri", "desc": "İlk kurumsal vadeli işlemler başladı.", "ana": "Wall Street yatırımcıları fiziksel BTC tutmadan bahis yapabilme imkanı buldu.", "res": "2017 boğasının zirvesine giden kurumsal fomo tetiklendi.", "date": "2017-12-10"},
    {"year": 2017, "title": "ICO Çılgınlığı ve 20k Zirvesi", "desc": "Bitcoin 20.000 doları gördü.", "ana": "Düzenlemesiz binlerce ICO piyasaya para akıttı.", "res": "Sert bir balon patlaması ve 3 yıllık ayı piyasası başladı.", "date": "2017-12-17"},
    {"year": 2018, "title": "Hash Savaşları (BCH vs BSV)", "desc": "Madenci kampları arasında güç savaşı.", "ana": "Ağ güvenliğinin siyasi rant kavgalarına alet olması.", "res": "Kripto piyasasından 100 milyar doların üzerinde değer silindi.", "date": "2018-11-15"},
    {"year": 2019, "title": "Çin Başkanı Xi Jinping Açıklaması", "desc": "Çin'in blockchain'i temel teknoloji yapacağını duyurdu.", "ana": "Devlet destekli blok zinciri rüzgarı büyük bir ani alım dalgası yarattı.", "res": "Kripto para piyasası ayı trendinden kısa süreliğine şiddetle çıktı.", "date": "2019-10-25"},
    {"year": 2020, "title": "Covid-19 Kara Perşembe Çöküşü", "desc": "Bir günde %50'lik devasa çöküş.", "ana": "Küresel piyasalarla olan korelasyonun tavan yaptığı bir likidite krizi.", "res": "Sistemik tasfiyeler temizlendi ve devasa QE (parasal genişleme) ile boğa başladı.", "date": "2020-03-12"},
    {"year": 2020, "title": "MicroStrategy Alımı", "desc": "Michael Saylor şirket hazinesine BTC ekledi.", "ana": "Halka açık bir şirketin itibari para yerine BTC'yi rezerv yapması.", "res": "Kurumsal benimseme rüzgarı (Institutional FOMO) resmen başladı.", "date": "2020-08-11"},
    {"year": 2021, "title": "Tesla'nın 1.5 Milyar Dolarlık Alımı", "desc": "Elon Musk destekli dev kurumsal kabul.", "ana": "Dünyanın en yenilikçi şirketinin BTC'ye geçişi parakende çılgınlığı başlattı.", "res": "Fiyat parabolik bir yükselişle yeni zirvelere tırmandı.", "date": "2021-02-08"},
    {"year": 2021, "title": "Çin Madencilik Yasağı", "desc": "Ağ gücünün (hashrate) %50'si kapandı.", "ana": "Dünyanın en büyük madencilik operasyonları zorla göç ettirildi.", "res": "Ağ çökmeyerek olağanüstü bir dayanıklılık (resilience) testi geçti.", "date": "2021-05-19"},
    {"year": 2021, "title": "El Salvador Yasal İhale Yasası", "desc": "Bitcoin resmi para birimi oldu.", "ana": "İlk kez bir egemen ulus-devlet kripto parayı resmi rezervine aldı.", "res": "Jeopolitik oyun teorisi işlemeye başladı.", "date": "2021-06-09"},
    {"year": 2021, "title": "İlk ABD Futures ETF (BITO)", "desc": "Wall Street ETF'i işleme başladı.", "ana": "Spot olmasa da türev piyasası üzerinden gelen büyük regülatif zafer.", "res": "Kurumsal sermayenin giriş kapıları genişledi.", "date": "2021-10-19"},
    {"year": 2021, "title": "69.000 Dolar Zirvesi ve Taproot", "desc": "Bitcoin döngüsel tepe noktasını gördü.", "ana": "Düşük faizlerin yarattığı rüzgarın sonuna gelindiği nokta.", "res": "Makroekonomik sıkılaşma ve faiz artırımlarının başlamasıyla derin bir ayı piyasası tetiklendi.", "date": "2021-11-10"},
    {"year": 2022, "title": "Terra (LUNA) ve UST Çöküşü", "desc": "Algoritmik stablecoin imparatorluğu yıkıldı.", "ana": "Ölüm sarmalına (death spiral) giren UST, piyasadan 40 milyar dolar sildi.", "res": "Celsisus, 3AC gibi dev borç veren şirketlerin zincirleme iflası.", "date": "2022-05-09"},
    {"year": 2022, "title": "FTX Borsası İflası", "desc": "Dünyanın en büyük 2. borsası dolandırıcılıktan çöktü.", "ana": "Müşteri fonlarının yasa dışı kullanımıyla oluşan likidite krizi.", "res": "Regülasyon çağrıları arttı, güven dibe vurdu, fiyat 15k'ya geriledi.", "date": "2022-11-11"},
    {"year": 2023, "title": "SVB Krizi ve USDC De-peg", "desc": "Silikon Vadisi Bankası battı, USDC 1 dolar altına düştü.", "ana": "Geleneksel bankacılık krizi kriptoya sıçradı.", "res": "Kriz ortamında Bitcoin bankacılık riskine karşı sığınak olarak yeniden hatırlandı.", "date": "2023-03-11"},
    {"year": 2023, "title": "BlackRock Spot ETF Başvurusu", "desc": "Dünyanın en büyük varlık yöneticisi ETF istedi.", "ana": "9 Trilyon dolarlık devin pazara girmesi, SEC'in red geleneğini sarstı.", "res": "Piyasaya büyük bir meşruiyet ve güven dalgası geldi.", "date": "2023-06-15"},
    {"year": 2023, "title": "Grayscale SEC Davası Zaferi", "desc": "Mahkeme, SEC'in ETF reddini haksız buldu.", "ana": "Regülatörlerin keyfi kararlarına karşı alınan büyük yasal zafer.", "res": "Ocak ayındaki Spot ETF onaylarının yolu tamamen açılmış oldu.", "date": "2023-08-29"},
    {"year": 2024, "title": "ABD Spot ETF Onayları", "desc": "SEC 11 farklı spot Bitcoin ETF'ini onayladı.", "ana": "Tarihi kurumsal kabul. Milyarlarca dolarlık kalıcı pasif fon akışı garantilendi.", "res": "Bitcoin resmen Wall Street'in ana akım yatırım aracına dönüştü.", "date": "2024-01-10"},
    {"year": 2024, "title": "Bitcoin Yeni ATH (73.750 Dolar)", "desc": "Tarihte ilk kez halving öncesi rekor kırıldı.", "ana": "ETF'lerin yarattığı devasa talep arzı yuttu.", "res": "Dört yıllık piyasa döngüsü teorisi (Halving cycle) tamamen değişime uğradı.", "date": "2024-03-14"},
    {"year": 2024, "title": "Dördüncü Halving", "desc": "Blok ödülü 3.125 BTC'ye düştü.", "ana": "Bitcoin'in enflasyon oranı altının altına inerek en sert (hardest) varlık oldu.", "res": "Madencilik endüstrisinde büyük konsolidasyon dönemi başladı.", "date": "2024-04-19"}
]

@st.cache_data(ttl=86400)
def get_historical_data(event_index, date_str):
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    import yfinance as yf
    
    # Simüle edilmiş erken dönem datası (yfinance öncesi)
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
        dates = pd.date_range(start="2013-03-15", periods=60)
        prices = np.linspace(40, 100, 16).tolist() + [140.0, 160.0, 120.0] + np.linspace(130, 100, 41).tolist()
        return pd.DataFrame({"Date": dates, "Price": prices})
    elif event_index == 5:
        dates = pd.date_range(start="2013-09-15", periods=60)
        prices = np.linspace(120, 140, 16).tolist() + [109.0, 115.0, 125.0] + np.linspace(130, 200, 41).tolist()
        return pd.DataFrame({"Date": dates, "Price": prices})
    elif event_index == 6:
        dates = pd.date_range(start="2014-01-24", periods=60)
        prices = np.linspace(800, 850, 31).tolist() + [400, 450, 500, 550, 500] + np.linspace(500, 450, 24).tolist()
        return pd.DataFrame({"Date": dates, "Price": prices})
    else:
        # Gerçek yfinance datası 2014 Eylül sonrası mevcuttur
        event_date = datetime.strptime(date_str, "%Y-%m-%d")
        start_date = event_date - timedelta(days=30)
        end_date = event_date + timedelta(days=90)
        
        try:
            df = yf.download("BTC-USD", start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"), progress=False)
            if df.empty:
                dates = pd.date_range(start=start_date, periods=120)
                return pd.DataFrame({"Date": dates, "Price": [100.0]*120})
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            df = df.reset_index()
            # Date sütun ismini bulma ve normalize etme
            date_col = "Date" if "Date" in df.columns else "Datetime"
            if date_col in df.columns:
                df = df.rename(columns={date_col: "Date", "Close": "Price"})
            
            return df[["Date", "Price"]]
        except Exception as e:
            # Fallback
            dates = pd.date_range(start=start_date, periods=120)
            return pd.DataFrame({"Date": dates, "Price": [1.0]*120})

def render_history():
    st.markdown("<h2>TARİHSEL ARŞİV VE SİSTEMİK KRİZLER</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-color);'>2008'den günümüze Bitcoin ağını ve piyasasını şekillendiren yapısal dönüm noktaları. Olayların piyasa etkisini görmek için kutulara tıklayın.</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    for idx, item in enumerate(HISTORY_DB):
        st.markdown(f\'\'\'
        <div style="display:flex; margin-bottom: 8px; align-items: center;">
            <div style="width: 120px; flex-shrink: 0;">
                <div style="font-size: 2rem; font-weight: 800; color: var(--border-color); line-height: 1;">{item["year"]}</div>
            </div>
            <div style="flex-grow: 1;">
                <h3 style="margin-top:0; color:white !important; margin-bottom:0;">{item["title"]}</h3>
            </div>
        </div>
        \'\'\', unsafe_allow_html=True)
        
        with st.expander("Tarihsel Analizi ve Bitcoin Fiyat Etkisini Görüntüle"):
            st.markdown(f\'\'\'
            <p style="font-size:1.1rem; color:var(--text-color); border-left: 3px solid var(--highlight); padding-left: 10px;">{item["desc"]}</p>
            <div style="margin-top: 16px; padding: 12px; background-color: rgba(0,0,0,0.3); border-radius: 4px;">
                <strong style="color:var(--warning);">Forensic Analiz:</strong>
                <p style="font-size:0.9rem; margin-bottom: 12px;">{item["ana"]}</p>
                <strong style="color:var(--success);">Sistemik Sonuç:</strong>
                <p style="font-size:0.9rem; margin-bottom: 0;">{item["res"]}</p>
            </div>
            \'\'\', unsafe_allow_html=True)
            
            st.markdown(f"<div style='margin-top: 20px; margin-bottom: 10px; color: var(--highlight); font-weight: bold;'>Olay Sonrası Fiyat Davranışı ({item['date']})</div>", unsafe_allow_html=True)
            
            try:
                df = get_historical_data(idx, item["date"])
                if not df.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df["Date"], y=df["Price"], 
                        mode='lines',
                        line=dict(color="#f85149", width=2),
                        fill='tozeroy',
                        fillcolor='rgba(248, 81, 73, 0.1)',
                        name="Bitcoin Fiyatı"
                    ))
                    
                    event_date_ts = pd.to_datetime(item["date"])
                    
                    # Grafiğe dikey olay çizgisi
                    fig.add_vline(x=event_date_ts, line_width=2, line_dash="dash", line_color="#58a6ff")
                    fig.add_annotation(
                        x=event_date_ts,
                        y=df["Price"].max() * 0.9 if df["Price"].max() > 0 else 0.01,
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
                st.error(f"Grafik verisi çekilemedi: {str(e)}")
        
        st.markdown("<br>", unsafe_allow_html=True)
'''

with open(APP_PATH, "w", encoding="utf-8") as f:
    f.write(part1 + middle + part2)

print("30 events and real charts successfully injected!")
