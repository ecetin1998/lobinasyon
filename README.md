# Lobinasyon

TFF Fantasy mini lig takip paneli. Haftalık kadro ekranlarından çıkarılan veriyi
puan durumu, oyuncu istatistikleri, kart takibi ve maç sonuçlarına çevirir.

## Çalıştırma

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Yeni hafta ekleme

`data/` klasörüne `gw05.json` gibi bir dosya at, uygulama otomatik alır. Kod değişikliği yok.

```json
{
  "week": 5,
  "fixtures": [
    {"home": "Tomarza", "home_score": 47, "away_score": 84, "away": "bilanço"}
  ],
  "teams": {
    "bilanço": {
      "mh": 84,
      "nostradamus": 6,
      "card": "tum_takim",
      "captain": "Salah",
      "vice": "Osimhen",
      "multiplier": 2,
      "xi":    [{"name": "Onana", "club": "TS", "points": 7}],
      "bench": [{"name": "Bahadır", "club": "KNY", "points": 3}]
    }
  }
}
```

### Alan notları

- `points` ekranda görünen puandır, yani kaptan çarpanı **dahil**.
- `multiplier`: normal kaptan 2, tripleks 3, dört dörtlük 4.
- `card`: `tum_takim`, `dort_dortluk`, `tripleks`, `hucum`, `limitsiz` veya `null`.
- Doğrulama: ilk 11 toplamı (+ kart varsa yedekler) + nostradamus = `mh`.
  Tutmazsa Takım Detayı sekmesinde uyarı çıkar.

## Yayına alma

GitHub'a push et, [share.streamlit.io](https://share.streamlit.io) üzerinden repoyu bağla,
ana dosya olarak `app.py` seç. Ücretsiz ve herkese açık bir URL veriyor, ligdekiler
hesap açmadan girebilir.
