import csv
import json
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

# =====================================================================
# GERÇEK ZAMANLI GOOGLE SHEETS ENTEGRASYONU
# =====================================================================
TABLO_ID = "1t_rL2XQxtIMH09Q4xnR0-xI6e6YgDeAUuJSlcdCaid8"
# =====================================================================

st.set_page_config(page_title="Last War Tren Yönetimi", layout="wide")
st.title(" 🚂 Last War - İnternet Tabanlı Profesyonel Tren Yönetim Paneli")

GUNLER_TR = [
    "Pazartesi",
    "Salı",
    "Çarşamba",
    "Perşembe",
    "Cuma",
    "Cumartesi",
    "Pazar",
]


@st.cache_data(ttl=5)  # Verileri her 5 saniyede bir Google'dan taze oku
def google_tablodan_oku():
    try:
        # Oyuncular sayfasını çek (Küçük harfe duyarlı yapıldı)
        url_oyuncular = f"https://docs.google.com/spreadsheets/d/{TABLO_ID}/gviz/tq?tqx=out:csv&sheet=oyuncular"
        df_oyuncular = pd.read_csv(url_oyuncular, header=None)
        oyuncular = df_oyuncular.dropna()[0].astype(str).tolist()

        # Durum sayfasını çek (Küçük harfe duyarlı yapıldı)
        url_durum = f"https://docs.google.com/spreadsheets/d/{TABLO_ID}/gviz/tq?tqx=out:csv&sheet=durum"
        df_durum = pd.read_csv(url_durum, header=None)
        guncel_gun = int(df_durum.iloc[0, 0])
    except Exception as e:
        st.error(
            f"Google E-Tablo bağlantı hatası! ID'yi ve paylaşım izinlerini kontrol edin: {e}"
        )
        oyuncular = [f"Oyuncu_{i}" for i in range(1, 101)]
        guncel_gun = 0

    return oyuncular, guncel_gun


# Google verilerini oturuma yükle
oyuncular, guncel_gun = google_tablodan_oku()

if "guncel_gun" not in st.session_state:
    st.session_state.guncel_gun = guncel_gun


def tarih_hesapla(gun_offset):
    baslangic = datetime.now()
    hedef = baslangic + timedelta(days=gun_offset)
    return f"{hedef.strftime('%d.%m.%Y')} {GUNLER_TR[hedef.weekday()]}"


N = len(oyuncular)
guncel_tarih = tarih_hesapla(st.session_state.guncel_gun)

# --- MATEMATİKSEL DÖNGÜ GESABI ---
if N > 0:
    yari_periyot = N // 2
    konduktor_idx = st.session_state.guncel_gun % N
    vip_idx = (konduktor_idx + yari_periyot) % N
    günün_konduktörü = oyuncular[konduktor_idx]
    günün_vipi = oyuncular[vip_idx]
else:
    günün_konduktörü = "Oyuncu Bulunamadı"
    günün_vipi = "Oyuncu Bulunamadı"
    yari_periyot = 0

# --- ARAYÜZ ---
sol_kolon, sag_kolon = st.columns(2)

with sol_kolon:
    st.header("👥 İttifak Bilgileri")
    st.info(
        "💡 **NOT:** Oyuncu ekleme, çıkarma veya kalıcı gün sabitleme işlemlerini doğrudan bağlı olan Google E-Tablonuz üzerinden yapabilirsiniz. Buradaki liste oradan canlı beslenir."
    )
    st.subheader(f"Aktif Üye Listesi ({N} Kişi)")
    st.dataframe(oyuncular, use_container_width=True, height=400)

with sag_kolon:
    st.header(f"🗓️ Gün {st.session_state.guncel_gun + 1} | {guncel_tarih}")

    # Gün Değiştirme Butonları
    k1, k2 = st.columns(2)
    with k1:
        if st.button("⏮️ Önceki Gün") and st.session_state.guncel_gun > 0:
            st.session_state.guncel_gun -= 1
            st.rerun()
    with k2:
        if st.button("⏭️ Sonraki Gün"):
            st.session_state.guncel_gun += 1
            st.rerun()

    # Oyun İçi Sohbet Şablonu
    st.subheader("📋 Oyun İçi Sohbet Şablonu")
    şablon = f"""
===================================
🚂  LAST WAR TREN GÖREV DAĞILIMI  🚂
📅  TARİH: {guncel_tarih} (Gün {st.session_state.guncel_gun + 1})
===================================

👑  [KONDÜKTÖR]: {günün_konduktörü}
    (Bu oyuncu {yari_periyot} gün sonra VIP olacak)

💎  [VIP GÖREV] : {günün_vipi}
    (Bu oyuncu {yari_periyot} gün sonra Kondüktör olacak)

===================================
• Aktif Üye: {N} | Görev Aralığı: Tam {yari_periyot} Gün
• Sıra otomatik işlemektedir. İyi oyunlar!
    """
    st.code(şablon, language="text")

    # Gelecek 5 Günün Tahmini
    st.subheader("🔮 Gelecek 5 Günün Tren Planı")
    gelecek_plan = []
    for i in range(1, 6):
        g_offset = st.session_state.guncel_gun + i
        k_idx = g_offset % N
        v_idx = (k_idx + yari_periyot) % N
        gelecek_plan.append(
            {
                "Tarih": tarih_hesapla(g_offset),
                "Kondüktör": oyuncular[k_idx],
                "VIP Yolcu": oyuncular[v_idx],
            }
        )
    st.table(gelecek_plan)
