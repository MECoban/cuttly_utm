# 🔗 Cutt.ly Tıklama Dashboard

Modern, rate-limit uyumlu Cutt.ly link analitik dashboard'u. Python/Streamlit ile geliştirilmiş.

## ✨ Özellikler

- 📊 **Real-time Analytics**: Tüm linklerinizin tıklama istatistikleri
- ⚡ **Smart Caching**: 1 saatlik cache ile hızlı yükleme
- 🚦 **Rate Limit Uyumlu**: Free plan için optimize (3 çağrı/60sn)
- 📈 **Görsel Grafikler**: En çok tıklanan linkler bar chart
- 🔄 **Progress Tracking**: Real-time güncelleme durumu
- 💾 **Persistent Cache**: JSON tabanlı local cache

## 🚀 Hızlı Başlangıç

### Gereksinimler
```bash
pip install -r requirements.txt
```

### Konfigürasyon
`.streamlit/secrets.toml` dosyası oluşturun:
```toml
CUTTLY_API_KEY = "YOUR_API_KEY_HERE"
```

### Çalıştırma
```bash
streamlit run app.py
```

Dashboard `http://localhost:8501` adresinde açılacak.

## 📁 Proje Yapısı

```
cuttly_utm/
├── app.py              # Ana Streamlit uygulaması
├── links.py            # Takip edilecek linkler
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore kuralları
└── .streamlit/
    └── secrets.toml   # API anahtarı (git'e dahil değil)
```

## ⚙️ Konfigürasyon

### Link Ekleme
`links.py` dosyasında LINKS listesine yeni linkler ekleyin:

```python
LINKS = [
    {
        "name": "Instagram Post",
        "target": "https://example.com/?utm_source=instagram",
        "short": "https://cutt.ly/abc123"
    }
]
```

### Cache Ayarları
`app.py` içinde cache süresini değiştirebilirsiniz:
```python
CACHE_TTL = 3600  # 1 saat (saniye)
```

## 🎯 Rate Limiting Stratejisi

- **Free Plan**: 3 çağrı/60 saniye
- **API Delay**: 21 saniye ara
- **Smart Cache**: 1 saat TTL
- **Sequential Processing**: Rate limit aşımını önler

## 📊 Dashboard Özellikleri

### Metrikler
- 📊 **Toplam Tıklama**: Tüm linklerin toplam tıklaması
- 🔄 **Güncellenen Linkler**: Cache'de bulunan link sayısı
- 🔗 **API Çağrısı**: Son güncelleme sırasında yapılan çağrı sayısı

### Tablo
| Kaynak | Kısa URL | Tıklama | Son Güncelleme |
|--------|----------|---------|----------------|

### Grafik
En çok tıklanan ilk 10 link için bar chart.

## 🔧 Troubleshooting

### Rate Limit Hatası
- 21 saniye ara yeterli değilse `API_DELAY` değerini artırın
- Cache TTL'yi uzatın (2-3 saat)

### API Hatası
- Cutt.ly API anahtarınızı kontrol edin
- Internet bağlantınızı doğrulayın

### Cache Problemi
- `cuttly_cache.json` dosyasını silin
- "🔄 Şimdi Yenile" butonunu kullanın

## 🌐 Deployment

### Streamlit Cloud
1. GitHub repo'sunu Streamlit Cloud'a bağlayın
2. Secrets bölümünde `CUTTLY_API_KEY` ekleyin
3. Deploy edin

### Vercel (Alternative)
Daha gelişmiş deployment için Vercel + FastAPI kullanabilirsiniz.

## 📝 Lisans

MIT License

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!

---

**Made with ❤️ by [MECoban](https://github.com/MECoban)**
