import os, json, time
import requests
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Any
from links import LINKS

# API anahtarını al (environment variable veya Streamlit secrets)
API_KEY = os.getenv("CUTTLY_API_KEY") or st.secrets.get("CUTTLY_API_KEY")
if not API_KEY:
    st.error("❌ CUTTLY_API_KEY bulunamadı! .streamlit/secrets.toml dosyasını kontrol edin.")
    st.stop()

# Streamlit sayfa konfigürasyonu
st.set_page_config(
    page_title="🔗 Cutt.ly Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔗 Cutt.ly Tıklama Dashboard")
st.markdown("**Free Plan Uyumlu** - Tüm linkler sırayla güncellenir (20sn ara ile)")

# Cache ayarları
CACHE_PATH = Path("cuttly_cache.json")
CACHE_TTL = 3600  # 1 saat cache (saniye)
API_DELAY = 21  # Free plan: 20+ saniye ara (3 çağrı/60sn)

# ---- Cache yönetimi ----
def load_cache() -> Dict[str, Any]:
    """JSON cache dosyasını yükle"""
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except Exception:
            return {}
    return {}

def save_cache(data: Dict[str, Any]):
    """Cache'i JSON dosyasına kaydet"""
    CACHE_PATH.write_text(json.dumps(data, indent=2))

# ---- Yardımcı fonksiyonlar ----
def code_from_short(short: str) -> str:
    """Kısa URL'den kod çıkar"""
    try:
        return short.split("/")[-1]
    except Exception:
        return short

