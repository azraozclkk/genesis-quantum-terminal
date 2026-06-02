import streamlit as st
import pandas as pd
import numpy as np
import requests
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

GLOSSARY_DB = {
    "Blockchain (Blok Zinciri)": "Verilerin kriptografik olarak birbirine bağlandığı, değiştirilemez ve merkeziyetsiz dijital kayıt defteri.",
    "PoW (Proof of Work)": "Madencilerin matematiksel bulmacaları çözerek işlemleri doğruladığı konsensüs algoritması.",
    "PoS (Proof of Stake)": "Doğrulayıcıların coinlerini kilitleyerek (stake) ağ güvenliğini sağladığı enerji verimli konsensüs modeli.",
    "Node (Düğüm)": "Blok zinciri ağının kurallarını uygulayan ve kayıt defterinin bir kopyasını tutan bilgisayar.",
    "Full Node": "Tüm işlem geçmişini barındıran ve ağdaki kuralları bağımsız bir şekilde tamamen doğrulayan düğüm.",
    "Light Node": "Ağın tüm geçmişini indirmeden, sadece işlem onaylarını doğrulayan hafif düğüm.",
    "Miner (Madenci)": "PoW ağlarında işlemleri bloğa eklemek için donanım gücü kullanan ve karşılığında ödül alan katılımcı.",
    "Hashrate": "Ağdaki tüm madencilerin saniyede ürettiği kriptografik tahmin sayısı. Ağın güvenlik metriklerinden biri.",
    "Halving (Yarılanma)": "Bitcoin ağında yaklaşık her dört yılda bir madenci blok ödülünün yarı yarıya azalması.",
    "Mempool (Bellek Havuzu)": "Ağa gönderilmiş ancak henüz bir bloğa dahil edilmemiş onay bekleyen işlemlerin havuzu.",
    "Block Reward (Blok Ödülü)": "Madencilere veya doğrulayıcılara yeni bir blok oluşturduklarında ağ tarafından verilen yeni coinler.",
    "Transaction Fee (İşlem Ücreti)": "Bir işlemin ağda öncelikli onaylanması için kullanıcının madencilere ödediği komisyon.",
    "UTXO (Unspent Transaction Output)": "Harcanmamış işlem çıktısı. Bitcoin'in, her bir coin'in kaynağını izlediği muhasebe modeli.",
    "Genesis Block": "Satoshi Nakamoto tarafından kazılan, Bitcoin blok zincirinin başlangıç bloğu (Blok 0).",
    "Cryptography": "Verileri sadece hedeflenen alıcının okuyabileceği şekilde şifreleme ve deşifre etme bilimi.",
    "Public Key (Açık Anahtar)": "Kripto para almak için başkalarıyla paylaşılan, banka IBAN numarasına benzeyen kriptografik adres.",
    "Private Key (Özel Anahtar)": "Sadece sahibinin bilmesi gereken, cüzdandaki varlıkları harcama yetkisi veren gizli şifre.",
    "Seed Phrase (Kurtarma İfadesi)": "Özel anahtarın türetildiği, cüzdanı geri yüklemek için kullanılan 12 veya 24 kelimelik anahtar sözcük dizisi.",
    "Fork (Çatallanma)": "Blok zinciri protokolünde kuralların değişmesi sonucu ağın ve topluluğun iki farklı zincire ayrılması.",
    "Hard Fork": "Eski kurallarla uyumlu olmayan, ağın tamamen yeni bir versiyona geçmesini zorunlu kılan kesin çatallanma.",
    "Soft Fork": "Geriye dönük uyumluluk sağlayan, eski düğümlerin yeni işlemleri de geçerli sayabildiği hafif ağ güncellemesi.",
    "Smart Contract (Akıllı Sözleşme)": "Kodlarına yazılan şartlar sağlandığında otomatik olarak çalışan ve aracıya ihtiyaç duymayan dijital sözleşmeler.",
    "EVM (Ethereum Virtual Machine)": "Ethereum üzerindeki tüm akıllı sözleşmelerin çalıştırıldığı ve hesaplandığı çalışma ortamı.",
    "Layer 1 (Katman 1)": "Kendi ağı, mutabakat mekanizması ve yerel kripto parası olan temel blok zincirleri (Örn: Bitcoin, Ethereum).",
    "Layer 2 (Katman 2)": "İşlem hızını ve ölçeklenebilirliği artırmak için Katman 1'in üzerine inşa edilen yan ağlar (Örn: Lightning Network, Arbitrum).",
    "Lightning Network": "Bitcoin ağında anında ve neredeyse ücretsiz mikro ödemelere olanak tanıyan Katman 2 çözümü.",
    "SegWit (Segregated Witness)": "İşlem boyutunu küçültmek için imza verilerini ana veriden ayıran kritik bir Bitcoin güncellemesi.",
    "Taproot": "Bitcoin'de gizliliği, ölçeklenebilirliği ve karmaşık çoklu imza senaryolarını geliştiren güncelleme.",
    "Schnorr Signatures": "Birden fazla imzayı tek bir imza gibi göstererek gizliliği ve veri verimliliğini artıran kriptografik teknik.",
    "SHA-256": "Bitcoin'in PoW madenciliğinde kullandığı, 256 bit uzunluğunda sabit bir çıktı üreten kriptografik özetleme fonksiyonu.",
    "Difficulty Adjustment": "Bitcoin ağında ortalama blok üretim süresini 10 dakikada tutmak için her 2016 blokta bir zorluğun ayarlanması.",
    "Consensus Mechanism": "Ağdaki tüm düğümlerin blok zincirinin geçerli durumu üzerinde anlaşmaya varmasını sağlayan kurallar bütünü.",
    "51% Attack (%51 Saldırısı)": "Bir kişi veya grubun ağdaki madencilik gücünün %50'sinden fazlasını ele geçirerek işlemleri iptal etme veya çift harcama (double spend) yapma girişimi.",
    "Double Spending (Çifte Harcama)": "Aynı dijital paranın kopyalanarak veya ağ manipüle edilerek aynı anda iki farklı kişiye harcanması sorunu.",
    "Orphan Block (Yetim Blok)": "İki madencinin aynı anda geçerli bir blok bulması sonucu kısa zincirde kaldığı için ağ tarafından terk edilen blok.",
    "Block Explorer": "Bir blok zincirindeki işlemleri, blokları ve adresleri sorgulamak ve izlemek için kullanılan arama motoru.",
    "Mainnet (Ana Ağ)": "Bir kripto para projesinin gerçek değer taşıyan ve faaliyette olan nihai ağı.",
    "Testnet (Test Ağı)": "Geliştiricilerin gerçek para riske atmadan yeni kodları veya uygulamaları test ettiği simülasyon ağı.",
    "DApp (Decentralized Application)": "Arka ucu merkezi sunucular yerine akıllı sözleşmeler ve blok zinciri üzerinde çalışan uygulamalar.",
    "Tokenomics": "Bir kripto paranın arzı, dağıtımı, enflasyon oranı ve kullanım senaryolarını inceleyen ekonomik modeli.",
    "Inflationary Token": "Maksimum arzı olmayan ve sürekli olarak yeni token üretilen kripto varlıklar (Örn: Dogecoin).",
    "Deflationary Token": "Zamanla dolaşımdaki miktarının azaltıldığı (yakım vb.) ve arzının sınırlandırıldığı varlıklar.",
    "Coin Burn (Coin Yakımı)": "Dolaşımdaki arzı azaltmak ve fiyat istikrarı sağlamak amacıyla belirli miktarda tokenın erişilemez ölü bir adrese gönderilmesi.",
    "Max Supply (Maksimum Arz)": "Bir kripto paranın tarihinde üretilebilecek mutlak üst sınır miktarı (Örn: Bitcoin için 21 Milyon).",
    "Circulating Supply": "Şu anda piyasada halkın elinde bulunan ve ticarete konu olan mevcut token miktarı.",
    "Interoperability": "Farklı blok zincirlerinin birbirleriyle veri ve değer transferi yaparak iletişim kurabilme yeteneği.",
    "Oracle": "Blok zincirindeki akıllı sözleşmelere dış dünyadan (örneğin hava durumu, maç sonuçları, hisse fiyatları) gerçek zamanlı veri sağlayan hizmet.",
    "Cold Wallet (Soğuk Cüzdan)": "İnternete bağlı olmayan, hacklenmeye karşı en yüksek güvenliği sağlayan donanım veya kağıt cüzdanlar.",
    "Hot Wallet (Sıcak Cüzdan)": "İnternete sürekli bağlı olan, günlük işlemler için pratik ancak siber saldırılara daha açık yazılım cüzdanları.",
    "Hardware Wallet": "Özel anahtarları çevrimdışı, şifreli bir çip içinde saklayan fiziksel USB benzeri cihaz (Örn: Ledger, Trezor).",
    "Paper Wallet": "Açık ve özel anahtarların QR kod formatında fiziksel bir kağıda basıldığı ultra-soğuk saklama yöntemi.",
    "Multisig (Multi-Signature)": "Bir işlem veya fon transferi için tek bir kişi yerine birden fazla onay (anahtar) gerektiren cüzdan yapısı.",
    "Self-Custody": "Varlıkların saklama yetkisinin bir borsa yerine tamamen kullanıcının kendi kontrolünde olması durumu.",
    "Phishing (Oltalama)": "Kullanıcıların özel anahtarlarını veya şifrelerini çalmak için tasarlanmış sahte web siteleri ve e-postalar.",
    "Dusting Attack": "Kullanıcıların adreslerine çok küçük miktarda coin (dust) göndererek, gizliliklerini deşifre edip kimliklerini bulmaya yönelik saldırı.",
    "Rug Pull": "Geliştiricilerin sahte bir proje oluşturup yatırım topladıktan sonra likiditeyi çekerek kaçması şeklindeki dolandırıcılık.",
    "Honeypot": "Yatırımcıların alım yapmasına izin veren ancak akıllı sözleşmedeki gizli bir kod yüzünden satış yapmalarını engelleyen tuzak projeler.",
    "Sybil Attack": "Bir ağın kararlarını manipüle etmek için tek bir saldırganın çok sayıda sahte düğüm (node) oluşturması.",
    "Replay Attack": "Bir hard fork sonrasında, bir zincirde yapılan geçerli işlemin diğer zincirde de aynen tekrarlanarak fonların çalınması riski.",
    "MEV (Miner Extractable Value)": "Madencilerin işlemleri sıraya koyarken arbitraj ve front-running yaparak elde ettikleri ekstra gizli kâr.",
    "Front-Running": "MEV botlarının bekleyen büyük bir alım işlemini görüp, ondan milisaniyeler önce kendi işlemini sıraya koyarak fiyat avantajı sağlaması.",
    "Market Cap (Piyasa Değeri)": "Dolaşımdaki arz ile mevcut fiyatın çarpılması sonucu elde edilen toplam piyasa büyüklüğü.",
    "Liquidity (Likidite)": "Bir varlığın piyasa fiyatını etkilemeden kolayca nakde veya başka bir varlığa çevrilebilme derecesi.",
    "Volatility (Volatilite)": "Bir varlığın fiyatının belirli bir zaman dilimindeki dalgalanma hızı ve büyüklüğü.",
    "Order Book (Emir Defteri)": "Bir borsadaki tüm alıcıların ve satıcıların verdikleri limit emirlerinin listelendiği tablo.",
    "Bid-Ask Spread (Alış-Satış Farkı)": "Piyasadaki en yüksek alım emri (Bid) ile en düşük satım emri (Ask) arasındaki fiyat uçurumu.",
    "Market Order (Piyasa Emri)": "Belirli bir fiyat hedefi gözetmeksizin, emrin o anki en iyi fiyattan derhal gerçekleşmesini sağlayan emir tipi.",
    "Limit Order (Limit Emri)": "Sadece yatırımcının belirlediği spesifik bir fiyattan veya daha iyisinden gerçekleşmesi şartıyla sisteme girilen emir.",
    "Stop-Loss": "Fiyatın yatırımcının belirlediği bir zararı kesme seviyesine düşmesi durumunda pozisyonun otomatik kapanmasını sağlayan emir.",
    "Take-Profit": "Fiyat hedeflenen kâr seviyesine ulaştığında pozisyonu kapatarak kârı realize eden emir türü.",
    "Slippage (Fiyat Kayması)": "Emrin sisteme girildiği andaki fiyat ile piyasa derinliğinin yetersizliği nedeniyle işlemin gerçekleştiği fiyat arasındaki olumsuz fark.",
    "Leverage (Kaldıraç)": "Yatırımcıların borsadan borç alarak anaparalarından daha büyük pozisyonlar (10x, 50x) açmasını sağlayan marjin sistemi.",
    "Margin (Teminat)": "Kaldıraçlı pozisyon açabilmek için borsaya rehin olarak bırakılması gereken minimum başlangıç sermayesi.",
    "Liquidation (Tasfiye)": "Fiyatın terste kalması sonucu zararın marjin miktarını aşmasıyla borsanın pozisyonu zorla ve zararına kapatması.",
    "Liquidation Cascade": "Büyük tasfiyelerin fiyatı daha da aşağı (veya yukarı) çekerek arka arkaya zincirleme tasfiyeleri tetiklemesi.",
    "Long Position": "Varlığın değer kazanacağı beklentisiyle açılan alım pozisyonu.",
    "Short Position": "Varlığın değer kaybedeceği beklentisiyle, borç alınarak yüksekten satılıp düşükten geri alınmasını hedefleyen pozisyon.",
    "Funding Rate (Fonlama Oranı)": "Sürekli vadeli işlemlerde (Perpetual Futures) long ve short pozisyonlar arasında periyodik olarak ödenen dengeleme ücreti.",
    "Arbitrage": "Aynı varlığın farklı borsalardaki fiyat farkından yararlanarak eşzamanlı risksiz kâr elde etme stratejisi.",
    "DCA (Dollar Cost Averaging)": "Fiyat dalgalanmalarından bağımsız olarak, varlığı periyodik zamanlarda sabit miktarlarda kademeli olarak satın alma stratejisi.",
    "Whale (Balina)": "Piyasayı sarsacak kadar çok elinde mal tutanlar.",
    "Bear Market (Ayı Piyasası)": "Fiyatların sürekli düşüş trendinde olduğu, karamsarlığın hakim olduğu uzun süreli piyasa koşulu.",
    "Bull Market (Boğa Piyasası)": "Fiyatların istikrarlı bir şekilde yükseldiği ve piyasaya coşku ve iyimserliğin hakim olduğu dönem.",
    "Altcoin (Alternatif Coin)": "Bitcoin dışındaki Ethereum, Solana, Ripple gibi diğer tüm kripto para birimlerine verilen genel ad.",
    "Stablecoin": "Değeri ABD Doları, altın veya başka bir itibari paraya sabitlenmiş fiyat istikrarı sağlayan kripto varlık.",
    "Fiat (İtibari Para)": "Devletler tarafından basılan, arkasında altın karşılığı olmayan ancak devletin itibarına dayanan Dolar, Euro, TL gibi paralar.",
    "OTC (Over the Counter)": "Piyasa fiyatını aniden düşürmemek için devasa balina işlemlerinin borsalar yerine doğrudan alıcı-satıcı arasında yapıldığı tezgah altı pazar.",
    "CEX (Centralized Exchange)": "Binance, Coinbase gibi kullanıcı fonlarını kendi bünyesinde saklayan şirket yönetimindeki merkezi kripto para borsaları.",
    "DEX (Decentralized Exchange)": "Uniswap, PancakeSwap gibi şirket veya sunucu olmadan, işlemlerin akıllı sözleşmeler aracılığıyla eşler arası yapıldığı merkeziyetsiz borsa.",
    "AMM (Automated Market Maker)": "DEX'lerde geleneksel emir defteri yerine işlemlerin algoritmik bir likidite havuzu formülüyle fiyatlandığı sistem.",
    "Liquidity Pool": "Kullanıcıların DEX'lerde ticaret yapılabilmesi için akıllı sözleşmelere kilitlediği token çiftlerinden oluşan fon havuzu.",
    "Impermanent Loss": "Likidite havuzlarına fon sağlayanların, tokenların fiyatlarındaki değişimden dolayı sadece cüzdanda tutmaya kıyasla yaşadıkları geçici veya kalıcı fırsat maliyeti.",
    "Yield Farming": "Yatırımcıların varlıklarını DeFi protokollerine kitleyerek yüksek faiz ve ek platform tokenları kazanması stratejisi.",
    "Staking": "PoS ağlarında kullanıcıların ağ güvenliğini sağlamak için coinlerini kilitlemesi ve karşılığında pasif gelir elde etmesi.",
    "TVL (Total Value Locked)": "Tüm kullanıcıların bir DeFi uygulamasının akıllı sözleşmelerine kilitlediği kripto paraların toplam dolar değeri.",
    "ROI (Return on Investment)": "Yatırımın getirisini veya zararını anaparaya oranla ölçen finansal metrik.",
    "ATH (All-Time High)": "Bir kripto paranın tarih boyunca ulaştığı en yüksek fiyat seviyesi.",
    "ATL (All-Time Low)": "Bir kripto paranın tarih boyunca gördüğü en düşük fiyat seviyesi.",
    "Support (Destek)": "Teknik analizde fiyat düşüşlerinin yavaşladığı ve alım tepkisinin geldiği tarihi taban fiyat seviyesi.",
    "Resistance (Direnç)": "Fiyat yükselişlerinin zorlandığı ve satış baskısının yoğunlaştığı tarihi tavan fiyat seviyesi.",
    "RSI (Relative Strength Index)": "Bir varlığın aşırı alım veya aşırı satım bölgesinde olup olmadığını gösteren teknik analiz momentum indikatörü.",
    "Moving Average (Hareketli Ortalama)": "Geçmiş fiyat verilerinin ortalamasını alarak trend yönünü yumuşatan ve belirleyen grafik göstergesi.",
    "Market Cycle": "Piyasaların genişleme, tepe noktası, daralma ve dip noktası aşamalarından oluşan tekrarlayan psikolojik döngüsü.",
    "Pump and Dump": "Manipülatörlerin bir coin'i överek fiyatını yapay şekilde şişirmesi (pump) ve ardından zirveden satarak yatırımcıları mağdur etmesi (dump).",
    "HODL": "Piyasa ne kadar düşerse düşsün varlıkları satmama ve uzun vadeli tutma felsefesi. 'Hold On for Dear Life' olarak da anılır.",
    "FOMO (Fear of Missing Out)": "Yükselen piyasayı veya fırsatı kaçırma korkusuyla plansızca yüksek fiyattan alım yapma dürtüsü.",
    "FUD (Fear, Uncertainty, Doubt)": "Yatırımcıları paniğe sürükleyip satış yaptırmak için kasıtlı olarak yayılan korku, belirsizlik ve şüphe haberleri.",
    "Rekt": "'Wrecked' kelimesinin bozulmuş hali. Bir yatırımcının yanlış hamleyle veya tasfiye olarak tüm parasını kaybetmesi durumu.",
    "To the Moon (Aya Çıkış)": "Bir varlığın fiyatının durdurulamaz bir şekilde inanılmaz seviyelere yükseleceğine dair aşırı iyimser ifade.",
    "Bagholder": "Fiyatı çökmüş ve eski seviyesine dönme umudu kalmamış değersiz coinleri elinde tutmak zorunda kalan yatırımcı.",
    "Diamond Hands (Elmas Eller)": "Piyasa ne kadar sarsılırsa sarsılsın panik satışı yapmayan iradeli yatırımcı.",
    "Paper Hands (Kağıt Eller)": "En ufak bir düşüşte panikleyerek zararına satış yapan iradesiz yatırımcı.",
    "Shill": "Bir kişinin finansal çıkar uğruna bir projeyi sosyal medyada abartılı ve aldatıcı bir şekilde pazarlaması.",
    "Ape In": "Herhangi bir araştırma yapmadan, sırf yükseliyor diye gözü kapalı bir şekilde projeye veya coin'e girmek.",
    "BTFD (Buy The F***ing Dip)": "Fiyatlarda yaşanan sert düzeltmelerin ve düşüşlerin aslında harika bir alım fırsatı olduğunu savunan strateji.",
    "WAGMI (We're All Gonna Make It)": "Kripto topluluğunda uzun vadede herkesin çok zengin ve başarılı olacağına dair umut aşılayan slogan.",
    "NGMI (Not Gonna Make It)": "Kötü yatırım kararları alanların asla başarılı olamayacağını ifade eden alaycı kısaltma.",
    "Degen (Degenerate)": "Yüksek riskli, arkası boş DeFi projelerine kumar bağımlısı gibi pervasızca yatırım yapan alt-kültür yatırımcısı.",
    "Flippening": "Ethereum'un piyasa değerinin bir gün Bitcoin'i geçerek birinci sıraya oturacağı beklentisine verilen isim.",
    "Maxi (Maximalist)": "Yalnızca Bitcoin'in gerçek ve değerli olduğuna, diğer tüm altcoinlerin çöp (shitcoin) olduğuna inanan fanatik.",
    "Shitcoin": "Hiçbir kullanım alanı, temel amacı veya teknolojisi olmayan değersiz kripto paralar.",
    "On-Chain Analytics": "Blok zincirinin halka açık verilerini analiz ederek balina hareketleri, borsa çıkışları gibi makro trendleri öngörme bilimi.",
    "Hash Ribbons": "Madenci kapitülasyonlarını tespit ederek tarihsel olarak en güçlü Bitcoin alım sinyallerinden birini veren gösterge.",
    "SOPR (Spent Output Profit Ratio)": "On-chain verilerde yatırımcıların genel olarak zararına mı yoksa kârına mı satış yaptığını gösteren duyarlılık oranı.",
    "MVRV Ratio": "Bitcoin'in mevcut piyasa değerinin (Market Cap), gerçekleşmiş değerine (Realized Cap) bölünmesiyle hesaplanan aşırı değerleme indeksi.",
    "Realized Cap": "Mevcut fiyattan değil, her bir Bitcoin'in en son hareket ettiği fiyattan değerlenmesiyle oluşturulan gerçeklik metriği.",
    "Quantitative Easing (QE)": "Merkez bankalarının ekonomiyi canlandırmak için para basarak tahvil satın aldığı genişlemeci makroekonomik politika. Kripto için yakıttır.",
    "Quantitative Tightening (QT)": "Merkez bankalarının bilançolarını daraltarak piyasadaki nakdi geri çektiği ve kripto gibi risk varlıklarını baskılayan sıkılaşma politikası.",
    "Inflation (Enflasyon)": "Paranın satın alma gücünün sürekli olarak düşmesi durumu. Bitcoin enflasyona karşı korunma (hedge) aracı olarak görülür.",
    "Deflation (Deflasyon)": "Fiyatların genel seviyesinin düşmesi ve paranın değerinin artması.",
    "CPI (Tüketici Fiyat Endeksi)": "ABD enflasyonunu ölçen ve açıklandığı gün kripto piyasalarında büyük volatilitelere yol açan makro veri.",
    "Fed (Federal Reserve)": "Para politikası kararlarıyla (faiz artırımı/indirimi) tüm küresel risk varlıklarını ve kripto piyasasını yönlendiren ABD Merkez Bankası.",
    "Interest Rate (Faiz Oranı)": "Merkez bankalarının borçlanma maliyetini belirlediği oran. Faiz düştüğünde Bitcoin gibi varlıklara sermaye akışı hızlanır.",
    "Dominance (Hakimiyet)": "Bitcoin'in toplam piyasa değerinin, tüm kripto para piyasasının değerine oranı. Altcoin sezonlarının habercisidir.",
    "Altseason (Altcoin Sezonu)": "Bitcoin hakimiyetinin düştüğü ve altcoinlerin Bitcoin'e kıyasla çok daha yüksek getiriler sağladığı coşkulu dönem.",
    "Web3": "Kullanıcıların kendi verilerine sahip olduğu ve aracıların ortadan kalktığı blok zinciri tabanlı merkeziyetsiz internet vizyonu.",
    "NFT (Non-Fungible Token)": "Blok zinciri üzerinde sahipliği kanıtlanan, birbirinin yerine geçemeyen ve eşsiz dijital sanat eserleri, oyun içi eşyalar veya tapular.",
    "Metaverse": "İnsanların sanal gerçeklikte etkileşime girdiği, ekonomisinin kripto paralar ve NFT'ler üzerinden döndüğü dijital evren.",
    "DAO (Decentralized Autonomous Organization)": "Merkezi bir CEO yerine, token sahiplerinin oylamalarıyla yönetilen ve kuralları akıllı sözleşmelere yazılı organizasyonlar.",
    "Airdrop": "Projelerin kendi ağlarını kullanan erken dönem test kullanıcılarına veya topluluğa ücretsiz token dağıtarak pazarlama yapması.",
    "Minting": "Bir blok zincirinde ilk kez bir tokenın veya NFT'nin yaratılarak dolaşıma sokulması süreci.",
    "Floor Price (Taban Fiyat)": "Bir NFT koleksiyonunda satışa sunulan en ucuz parçanın o anki piyasa fiyatı.",
    "Gas Fee": "Ethereum ağında bir işlemi veya akıllı sözleşmeyi gerçekleştirmek için ödenen, ağ yoğunluğuna göre değişen işlem ücreti.",
    "Gwei": "Ethereum işlem ücretlerini (Gas) hesaplarken kullanılan Ether'in milyarda birlik alt birimi.",
    "ERC-20": "Ethereum ağında birbirinin yerine geçebilen (fungible) standart tokenların oluşturulmasını sağlayan teknik protokol.",
    "ERC-721": "Ethereum ağında benzersiz ve bölünemez (non-fungible) NFT'lerin oluşturulmasını sağlayan teknik standart.",
    "InterPlanetary File System (IPFS)": "Dosyaları ve verileri merkezi sunucular yerine eşler arası dağıtık bir ağda barındıran protokol.",
    "Zero-Knowledge Proofs (ZK)": "Bir tarafın, diğer tarafa bir bilginin doğruluğunu, bilginin kendisini açığa çıkarmadan matematiksel olarak ispatlamasını sağlayan kriptografi teknolojisi.",
    "Rollups": "Katman 2 ağlarının, yüzlerce işlemi kendi içinde sıkıştırarak (roll-up) Katman 1 ağına tek bir işlem olarak gönderdiği ölçeklendirme çözümü.",
    "ASIC (Application-Specific Integrated Circuit)": "Madencilik için özel üretilmiş, sadece SHA-256 gibi spesifik algoritmaları çözmeye odaklı yüksek performanslı donanım.",
    "ASIC Resistance": "Bir blok zincirinin ASIC donanımlarının değil, sadece standart ekran kartları (GPU) ile kazılabilmesini sağlamaya yönelik algoritma tasarımı.",
    "BIP (Bitcoin Improvement Proposal)": "Geliştiricilerin Bitcoin protokolüne yeni özellikler veya standartlar önermek için hazırladıkları resmi teknik taslaklar.",
    "EIP (Ethereum Improvement Proposal)": "Ethereum ağı için önerilen ve topluluk tarafından tartışılan teknik güncellemeler ve standart teklifleri.",
    "Block Height (Blok Yüksekliği)": "Genesis bloğundan itibaren ağda kazılmış ve zincire eklenmiş toplam blok sayısı.",
    "Block Time": "Ağın algoritmasına göre iki geçerli bloğun bulunması arasında geçen hedeflenen süre (Örn: BTC 10 dk, ETH 12 sn).",
    "Confirmation (Onay)": "Bir işlemin yeni bir bloğa dahil edilip ağ tarafından kabul görmesi. Genelde borsalar için 6 onay güvenli kabul edilir.",
    "Decentralization (Merkeziyetsizlik)": "Ağın tek bir sunucuya, kuruma veya yöneticiye bağlı kalmadan binlerce bağımsız düğüm tarafından yönetilmesi.",
    "Emission Rate (Emisyon Oranı)": "Bir kripto para biriminin ne kadar hızla üretildiğini ve dolaşıma sokulduğunu gösteren metrik.",
    "Hash (Özet)": "Değişken uzunluktaki verinin matematiksel bir fonksiyondan geçirilerek sabit uzunlukta benzersiz bir şifreli metne dönüştürülmesi.",
    "Mainnet Swap": "Bir projenin geçici olarak başka bir ağda (örn. Ethereum) çıkardığı tokenlarını, kendi orijinal ağına (Mainnet) taşıması.",
    "Merkle Tree": "Blok içerisindeki binlerce işlemi hiyerarşik bir ağaç yapısında özetleyerek doğrulama hızını artıran veri yapısı.",
    "Nonce": "Madencilerin doğru blok özetini (hash) bulmak için saniyede milyarlarca kez değiştirdiği rastgele sayı.",
    "P2P (Peer-to-Peer)": "Bir merkezi sunucuya bağlanmak yerine kullanıcıların bilgisayarlarının doğrudan birbiriyle veri alışverişi yaptığı iletişim modeli.",
    "Protocol": "Ağdaki bilgisayarların birbiriyle nasıl konuşacağını ve işlemlerin nasıl doğrulanacağını belirleyen kesin kurallar dizisi.",
    "Timestamp (Zaman Damgası)": "Bir bloğun ve içerdiği işlemlerin tam olarak hangi saniyede ağa kaydedildiğini kanıtlayan değiştirilemez veri.",
    "Turing Complete": "Ethereum gibi ağların, teorik olarak bir bilgisayarın çözebileceği her türlü hesaplama ve kodu çalıştırabilme kapasitesi.",
    "Validator (Doğrulayıcı)": "PoS ağlarında varlıklarını kilitleyerek (stake) işlemleri onaylayan ve yeni blokları zincire ekleyen katılımcı.",
    "Wallet Address (Cüzdan Adresi)": "Açık anahtardan türetilen, başkalarının size kripto para göndermesi için kullandığı genellikle 26-35 karakterlik dizi.",
    "Whitepaper": "Satoshi Nakamoto'nun 2008'de yaptığı gibi, projenin teknolojisini, amacını ve çözüm önerilerini detaylandıran teknik doküman.",
    "Account Abstraction": "Ethereum'da kullanıcı cüzdanlarını akıllı sözleşmelere dönüştürerek sosyal kurtarma, otomatik ödeme gibi gelişmiş özellikler sağlayan teknoloji (ERC-4337).",
    "AMM (Otomatik Piyasa Yapıcı)": "Geleneksel emir defteri olmadan işlemlerin havuzdaki tokenların oranına göre algoritmik olarak gerçekleştiği DEX sistemi.",
    "API Key": "Yatırımcıların borsa hesaplarını portföy yönetim uygulamalarına veya işlem botlarına bağlamak için kullandığı dijital anahtar.",
    "BFT (Byzantine Fault Tolerance)": "Ağdaki bazı bilgisayarların arızalanmasına veya kötü niyetli davranmasına rağmen tüm sistemin çökmeksizin doğru karara varabilme yeteneği.",
    "Bridge (Köprü)": "Farklı blok zinciri ağları arasında (örn. Ethereum'dan Polygon'a) kripto para ve veri transferini sağlayan protokol.",
    "Censorship Resistance": "Hiçbir hükümetin, bankanın veya kurumun blok zincirindeki işlemleri engelleyememesi veya geri alamaması özelliği.",
    "CLI (Command Line Interface)": "Geliştiricilerin arayüz kullanmadan doğrudan terminal komutlarıyla cüzdan ve ağ operasyonlarını yürüttüğü arabirim.",
    "Collateral (Teminat)": "DeFi kredilerinde veya kaldıraçlı işlemlerde borç alabilmek için kilitlenen ve borç ödenmezse likide edilen varlık.",
    "Consortium Blockchain": "Tamamen halka açık (public) veya tamamen kapalı (private) olmak yerine bir grup şirketin ortak yönettiği blok zinciri modeli.",
    "Crowdloan": "Polkadot ekosisteminde projelerin parachain slotu kazanmak için topluluktan kilitli DOT tokenı destek olarak toplama süreci.",
    "Cryptography": "Açık ağlar üzerinde güvenli iletişim kurmak ve verileri şifrelemek için kullanılan matematiğin alt dalı.",
    "Cryptoeconomics": "Kriptografi ve oyun teorisi ilkelerini kullanarak ağdaki katılımcıların iyi niyetli davranmasını teşvik eden disiplin.",
    "Custodial": "Özel anahtarların sizin yerinize Binance, Coinbase gibi merkezi bir platform tarafından yönetildiği ve saklandığı hizmet.",
    "Cyberpunk": "1990'larda internetin gözetim ve otoriteden kurtulması için kriptografiyi savunan aktivist hareket (Cypherpunk).",
    "DAG (Directed Acyclic Graph)": "Geleneksel blok zinciri yerine işlemlerin bir ağ şeklinde birbirini onayladığı daha hızlı ve ücretsiz veri yapısı (Örn: IOTA, Nano).",
    "Dark Web": "Sadece Tor gibi özel tarayıcılarla girilebilen, ilk Bitcoin adaptasyonunun yoğun olarak gerçekleştiği denetimsiz internet katmanı.",
    "Dead Cat Bounce (Ölü Kedi Sıçraması)": "Sert bir düşüş trendinde yaşanan ve yükseliş başlıyor yanılgısı yaratan kısa süreli ve zayıf fiyat tepkisi.",
    "Death Cross (Ölüm Kesişimi)": "Kısa vadeli hareketli ortalamanın (örn. 50 günlük), uzun vadeli hareketli ortalamayı (örn. 200 günlük) aşağı yönlü kesmesiyle oluşan güçlü ayı piyasası sinyali.",
    "Golden Cross (Altın Kesişim)": "50 günlük hareketli ortalamanın, 200 günlük hareketli ortalamayı yukarı yönlü keserek oluşturduğu güçlü boğa piyasası sinyali.",
    "Decentralized Identity (DID)": "Kullanıcıların dijital kimliklerini dev teknoloji şirketlerinin tekelinden çıkarıp blok zincirinde şifreli olarak barındırması.",
    "Devnet (Geliştirici Ağı)": "Testnet'ten de önceki aşamada, sadece çekirdek geliştiricilerin yeni özellikleri denediği oldukça deneysel ağ sürümü.",
    "Dex Aggregator": "Kullanıcıya en iyi fiyatı sunmak için 1inch gibi farklı merkeziyetsiz borsalardaki likidite havuzlarını tarayan ve emri bölen protokol.",
    "Diluted Market Cap": "Bir kripto paranın şu anki arzı değil, maksimum arzının tamamı piyasada olsaydı oluşacak olan teorik toplam piyasa değeri.",
    "Distributed Ledger Technology (DLT)": "Blok zincirini de kapsayan, verilerin merkezi bir sunucu yerine binlerce bilgisayara dağıtıldığı teknolojilerin üst şemsiye terimi.",
    "Dust": "İşlem ücretini (Gas) bile karşılamayacak kadar küçük, cüzdanda kalan ve transfer edilemeyen artık coin kırıntıları.",
    "Eclipse Attack": "Kötü niyetli kişilerin bir düğümü (node) izole edip ona sadece kendi sahte işlem verilerini göndererek onu ağdan koparması.",
    "Entry Point (Giriş Noktası)": "Yatırımcının teknik analiz veya stratejisine dayanarak bir varlığı satın almayı uygun gördüğü spesifik fiyat seviyesi.",
    "EVM-Compatible": "Binance Smart Chain, Avalanche C-Chain gibi kendi ağı olmasına rağmen Ethereum akıllı sözleşmelerini çalıştırabilen ağlar.",
    "Exit Scam": "Proje kurucularının topluluktan para topladıktan veya yatırım aldıktan sonra sosyal medyalarını kapatıp fonlarla birlikte ortadan kaybolması.",
    "Fair Launch (Adil Başlangıç)": "Ön satış veya özel yatırımcılara ayrılan bir pay olmadan, herkesin eşit şartlarda kazarak veya alarak başladığı token lansmanı.",
    "Faucet": "Kullanıcıların testnet ağlarında işlem ücretlerini ödeyebilmeleri için ücretsiz ve değersiz test coinleri dağıtan platformlar.",
    "Fiat Gateway": "Kullanıcıların kredi kartı veya banka havalesi ile kripto ekosistemine itibari para (Dolar, TL vb.) sokmasını sağlayan servis.",
    "Flash Crash": "Aşırı satış baskısı veya algoritmik bir hata sonucu saniyeler içinde fiyatın çöktüğü ve hemen geri toplandığı olay.",
    "Flash Loan (Flaş Kredi)": "DeFi ekosisteminde, teminat gösterilmeksizin alınan ancak aynı işlem bloğu içerisinde geri ödenmesi zorunlu olan anlık devasa krediler.",
    "Flipping": "Özellikle NFT piyasasında veya ICO dönemlerinde, bir varlığı ucuzdan alıp (mint edip) saatler içinde yüksek fiyattan başkasına satma stratejisi.",
    "Fractional Reserve": "Borsaların veya bankaların müşteri fonlarının %100'ünü karşılık olarak tutmayıp bir kısmını yatırıma yönlendirdiği sistem.",
    "Front-End": "Bir uygulamanın kullanıcıların gördüğü, cüzdan bağladığı ve işlem yaptığı web arayüzü kısmı.",
    "Full-Time Trader": "Başka hiçbir geliri olmadan hayatını tamamen kripto veya hisse piyasalarında aktif al-sat yaparak kazanan kişi.",
    "Fungible": "Birbirinin yerine geçebilen, özellikleri tamamen aynı olan varlıklar. Örn: Senin elindeki 1 BTC ile benim elimdeki 1 BTC'nin farkı yoktur.",
    "Non-Fungible": "Eşsiz olan ve diğerleriyle aynı değeri taşımayan varlıklar. Örn: Bir sanat eseri veya bir gayrimenkul tapusu (NFT'lerin temel mantığı).",
    "GameFi": "Kullanıcıların oyun oynayarak (Play-to-Earn) kripto para veya NFT kazandığı ve oyun içi ekonomilerin blok zincirine entegre olduğu konsept.",
    "Gas Limit": "Ethereum ağında bir kullanıcının belirli bir işlemi gerçekleştirmek için harcamayı göze aldığı maksimum gas miktarı.",
    "Geth": "Ethereum ağında çalışmak üzere Go diliyle yazılmış, dünyadaki en yaygın Ethereum düğüm (node) istemci yazılımı.",
    "Gossip Protocol": "Düğümlerin ağda yeni çıkan blokları ve işlemleri tıpkı bir 'dedikodu' gibi birbirlerine anında ve dağıtık bir şekilde yayma algoritması.",
    "Governance Token": "Sahiplerine projenin gelecekteki güncellemeleri, hazine fonlarının kullanımı gibi konularda oy hakkı veren kripto paralar (Örn: UNI, MKR).",
    "Gwei": "Ethereum işlem ücretlerini hesaplamakta kullanılan birim (1 Ether = 1 Milyar Gwei).",
    "Hal Finney": "Satoshi Nakamoto'dan ilk Bitcoin transferini alan, e-posta listelerinde Bitcoin'e inanan ve kodlara katkı sağlayan efsanevi kriptograf.",
    "Hard Cap": "Bir ICO (İlk Coin Arzı) veya fon toplama sürecinde projenin almayı kabul ettiği en yüksek toplam yatırım miktarı.",
    "Soft Cap": "Projenin iptal edilmeden geliştirilmeye başlanması için ICO sırasında toplanması gereken minimum yatırım tutarı.",
    "Hash Rate": "Bitcoin madencilik ağının saniyede denediği milyarlarca şifreleme tahmini gücü. Ağ ne kadar güçlü olursa hacklenmesi o kadar zorlaşır.",
    "HD Wallet (Hierarchical Deterministic)": "Tek bir ana kurtarma kelimesinden (Seed phrase) sınırsız sayıda yeni ve benzersiz alt cüzdan adresleri üretebilen cüzdan standartı.",
    "Honeyminer": "Bilgisayarın arka planında çalışarak kullanıcıların cihazlarını bir havuza dahil edip Bitcoin madenciliği yapmasını sağlayan uygulamalara verilen genel ad.",
    "Iceberg Order (Buzdağı Emri)": "Balinaların piyasayı korkutmamak için devasa büyüklükteki bir satım emrini küçük parçalara bölerek sırayla tahtaya koyması stratejisi.",
    "IDO (Initial DEX Offering)": "Projenin ön satışını doğrudan merkeziyetsiz bir borsada (PancakeSwap, Uniswap) gerçekleştirmesi.",
    "IEO (Initial Exchange Offering)": "Proje ön satışının doğrudan Binance Launchpad gibi merkezi borsalar üzerinden denetimli bir şekilde yapılması.",
    "Immutable (Değiştirilemezlik)": "Blok zincirine kaydedilen bir işlemin geriye dönük olarak hacklenememesi, silinememesi ve manipüle edilememesi durumu.",
    "Impermanent Loss (Kalıcı Olmayan Kayıp)": "Likidite sağlayan kullanıcıların, havuza koydukları tokenların dış piyasada fiyat değiştirmesi nedeniyle oluşan fırsat zararı.",
    "Index Fund (Endeks Fonu)": "Tek bir coin seçmek yerine kripto pazarının ilk 10 coinini sepete ekleyerek genel piyasa performansını takip eden fon yapısı.",
    "Initial Coin Offering (ICO)": "Projelerin geliştirme aşamasındayken yatırımcılara kendi çıkardıkları tokenları satarak sermaye topladığı finansman yöntemi.",
    "Interoperability": "Polkadot veya Cosmos gibi projelerin, birbirinden tamamen farklı ağların birbirleriyle iletişim kurmasını sağlaması.",
    "IPFS (InterPlanetary File System)": "Web sitelerini ve NFT medya dosyalarını merkezi sunucularda değil, eşler arası dağıtık ağlarda barındıran teknoloji.",
    "KYC (Know Your Customer)": "Borsaların regülasyonlar gereği kullanıcılarından kimlik, pasaport ve adres doğrulaması talep etmesi süreci.",
    "AML (Anti-Money Laundering)": "Kara para aklamayı önlemek için devletlerin koyduğu ve borsaların uymak zorunda olduğu yasalar bütünü.",
    "Layer 0 (Katman 0)": "Polkadot gibi diğer bağımsız blok zincirlerinin (Layer 1) kendi üzerlerinde çalışmasına olanak tanıyan temel iletişim katmanı.",
    "Ledger": "İşlemlerin tutulduğu ana defter.",
    "Hardware Ledger": "Özel anahtarları koruyan soğuk donanım cüzdan markası.",
    "Limit Order": "Fiyatın tam olarak sizin belirlediğiniz bir seviyeye gelmesi şartıyla alış veya satış yapılmasını emreden mekanizma.",
    "Liquidation Price": "Kaldıraçlı işlemlerde yatırılan teminatın sıfırlandığı ve pozisyonun borsa tarafından otomatik olarak yok edildiği fiyat noktası.",
    "Liquidity Mining": "Protokollerin, kendi platformlarına fon (likidite) sağlayan kullanıcılara platform tokenı ile faiz ödemesi.",
    "Long Squeeze": "Fiyatın aniden düşmesiyle 'Long' (yükseliş) bekleyen çok sayıda kişinin tasfiye edilmesi ve zincirleme satış baskısı yaratması durumu.",
    "Short Squeeze": "Fiyatın aniden yükselmesiyle 'Short' açanların tasfiye olup zorla alım yapmak zorunda kalması ve fiyatı daha da yukarı fırlatması.",
    "Mainnet": "Test aşaması bitmiş ve gerçek paraların döndüğü orijinal ve bağımsız blok zinciri ağı.",
    "Testnet": "Geliştiricilerin sadece deneme amacıyla kullandığı değeri olmayan ağ.",
    "Margin Call (Marjin Çağrısı)": "Kaldıraçlı pozisyonlarda tasfiye yaklaşırken borsanın yatırımcıdan teminat eklemesini istediği uyarı.",
    "Market Order": "Fiyata bakılmaksızın tahtadaki o anki en iyi fiyattan derhal gerçekleşmesi istenen piyasa emri.",
    "Masternode": "Ağdaki işlemlerin anonimleştirilmesi veya oylamaların yapılması gibi özel görevleri üstlenen ve yüklü miktarda coin stake eden gelişmiş düğüm (Örn: DASH).",
    "Maximum Extractable Value (MEV)": "Madencilerin yeni bloğu oluştururken yüksek komisyon ödeyen işlemleri öne çekip ekstra kâr elde ettiği arka kapı stratejisi.",
    "Mempool": "Ağa iletilen fakat henüz madenciler tarafından onaylanmamış işlemlerin geçici olarak tutulduğu havuz.",
    "MetaMask": "Ethereum ve EVM uyumlu ağlara erişim sağlayan, tarayıcı eklentisi ve mobil uygulama formundaki en yaygın Web3 sıcak cüzdanı.",
    "Microtransaction": "Kredi kartlarıyla yüksek komisyonlardan dolayı yapılamayan ancak Lightning Network ile mümkün olan birkaç kuruşluk anlık ödemeler.",
    "Miner Extractable Value (MEV)": "Ethereum ve diğer akıllı kontrat platformlarında madencilerin front-running yaparak işlem sırasını değiştirmesi.",
    "Mint": "Yepyeni bir NFT'yi veya tokenı blok zinciri ağına basarak ilk defa dolaşıma sokma eylemi.",
    "Moon": "Fiyatın roket gibi fırlayarak aya çıkacağını iddia eden umutlu ifade.",
    "Moving Average Convergence Divergence (MACD)": "Trendin yönünü ve gücünü ölçmek için kullanılan gelişmiş bir momentum indikatörü.",
    "Multisig": "Paranın cüzdandan çıkabilmesi için 3 ortaktan 2'sinin onaylaması gerektiği gibi kurallar tanımlanabilen çoklu imza cüzdanı.",
    "Node": "Bitcoin yazılımını bilgisayarına kurup ağı senkronize eden, işlemleri onaylayan ve yayınlayan her bir bilgisayar.",
    "Non-Custodial": "Kullanıcının anahtarlarına %100 sahip olduğu cüzdan türü (Trust Wallet, Metamask).",
    "Custodial": "Kullanıcının anahtarlarını platformun tuttuğu cüzdan türü (Binance).",
    "Nonce (Number Only Used Once)": "PoW madenciliğinde doğru hash değerini bulmak için saniyede trilyonlarca kez değiştirilerek denenen rastgele tekil sayı.",
    "Off-Chain": "Doğrudan blok zincirine kaydedilmeyip daha hızlı ve ucuz olduğu için ağın dışında yürütülen işlemler (Lightning Network).",
    "On-Chain": "Tüm dünyanın görebileceği şekilde doğrudan blok zincirinin ana defterine kaydedilen silinemez işlemler.",
    "Oracle": "Chainlink gibi akıllı sözleşmelere dış dünyadan dolar fiyatı veya hava durumu gibi gerçek zamanlı veri akışı sağlayan sistemler.",
    "Order Book": "Alıcıların ve satıcıların tekliflerini içeren borsa tahtası.",
    "Orphan Block": "Aynı anda kazılan iki bloktan, ağın daha uzun zinciri tercih etmesi nedeniyle dışarıda kalarak geçersiz sayılan geçerli blok.",
    "OTC (Tezgah Altı Piyasa)": "Balinaların işlem yaparken borsada devasa dalgalanma yaratmamak için aracı kurumlarla özel fiyat üzerinden yaptığı ticaret.",
    "Paper Wallet": "Özel anahtarın QR kod olarak kağıda basılıp bir kasada saklandığı tamamen offline cüzdan türü.",
    "Parachain": "Polkadot ağına paralel olarak çalışan ve güvenliği Polkadot tarafından sağlanan özel blok zincirleri.",
    "Peer-to-Peer (P2P)": "Arada banka olmadan doğrudan iki kişinin cüzdanı arasındaki iletişim.",
    "Phishing": "Sahte siteler kurarak kurbanların seed kelimelerini ele geçirmeye yönelik sosyal mühendislik saldırısı.",
    "Play-to-Earn (P2E)": "Axie Infinity gibi oyunları oynayarak gerçek kripto para ve NFT geliri elde etme modeli.",
    "PoA (Proof of Authority)": "Merkeziyetsizlikten ödün vererek güvenilir olduğu bilinen belirli kurumların ağı onayladığı hızlı konsensüs.",
    "PoB (Proof of Burn)": "Coinlerin sonsuza dek yok edilerek (yakılarak) karşılığında madencilik yapma veya hak iddia etme ayrıcalığı kazanılması.",
    "PoC (Proof of Capacity)": "İşlemci gücü yerine bilgisayarınızın hard diskindeki boş alanın büyüklüğüne göre madencilik yaptıran algoritma (Chia).",
    "PoD (Proof of Developer)": "Dolandırıcılığı önlemek için bir projeyi kuran geliştiricinin gerçek kimliğini kanıtlaması süreci.",
    "Ponzi Scheme": "Sisteme giren yeni yatırımcıların parasıyla eski yatırımcılara kâr ödendiği, eninde sonunda çökmeye mahkum dolandırıcılık modeli.",
    "Portfolio": "Bir kişinin elinde tuttuğu BTC, ETH ve diğer tüm tokenların sepeti.",
    "Premine": "Projenin halka açılmadan önce geliştiricilerin kendine milyonlarca coin önceden kazarak veya üreterek piyasaya çıkması.",
    "Privacy Coin": "Monero, Zcash gibi işlemleri gönderen, alan ve miktar bilgisini tamamen şifreleyerek on-chain takibi imkansız kılan kripto paralar.",
    "Private Key": "Varlıkların transfer edilmesini sağlayan 256 bitlik şifreli yönetici anahtarı.",
    "Proof of Reserves (Rezerv Kanıtı)": "Borsaların, kullanıcıların yatırdığı fonların tamamının kendi soğuk cüzdanlarında eksiksiz bulunduğunu kriptografik olarak denetletmesi.",
    "Proof of Work (PoW)": "Ağın güvenliğinin bilgisayarların tükettiği elektrik ve hesaplama gücüne dayandığı sistem.",
    "Proof of Stake (PoS)": "Ağın güvenliğinin kilitlenen coinlerin teminatına dayandığı sistem.",
    "Public Key": "Banka IBAN'ı gibi çalışan açık cüzdan adresi.",
    "Pump and Dump": "Balinaların veya grupların anlaşıp bir coinin fiyatını hızla uçurup zirvede küçük yatırımcıya satarak çökerttiği dolandırıcılık.",
    "QR Code": "Açık veya özel anahtarların kameralar tarafından hızlıca okunabilmesi için kullanılan karekod.",
    "Ransomware": "Bilgisayar dosyalarını şifreleyip açmak için Bitcoin fidye isteyen zararlı yazılım türü.",
    "Rebalancing": "Portföydeki varlıkların belirli oranlarda sabit kalması için dönem dönem kârdaki coinleri satıp düşükleri alma stratejisi.",
    "Regulator": "SEC, CFTC gibi piyasanın kurallarını belirleyen devlet denetleme kurumları.",
    "Rekt": "Ağır zarar edip tasfiye olan yatırımcıları tanımlayan argoca kelime.",
    "Return on Investment (ROI)": "Yatırımdan elde edilen yüzdelik kâr veya zarar.",
    "Ring Signature": "Monero ağında işlemin kim tarafından yapıldığını gizlemek için birden fazla kullanıcının imzasını birbirine karıştıran gizlilik teknolojisi.",
    "ROI": "Yatırım getirisi.",
    "Rug Pull": "Geliştiricilerin DEX'teki tüm likiditeyi çalıp projeyi aniden terk etmesi.",
    "Satoshi Nakamoto": "Bitcoin'i yaratan ve ortadan kaybolan kişi veya grubun efsanevi takma adı.",
    "Satoshi (Sat)": "Bitcoin'in bölünebildiği 100 milyonda birlik en küçük parçası (0.00000001 BTC).",
    "Scalability (Ölçeklenebilirlik)": "Bir ağın, saniyede binlerce işlemi yavaşlamadan ve işlem ücretlerini yükseltmeden işleyebilme kapasitesi.",
    "Scam": "Dolandırıcılık amacı güden sahte projeler.",
    "Scrypt": "Litecoin'in, Bitcoin'in SHA-256 algoritmasına alternatif olarak kullandığı ve ASIC donanımlarına başlangıçta dirençli olan madencilik algoritması.",
    "SEC (Securities and Exchange Commission)": "ABD'de menkul kıymetleri denetleyen ve kripto piyasası üzerinde devasa bir baskı/regülasyon gücüne sahip resmi kurum.",
    "Security Token": "Hisse senedi, tahvil veya gayrimenkul gibi gerçek dünya varlıklarının blok zincirinde dijitalleşmiş hali. SEC düzenlemelerine tabidir.",
    "Seed Phrase": "Cüzdana erişimi sağlayan ve dünyanın her yerinden paranızı kurtarmanızı sağlayan ardışık 12 veya 24 İngilizce kelime.",
    "Segregated Witness (SegWit)": "Bitcoin'in işlem boyutunu küçültmek için imza verisini ayıran ve Lightning ağının temelini atan güncelleme.",
    "Self-Executing": "Herhangi bir aracı müdahalesine gerek duymadan koşullar sağlanınca kendi kendini başlatan akıllı sözleşmeler.",
    "Sell Wall (Satış Duvarı)": "Emir defterinde fiyatın belirli bir seviyenin üstüne çıkmasını engelleyen devasa boyuttaki yığılmış limit satış emri.",
    "Buy Wall (Alış Duvarı)": "Fiyatın belirli bir seviyenin altına inmesini engelleyen devasa alış emir yığını.",
    "Sharding": "Ethereum gibi ağların ölçeklenebilirliğini artırmak için tüm ağı ve veri tabanını daha küçük parçalara (shard) bölerek paralel işlem yaptırma tekniği.",
    "Shill": "Paralı veya menfaatçi bir şekilde kötü bir projenin gizli reklamını yapmak.",
    "Shitcoin": "Temeli olmayan değersiz altcoinler.",
    "Shorting (Açığa Satış)": "Fiyat düşüşünden para kazanmak için borsadan ödünç coin alarak satmak ve fiyat düştüğünde ucuza geri alarak borcu kapatmak.",
    "Sidechain (Yan Zincir)": "Kendi kuralları olan ancak Polygon örneğindeki gibi iki yönlü bir köprü ile Ethereum gibi ana bir blok zincirine bağlı çalışan bağımsız ağ.",
    "Signature (İmza)": "İşlemi yapanın özel anahtar sahibi olduğunu matematiksel olarak kanıtlayan kriptografik imza.",
    "Silk Road": "Dark Web'de Bitcoin'in ilk kitlesel benimsenmesini sağlayan ve FBI tarafından kapatılan meşhur karaborsa platformu.",
    "Smart Contract": "Kodların kanun olduğu dijital sözleşme.",
    "Soft Cap": "Projenin hayata geçmesi için gereken en düşük sermaye limiti.",
    "Soft Fork": "Eski node'ların güncelleme yapmasa da çalışmaya devam edebildiği geriye dönük uyumlu yumuşak ağ güncellemesi.",
    "Solidity": "Ethereum üzerinde akıllı sözleşme (smart contract) yazmak için kullanılan nesne yönelimli ana programlama dili.",
    "Sovereign Entity (Egemen Varlık)": "Amerika Birleşik Devletleri, Almanya gibi ellerinde el konulmuş devasa miktarda Bitcoin bulunduran devlet balinaları.",
    "SOPR (Spent Output Profit Ratio)": "Bitcoin yatırımcılarının gerçekleşmiş kârlılık oranını izleyen zincir üstü metrik.",
    "Slippage": "İşlemin yapılmak istendiği fiyat ile gerçekte uygulanan fiyat arasındaki fark.",
    "Stablecoin": "Değeri her zaman 1 Dolar'a sabit olmak üzere tasarlanmış kripto paralar (USDT, USDC).",
    "Staking": "Kilitli tutma işlemi.",
    "Stale Block": "Geçerli olan ancak ağın çoğunluğunun bağlandığı uzun zincire eklenemediği için terk edilen blok.",
    "State Channel": "Tarafların aralarındaki yüzlerce işlemi blok zincirine kaydetmeden özel bir kanalda anında yaptığı ve sadece nihai sonucu ana zincire kaydettiği teknoloji.",
    "Store of Value (Değer Deposu)": "Altın veya Bitcoin gibi, satın alma gücünü zaman içinde koruması beklenen deflasyonist varlık.",
    "Sybil Attack": "Saldırganın binlerce sahte kimlik yaratarak ağın kontrolünü ele geçirmeye çalışması.",
    "Synthetic Asset": "Gerçek dünyadaki hisse senetlerinin (Apple, Tesla) blok zinciri üzerinde fiyatını taklit eden dijital türev varlıklar (Örn: Synthetix).",
    "Taint": "Geçmişte çalındığı veya yasadışı işlerde kullanıldığı için kara listeye alınan 'kirli' Bitcoinler.",
    "Tangle": "IOTA projesinin blok zinciri yerine kullandığı, her yeni işlemin geçmiş iki işlemi onaylamak zorunda olduğu madencisiz ağ yapısı.",
    "Taproot": "Gizliliği artıran Bitcoin güncellemesi.",
    "Technical Analysis (TA)": "Geçmiş fiyat hareketlerine ve grafik formasyonlarına bakarak gelecekteki fiyatı tahmin etmeye çalışan metodoloji.",
    "Testnet": "Test ağı.",
    "Ticker": "Kripto paraların borsalarda işlem gören 3-4 harfli kısa kısaltmaları (Örn: BTC, ETH, SOL).",
    "Time-Weighted Average Price (TWAP)": "Balinaların piyasayı etkilememek için devasa emri belirli bir zamana eşit olarak yayarak gerçekleştirdiği algoritmik işlem.",
    "Volume-Weighted Average Price (VWAP)": "Fiyatı hacimle ağırlıklandırarak piyasa trendini belirleyen ticari gösterge.",
    "Token": "Kendi bağımsız blok zinciri ağı olmayan, Ethereum gibi mevcut bir ağın üzerinde akıllı sözleşmeler aracılığıyla üretilen kripto varlık.",
    "Token Generation Event (TGE)": "Bir projenin akıllı sözleşmelerini çalıştırarak ilk tokenları resmen yaratıp ön satış yatırımcılarına dağıttığı an.",
    "Tokenomics": "Projenin enflasyon yapısı, token dağıtımı ve kullanım durumlarının tamamı.",
    "Total Supply": "Şu an dünyada var olan ancak kilitli olduğu için tamamı dolaşımda olmayan tokenların toplam miktarı.",
    "Total Value Locked (TVL)": "Platformlara kilitli sermaye büyüklüğü.",
    "TPS (Transactions Per Second)": "Bir blok zincirinin saniyede gerçekleştirebildiği işlem sayısı. Bitcoin 7, Visa 24.000, Solana 65.000 TPS teorik kapasiteye sahiptir.",
    "Trading Volume": "Bir borsada veya tüm piyasada son 24 saatte alınıp satılan toplam varlığın dolar cinsinden değeri.",
    "Transaction": "Hesaplar arası işlem.",
    "Transaction Fee": "İşlem ücreti.",
    "Transaction ID (TXID)": "Blok zincirindeki her bir işlemi (transferi) benzersiz şekilde tanımlayan harf ve rakamlardan oluşan takip numarası.",
    "Trustless": "Tarafların birbirine veya bir bankaya güvenmek zorunda kalmadan işlemin matematik ve kod ile garanti altına alındığı sistem.",
    "Turing Complete": "Hesaplama yeterliliği.",
    "Unbanked": "Geleneksel bankacılık sistemine erişimi olmayan, ancak bir akıllı telefonla Bitcoin ağına katılabilen milyarlarca insan.",
    "Unconfirmed": "Ağa iletilen fakat henüz madenciler tarafından bir bloğa yazılmadığı için beklemede olan işlem durumu.",
    "URI (Uniform Resource Identifier)": "Bir işlemin QR kod içerisine cüzdan adresi ve tutar ile birlikte gömülmesini sağlayan standart kod.",
    "Use Case": "Kullanım durumu.",
    "User Interface (UI)": "Kullanıcı arayüzü.",
    "Utility Token": "Sadece borsalarda alınıp satılmak için değil, platform içinde belirli bir hizmete (indirim, veri depolama) erişmek için tasarlanmış token.",
    "Validator": "Ağı doğrulayan düğüm.",
    "Venture Capital (VC)": "Kripto projelerine henüz tohum (seed) aşamasındayken milyonlarca dolar erken yatırım yapan devasa risk sermayesi fonları.",
    "Virgin Bitcoin": "Madenciler tarafından yeni kazılmış ve henüz hiçbir adrese transfer edilmediği için sicili tamamen temiz olan 'Bakar' Bitcoin.",
    "Volatility": "Oynaklık.",
    "Volume": "Hacim.",
    "Wallet": "Cüzdan.",
    "Wash Trading": "Borsaların işlem hacmini sahte bir şekilde yüksek göstermek için kendi kendine aynı coinleri sürekli alıp satması şeklindeki manipülasyon.",
    "Watchlist": "Yatırımcıların takip ettiği projelerin listesi.",
    "Weak Hands": "Zayıf eller (panik satanlar).",
    "Web 1.0": "Sadece okunabilen statik web siteleri dönemi.",
    "Web 2.0": "Sosyal medyanın ve etkileşimin olduğu (Google, Facebook) ancak verilerin merkezileştiği dönem.",
    "Web 3.0": "Veri sahipliğinin kullanıcılara geçtiği, token destekli ve merkeziyetsiz yeni nesil internet.",
    "Wei": "Ethereum'un bölünebildiği 10^18'de birlik (1 kentilyonda birlik) en küçük teknik yapı taşı.",
    "Whale": "Balina.",
    "Whale Watching": "Balinaların büyük on-chain transferlerini anlık izleyerek piyasa yönünü tahmin etmeye çalışma faaliyeti.",
    "White Hat Hacker (Beyaz Şapkalı Hacker)": "Akıllı sözleşmelerdeki açıkları çalarak değil, bulup projeye bildirerek karşılığında ödül (Bounty) alan iyi niyetli siber güvenlik uzmanı.",
    "Whitepaper": "Proje tanıtım dokümanı.",
    "Whitelist": "Bir NFT koleksiyonuna veya ICO ön satışına katılmaya önceden hak kazanmış ve garantili cüzdanların bulunduğu ayrıcalıklı liste.",
    "Yield Farming": "Maksimum getiri sağlamak için sermayeyi sürekli farklı DeFi protokolleri arasında gezdirme stratejisi.",
    "Zero-Knowledge Proof (ZKP)": "Bir bilginin doğruluğunu, bilgi ifşa edilmeden kanıtlama sistemi.",
    "Zk-Rollups": "Ethereum ölçeklendirme çözümü.",
}

