import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def fetch_live_seller_intel():
    intel_data = []
    
    # 1. GBTC (Grayscale) Live Data
    try:
        gbtc = yf.Ticker("GBTC")
        hist_gbtc = gbtc.history(period="1mo")
        if not hist_gbtc.empty:
            vol_trend = hist_gbtc['Volume'].values
            price_change = ((hist_gbtc['Close'].iloc[-1] - hist_gbtc['Close'].iloc[0]) / hist_gbtc['Close'].iloc[0]) * 100
            status = "Çıkışlar Hızlanıyor" if price_change < 0 else "Dengeleniyor"
            heat = "Yüksek" if price_change < -5 else "Orta"
            
            intel_data.append({
                "name": "GBTC (Grayscale) ETF",
                "volume": f"${hist_gbtc['Volume'].iloc[-1] * hist_gbtc['Close'].iloc[-1] / 1e6:,.1f}M",
                "status": f"Canlı Piyasa: {status}",
                "heat": heat,
                "slippage": f"%{abs(price_change/10):.2f} - %{abs(price_change/5):.2f}",
                "routes": "Coinbase Prime",
                "trigger": "Canlı İşlem Hacmi ve Fiyat Volatilitesi.",
                "chart_y": vol_trend,
                "chart_title": "30 Günlük Gerçek Hacim Trendi (GBTC)"
            })
    except Exception:
        pass

    # 2. Miner Capitulation (Mempool Space Live Hashrate)
    try:
        res = requests.get("https://mempool.space/api/v1/mining/hashrate/1m")
        if res.status_code == 200:
            data = res.json()
            hashrates = [x["avgHashrate"] for x in data.get("hashrates", [])[-30:]]
            if hashrates:
                current_hr = hashrates[-1]
                avg_hr = np.mean(hashrates)
                heat = "Yüksek" if current_hr < avg_hr * 0.95 else "Orta"
                
                intel_data.append({
                    "name": "Madenci Kapitülasyonu",
                    "volume": f"{current_hr / 1e18:.1f} EH/s",
                    "status": "Ağ Üzerinden Canlı Hash Rate",
                    "heat": heat,
                    "slippage": "%1.5 - %2.5",
                    "routes": "Binance, B2B OTC",
                    "trigger": "Canlı Hash Rate'in 30 günlük ortalamanın altına düşmesi.",
                    "chart_y": hashrates,
                    "chart_title": "30 Günlük Gerçek Hash Rate Trendi"
                })
    except Exception:
        pass

    # 3. Mt. Gox & US DOJ Proxy (BTC Real Volatility)
    try:
        btc = yf.Ticker("BTC-USD")
        hist_btc = btc.history(period="1mo")
        if not hist_btc.empty:
            volatility = hist_btc['High'] - hist_btc['Low']
            current_vol = volatility.iloc[-1]
            avg_vol = volatility.mean()
            
            # Mt Gox
            intel_data.append({
                "name": "Mt. Gox & Kurumsal Cüzdanlar",
                "volume": "142,000+ BTC",
                "status": "Canlı Volatilite Proxy İzlemesi",
                "heat": "Kritik" if current_vol > avg_vol * 1.5 else "Orta",
                "slippage": f"%{(current_vol/hist_btc['Close'].iloc[-1])*100:.2f} (Canlı Tahmin)",
                "routes": "Kraken, Coinbase Prime",
                "trigger": "BTC Gerçek Volatilitesinin (ATR) ani artışı.",
                "chart_y": volatility.values,
                "chart_title": "30 Günlük BTC Gerçek Volatilite (Risk Proxy)"
            })
    except Exception:
        pass

    # Fallback if APIs fail
    if len(intel_data) == 0:
        intel_data = [
            {
                "name": "API Bağlantı Hatası",
                "volume": "Veri Yok",
                "status": "Çevrimdışı",
                "heat": "Bilinmiyor",
                "slippage": "N/A",
                "routes": "N/A",
                "trigger": "Lütfen internet bağlantınızı kontrol edin.",
                "chart_y": np.zeros(30),
                "chart_title": "Veri Yok"
            }
        ]

    return intel_data