def normalize_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Cutt.ly API yanıtını normalize et"""
    # Farklı API response formatlarını destekle
    stats = data.get("stats") or data.get("url") or {}
    
    return {
        "status": stats.get("status"),
        "title": stats.get("title"),
        "fullLink": stats.get("fullLink"),
        "shortLink": stats.get("shortLink"),
        "clicks": stats.get("clicks") or stats.get("totalClicks") or 0,
        "date": stats.get("date"),
        "devices": stats.get("devices"),
        "refs": stats.get("refs"),
        "raw": stats,
    }

# ---- API çağrısı ----
def fetch_stats_live(code: str) -> Dict[str, Any]:
    """Canlı API çağrısı yap (rate limit aware)"""
    
    # Farklı API endpoint formatlarını dene
    attempts = [
        f"https://cutt.ly/api/api.php?key={API_KEY}&stats=https://cutt.ly/{code}",
        f"https://cutt.ly/api/api.php?key={API_KEY}&short={code}&stats=true",
    ]
    
    for attempt_url in attempts:
        try:
            resp = requests.get(attempt_url, timeout=15)
            
            if resp.status_code == 429:
                # Rate limit hit, kısa bir bekleme
                time.sleep(2)
                continue
                
            resp.raise_for_status()
            data = resp.json()
            
            # API yanıtını normalize et
            normalized = normalize_response(data)
            
            # Rate limit için istekler arası bekleme (Free plan: 20+ sn)
            # Bu bekleme fetchStats_live çağıran yerde yapılacak
            
            return normalized
            
        except Exception as e:
            continue
    
    # Tüm denemeler başarısız
    raise RuntimeError(f"API çağrısı başarısız: {code}")

# ---- Ana veri yükleme logic ----
def load_data():
    """Ana veri yükleme fonksiyonu - Tüm linkler sırayla güncellenir"""
    
    cache = load_cache()
    now = int(time.time())
    api_calls_made = 0
    results = []
    
    with st.spinner("Veriler yükleniyor... Bu işlem biraz zaman alabilir (20sn x link sayısı)"):
        progress_bar = st.progress(0.0)
        status_placeholder = st.empty()
        
        for idx, item in enumerate(LINKS):
            code = code_from_short(item["short"])
            cached = cache.get(code)
            
            # Cache kontrolü
            fresh_needed = True
            if cached and (now - cached.get("ts", 0) < CACHE_TTL):
                fresh_needed = False
            
            try:
                if fresh_needed:
                    # Canlı API çağrısı
                    status_placeholder.write(f"🔄 Güncelleniyor: **{item['name']}** ({idx+1}/{len(LINKS)})")
                    
                    stats = fetch_stats_live(code)
                    cache[code] = {"ts": now, "data": stats}
                    save_cache(cache)  # Her güncelleme sonrası kaydet
                    api_calls_made += 1
                    
                    # Güncellenmiş veriyi hemen göster
                    status_placeholder.success(f"✅ **{item['name']}**: {stats.get('clicks', 0)} tıklama")
                    
                    # Rate limit için bekleme (son link değilse)
                    if idx < len(LINKS) - 1:
                        countdown_placeholder = st.empty()
                        for remaining in range(API_DELAY, 0, -1):
                            countdown_placeholder.write(f"⏳ Sonraki link için {remaining} saniye...")
                            time.sleep(1)
                        countdown_placeholder.empty()
                    
                else:
                    # Cache'den al
                    stats = cached.get("data", {})
                    status_placeholder.write(f"💾 Cache'den alınıyor: **{item['name']}** ({idx+1}/{len(LINKS)})")
                
                # Sonucu listeye ekle
                result = {
                    "Kaynak": item["name"],
                    "Kısa URL": stats.get("shortLink") or item["short"],
                    "Tıklama": stats.get("clicks") or 0,
                    "Son Güncelleme": (
                        time.strftime("%H:%M", time.localtime(cached.get("ts", 0))) 
                        if cached else "—"
                    )
                }
                results.append(result)
                
            except Exception as e:
                # Hata durumu
                status_placeholder.write(f"❌ Hata: **{item['name']}** - {str(e)[:50]}")
                results.append({
                    "Kaynak": item["name"],
                    "Kısa URL": item["short"],
                    "Tıklama": 0,
                    "Son Güncelleme": "—"
                })
            
            # Progress güncelle
            progress_bar.progress((idx + 1) / len(LINKS))
        
        progress_bar.empty()
        status_placeholder.empty()
    
    # Cache'i kaydet
    save_cache(cache)
    
    return results, api_calls_made

# ---- Sidebar ----
st.sidebar.markdown("### ⚙️ Ayarlar")
st.sidebar.markdown(f"**API Stratejisi:** {API_DELAY}sn ara ile tüm linkler")
st.sidebar.markdown(f"**Cache TTL:** {CACHE_TTL//3600} saat")
st.sidebar.markdown(f"**Toplam Süre:** ~{len(LINKS) * API_DELAY // 60} dk (ilk çalıştırma)")

if st.sidebar.button("🔄 Şimdi Yenile", type="primary"):
    # Cache'i temizle ve sayfayı yenile
    if CACHE_PATH.exists():
        CACHE_PATH.unlink()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**⏰ Süreç:** Tüm linkler tek seferde güncellenir")
st.sidebar.markdown("**💾 Cache:** Başarılı veriler 1 saat saklanır")

# ---- Ana içerik ----
data, api_calls_made = load_data()

# Metrikleri göster
col1, col2, col3 = st.columns(3)

with col1:
    total_clicks = sum(row["Tıklama"] for row in data if isinstance(row["Tıklama"], int))
    st.metric("📊 Toplam Tıklama", total_clicks)

with col2:
    updated_count = sum(1 for row in data if row["Son Güncelleme"] != "—")
    st.metric("🔄 Güncellenen Linkler", f"{updated_count}/{len(LINKS)}")

with col3:
    st.metric("🔗 API Çağrısı", f"{api_calls_made} adet")

# ---- Veri tablosu ----
df = pd.DataFrame(data)

# Tıklama sütununu sayısal yap
df["Tıklama"] = pd.to_numeric(df["Tıklama"], errors='coerce').fillna(0).astype(int)

st.markdown("### 📋 Link İstatistikleri")
st.dataframe(
    df, 
    use_container_width=True,
    hide_index=True,
    column_config={
        "Kaynak": st.column_config.TextColumn("Kaynak", width="large"),
        "Kısa URL": st.column_config.LinkColumn("Kısa URL", width="large"),
        "Tıklama": st.column_config.NumberColumn("Tıklama", format="%d", width="medium"),
        "Son Güncelleme": st.column_config.TextColumn("Son Güncelleme", width="medium"),
    }
)

# ---- Grafik ----
if total_clicks > 0:
    st.markdown("### 📈 Tıklama Grafiği")
    
    # En yüksek tıklanan linkler (top 10)
    df_chart = df[df["Tıklama"] > 0].nlargest(10, "Tıklama")
    
    if not df_chart.empty:
        st.bar_chart(
            df_chart.set_index("Kaynak")["Tıklama"],
            height=400
        )
    else:
        st.info("📊 Henüz tıklama verisi yok")

# ---- Footer ----
st.markdown("---")
st.markdown(
    "**💡 İpucu:** İlk çalıştırma ~6 dakika sürer (17 link × 21sn). "
    "Sonraki yenilemeler cache sayesinde çok hızlıdır. Cache 1 saat geçerlidir."
)