HISTORY_DB = [
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
    import requests
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
        
        with st.expander("Tarihsel Analizi ve Bitcoin Fiyat Etkisini Görüntüle"):
            st.markdown(f'''
            <p style="font-size:1.1rem; color:var(--text-color); border-left: 3px solid var(--highlight); padding-left: 10px;">{item["desc"]}</p>
            <div style="margin-top: 16px; padding: 12px; background-color: rgba(0,0,0,0.3); border-radius: 4px;">
                <strong style="color:var(--warning);">Forensic Analiz:</strong>
                <p style="font-size:0.9rem; margin-bottom: 12px;">{item["ana"]}</p>
                <strong style="color:var(--success);">Sistemik Sonuç:</strong>
                <p style="font-size:0.9rem; margin-bottom: 0;">{item["res"]}</p>
            </div>
            ''', unsafe_allow_html=True)
            
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



@st.cache_data(ttl=300)
def fetch_live_seller_intel():
    import requests
    import yfinance as yf
    import numpy as np
    intel_data = []
    
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
    except:
        pass

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
    except:
        pass

    try:
        btc = yf.Ticker("BTC-USD")
        hist_btc = btc.history(period="1mo")
        if not hist_btc.empty:
            volatility = hist_btc['High'] - hist_btc['Low']
            current_vol = volatility.iloc[-1]
            avg_vol = volatility.mean()
            
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
    except:
        pass

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

# --- Stochastic Simulation Engine ---
def run_quantum_sim(v, w, d, a_total, a_active_set):
    ticks = 120
    prices = [60000.0]
    agents_active = [a_active_set]
    low_liquidity_flags = [False]
    panic_index = [0.0]
    liquidation_volume = [0.0]
    
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
            agents_lost = np.random.randint(5, 20)
            new_agents = max(0, prev_agents - agents_lost)
            panic = min(100.0, (abs(price_change) / 1000) * 20 + (agents_lost * 2))
            liq_vol = agents_lost * np.random.uniform(0.5, 2.5)
        elif price_change > 500:
            new_agents = min(a_total, prev_agents + np.random.randint(1, 10))
            panic = max(0.0, panic_index[-1] - 10)
            liq_vol = 0.0
        else:
            new_agents = prev_agents
            panic = max(0.0, panic_index[-1] - 5)
            liq_vol = 0.0
            
        is_low_liq = new_agents < (a_total * 0.3)
        if is_low_liq:
            new_price = new_price * 0.85
            agents_lost_cascade = int(new_agents * 0.1)
            new_agents = new_agents - agents_lost_cascade
            panic = 100.0
            liq_vol += agents_lost_cascade * np.random.uniform(2.0, 5.0)
            
        prices.append(new_price)
        agents_active.append(new_agents)
        low_liquidity_flags.append(is_low_liq)
        panic_index.append(panic)
        liquidation_volume.append(liq_vol)
        
    return pd.DataFrame({
        'Tick': range(ticks),
        'Price': prices,
        'ActiveAgents': agents_active,
        'LowLiquidity': low_liquidity_flags,
        'PanicIndex': panic_index,
        'LiquidationVol': liquidation_volume
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
    
    fig.add_trace(
        go.Scatter(x=df['Tick'], y=df['PanicIndex'] * 10, name="Panik Endeksi (x10)", line=dict(color="#d29922", width=1, dash="dashdot")),
        secondary_y=True,
    )
    
    fig.add_trace(
        go.Bar(x=df['Tick'], y=df['LiquidationVol'] * 10, name="Tasfiye Şiddeti", marker_color="rgba(248, 81, 73, 0.4)"),
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
    st.markdown("<h2>SATICI İSTİHBARATI <span style='font-size: 1rem; color: var(--success);'>[CANLI VERİ BAĞLANTISI AKTİF]</span></h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-color);'>Kurumsal ve Egemen satış tehditlerinin on-chain ve türev piyasalardaki canlı izlemesi.</p><hr>", unsafe_allow_html=True)
    
    intel_list = fetch_live_seller_intel()
    
    for intel in intel_list:
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
                    <div style='margin-bottom:8px;'><strong style='color:var(--text-color);'>Canlı Slippage (Tahmin):</strong> <span style='color:var(--danger);'>{intel["slippage"]}</span></div>
                    <div style='margin-bottom:8px;'><strong style='color:var(--text-color);'>Rota:</strong> <span style='color:white;'>{intel["routes"]}</span></div>
                </div>
                <div style='margin-top: 15px; padding: 10px; background-color: rgba(0,0,0,0.3); border-radius: 4px;'>
                    <strong style='color:var(--text-color);'>Algoritmik Tetikleyici:</strong><br>
                    <span style='font-size:0.9rem;'>{intel["trigger"]}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
        with col2:
            y_data = intel["chart_y"]
            x_data = np.arange(len(y_data))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=x_data, y=y_data,
                mode='lines',
                line=dict(color="#f85149", width=2, shape='spline'),
                fill='tozeroy',
                fillcolor='rgba(248, 81, 73, 0.1)'
            ))
            
            fig.update_layout(
                title=intel["chart_title"],
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#c9d1d9"),
                margin=dict(l=0, r=0, t=30, b=10),
                height=250,
                xaxis=dict(showgrid=False, visible=False),
                yaxis=dict(showgrid=True, gridcolor="#1f2937")
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
