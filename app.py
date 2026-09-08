# -*- coding: utf-8 -*-
"""Lobinasyon — TFF Fantasy mini lig paneli."""
import json, glob, os
from collections import defaultdict

import streamlit as st

st.set_page_config(page_title="Lobinasyon", page_icon="⚽",
                   layout="wide", initial_sidebar_state="collapsed")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEARCH_DIRS = [os.path.join(BASE_DIR, "data"), BASE_DIR, os.getcwd()]

CARD_LABEL = {
    "tum_takim": "Tüm Takım Sahaya", "dort_dortluk": "Dört Dörtlük ×4",
    "tripleks": "Tripleks ×3", "hucum": "Hücum!", "limitsiz": "Limitsiz Bütçe", None: "—",
}
CARD_KEYS = ["tum_takim", "dort_dortluk", "tripleks", "hucum", "limitsiz"]
CARD_CLS = {"tum_takim": "c-tts", "dort_dortluk": "c-x4", "tripleks": "c-x3",
            "hucum": "c-huc", "limitsiz": "c-lim"}
PER_TYPE = 2
FORM_TR = {"W": "G", "D": "B", "L": "M"}

CSS = """
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Inter:wght@400;600;800&display=swap');
.stApp{background:
  radial-gradient(1200px 600px at 12% -8%, #1d2a6b 0%, transparent 55%),
  radial-gradient(900px 500px at 92% 0%, #0f3d43 0%, transparent 50%),
  #090c26;}
.block-container{padding-top:1.4rem;max-width:1250px}
#MainMenu,footer,header{visibility:hidden}
html,body,[class*="css"]{font-family:'Inter',sans-serif}

.hero{background:linear-gradient(105deg,#16205c 0%,#1b2f7a 45%,#0e5c52 100%);
 border:1px solid #2c3a86;border-radius:20px;padding:22px 26px;margin-bottom:18px;
 position:relative;overflow:hidden}
.hero:after{content:"";position:absolute;right:-60px;top:-70px;width:280px;height:280px;
 border-radius:50%;background:radial-gradient(circle,#4ade9f33,transparent 70%)}
.hero h1{font-family:'Barlow Condensed';font-size:46px;letter-spacing:1px;margin:0;
 color:#fff;text-transform:uppercase;line-height:1}
.hero p{margin:6px 0 0;color:#9fb0e8;font-size:12.5px;letter-spacing:.5px}

.pod{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:6px 0 18px}
.pod .p{border-radius:16px;padding:16px 14px;text-align:center;
 background:#141a48;border:1px solid #29327a}
.pod .p1{background:linear-gradient(160deg,#3a2f08,#151a45);border-color:#c9a227}
.pod .p2{background:linear-gradient(160deg,#2a2f38,#151a45);border-color:#9aa6b5}
.pod .p3{background:linear-gradient(160deg,#33220f,#151a45);border-color:#b1723a}
.pod .medal{font-size:24px}
.pod .nm{font-family:'Barlow Condensed';font-size:24px;color:#fff;margin-top:2px;
 white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pod .pts{font-size:30px;font-weight:800;color:#4ade9f;line-height:1.1}
.pod .sub{font-size:11px;color:#8e9ad4}

.strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:8px}
.strip .s{background:#121840;border:1px solid #262f70;border-radius:14px;padding:12px 14px}
.strip .l{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#7d89c9}
.strip .v{font-size:21px;font-weight:800;color:#eef1ff;margin-top:3px;line-height:1.15;
 white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.strip .n{font-size:11px;color:#7d89c9;margin-top:2px}

.tbl{width:100%;border-collapse:collapse;font-size:13.5px}
.tbl th{font-size:10px;text-transform:uppercase;letter-spacing:.8px;color:#7d89c9;
 text-align:right;padding:9px 8px;border-bottom:1px solid #2a3170;font-weight:700}
.tbl th:nth-child(-n+3){text-align:left}
.tbl td{padding:9px 8px;border-bottom:1px solid #1c2258;text-align:right;
 color:#dfe4ff;font-variant-numeric:tabular-nums}
.tbl td:nth-child(-n+3){text-align:left}
.tbl tr:hover td{background:#161d4d}
.tbl th.on{color:#4ade9f}
.of{color:#6b74a8;font-size:11px}
[class^=pz-]{display:inline-block;padding:2px 6px;border-radius:6px;font-size:10px;font-weight:800}
.pz-KL{background:#4a3a12;color:#ffd76a}.pz-DEF{background:#183166;color:#8fb8ff}
.pz-OS{background:#14432f;color:#5ef0aa}.pz-FOR{background:#4a1f24;color:#ff8f8f}
.pz-NA{background:#252a5e;color:#7d89c9}
.rk{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;
 border-radius:8px;background:#1d2560;color:#98a4e0;font-size:12px;font-weight:800}
.rk.g{background:#c9a227;color:#221a00}.rk.s{background:#9aa6b5;color:#15181d}
.rk.b{background:#b1723a;color:#1d1206}
.tm{color:#fff;font-weight:600}
.up{color:#4ade9f;font-size:11px}.dn{color:#ff6b6b;font-size:11px}.eq{color:#5a659e;font-size:11px}
.pz{font-weight:800;color:#4ade9f}
.form span{display:inline-block;width:17px;height:17px;line-height:17px;border-radius:5px;
 font-size:10px;font-weight:800;text-align:center;margin-right:3px}
.fw{background:#14432f;color:#5ef0aa}.fd{background:#3d3410;color:#ffd76a}
.fl{background:#43181c;color:#ff8f8f}

.pill{display:inline-block;padding:3px 9px;border-radius:20px;font-size:10.5px;font-weight:700}
.c-tts{background:#14432f;color:#5ef0aa}.c-x4{background:#341f6b;color:#c3a6ff}
.c-x3{background:#183166;color:#8fb8ff}.c-huc{background:#4a1f24;color:#ff8f8f}
.c-lim{background:#4a3a12;color:#ffd76a}.c-none{background:#212960;color:#7d89c9}
.stk{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:3px}
.on{background:#4ade9f}.off{background:#39406f}

.bar{height:5px;border-radius:3px;background:#232a63;overflow:hidden;min-width:60px}
.bar i{display:block;height:100%;background:linear-gradient(90deg,#4ade9f,#3aa6ff)}

.pitch{background:linear-gradient(#1a7a45,#126034);border-radius:16px;padding:16px 10px;
 border:1px solid #2b8a58}
.row{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.pl{background:#f2f5ff;border-radius:10px;width:96px;padding:6px 4px;text-align:center;
 box-shadow:0 2px 6px #0004;position:relative}
.pl .p{font-size:15px;font-weight:800;color:#0d1030}
.pl .n{font-size:11px;font-weight:700;color:#20264f;white-space:nowrap;overflow:hidden;
 text-overflow:ellipsis}
.pl .c{font-size:9.5px;color:#6b74a8}
.pl .mx{font-size:9px;font-weight:700;color:#12b26b;margin-left:3px;vertical-align:super}
.pl.dim{opacity:.6}
.badge{position:absolute;top:-7px;left:-7px;width:19px;height:19px;border-radius:50%;
 font-size:10px;font-weight:800;line-height:19px;color:#fff}
.bc{background:#12b26b}.bv{background:#2f6ef5}

.stTabs [data-baseweb="tab-list"]{gap:4px;border-bottom:1px solid #262f70}
.stTabs [data-baseweb="tab"]{background:transparent;color:#8e9ad4;font-weight:700;
 font-size:13px;padding:8px 16px}
.stTabs [aria-selected="true"]{color:#4ade9f;border-bottom:2px solid #4ade9f}

.scroll{width:100%;overflow-x:visible}
.tip{position:relative;cursor:help;border-bottom:1px dotted #4a5599}
.tipbox{visibility:hidden;opacity:0;position:absolute;left:0;top:150%;z-index:99;
 background:#0d1236;border:1px solid #3a4590;border-radius:10px;padding:9px 11px;
 min-width:210px;max-width:290px;box-shadow:0 8px 22px #0009;
 font-size:11.5px;font-weight:400;color:#c9d2ff;line-height:1.75;
 transition:opacity .12s;pointer-events:none;white-space:normal}
.tipbox b{color:#fff;font-weight:700}
.tipbox i{color:#8e9ad4;font-style:normal;font-size:10.5px}
.tipbox u{color:#4ade9f;text-decoration:none;font-weight:800}
.tip:hover .tipbox{visibility:visible;opacity:1}
.tbl tr:nth-last-child(-n+4) .tipbox{top:auto;bottom:150%}
.owns{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:6px}
.own{background:#161d4d;border:1px solid #2b3480;border-radius:10px;padding:6px 10px;
 font-size:12px;color:#dfe4ff;font-weight:600}
.own.cap{border-color:#12b26b;background:#12331f}
.own i{display:block;font-style:normal;font-size:10px;color:#8e9ad4;font-weight:400}

@media (max-width:760px){
 .block-container{padding-left:.7rem;padding-right:.7rem;padding-top:.8rem}
 .hero{padding:16px 16px;border-radius:16px}
 .hero h1{font-size:32px}
 .hero p{font-size:10.5px;letter-spacing:.3px}

 /* podyum: lider tam genislik, 2-3 altta yan yana */
 .pod{grid-template-columns:1fr 1fr;gap:8px}
 .pod .p1{grid-column:1 / -1}
 .pod .nm{font-size:19px}
 .pod .pts{font-size:25px}
 .pod .sub{font-size:10px}
 .pod .medal{font-size:20px}

 .strip{grid-template-columns:1fr 1fr;gap:8px}
 .strip .s{padding:10px 11px}
 .strip .v{font-size:17px}
 .strip .l{font-size:9px;letter-spacing:.6px}
 .strip .n{font-size:10px}

 .scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
 .tipbox{display:none}
 .tip{border-bottom:none}
 .tbl{font-size:12.5px}
 .tbl th,.tbl td{padding:8px 5px}
 .rk{width:21px;height:21px;font-size:11px;border-radius:7px}

 /* puan durumu: O G B M A Y gizle, form + AV + P kalsin */
 .t-std th:nth-child(n+5):nth-child(-n+8),
 .t-std td:nth-child(n+5):nth-child(-n+8){display:none}

 /* oyuncular: secim, takim, en iyi, bosa, bar gizle */
 .t-pl th:nth-child(7),.t-pl td:nth-child(7),
 .t-pl th:nth-child(9),.t-pl td:nth-child(9),
 .t-pl th:nth-child(10),.t-pl td:nth-child(10),
 .t-pl th:nth-child(12),.t-pl td:nth-child(12){display:none}

 .t-card{min-width:520px}
 .t-res td{font-size:12.5px;padding:8px 4px}

 /* saha: 4 sutuna dus, kartlar kucul */
 .pitch{padding:12px 6px;border-radius:14px}
 .row{gap:6px;margin-bottom:9px}
 .pl{width:auto;flex:0 0 calc(25% - 5px);min-width:0;padding:5px 3px}
 .pl .p{font-size:13px}
 .pl .n{font-size:10px}
 .pl .c{font-size:9px}
 .badge{width:17px;height:17px;line-height:17px;font-size:9px;top:-6px;left:-6px}

 .stTabs [data-baseweb="tab-list"]{overflow-x:auto;flex-wrap:nowrap}
 .stTabs [data-baseweb="tab"]{padding:8px 10px;font-size:11.5px;white-space:nowrap}
 .sec{font-size:17px}
}

@media (max-width:420px){
 .hero h1{font-size:27px}
 .strip{grid-template-columns:1fr}
 .pod .nm{font-size:17px}
 .pl{flex:0 0 calc(33.333% - 4px)}
 .tbl{font-size:12px}
}

.sec{font-family:'Barlow Condensed';font-size:20px;color:#4ade9f;letter-spacing:.6px;
 text-transform:uppercase;margin:18px 0 8px}
</style>
"""

TR_ALPHABET = "aAbBcCçÇdDeEfFgGğĞhHıIiİjJkKlLmMnNoOöÖpPrRsSşŞtTuUüÜvVyYzZ"
_TR_ORDER = {ch: i for i, ch in enumerate(TR_ALPHABET)}


def tr_key(text: str):
    """Turkce alfabeye gore siralama anahtari.

    ç, ğ, ı, i, ö, ş, ü dogru yere oturur ve buyuk/kucuk harf farki
    siralamayi bozmaz (avengers ile Bekiroteam ayni kefede).
    """
    return [_TR_ORDER.get(ch, ord(ch) + 1000) // 2 for ch in str(text)]



def weeks_label(v) -> str:
    """MH1 (C), 2, 3 (C) · C×2 seklinde hafta listesi uretir."""
    parts = []
    for i, wk in enumerate(sorted(set(v["w"]))):
        cap = " (C)" if wk in v["cw"] else ""
        parts.append((f"MH{wk}" if i == 0 else str(wk)) + cap)
    out = ", ".join(parts)
    if v["c"] > 1:
        out += f" · C×{v['c']}"
    return out



# Pozisyon kodlari: KL kaleci, DEF defans, OS orta saha, FOR forvet
POS_ORDER = ["KL", "DEF", "OS", "FOR"]
POS_LABEL = {"KL": "Kaleci", "DEF": "Defans", "OS": "Orta saha", "FOR": "Forvet"}
POS_FILE = {}   # oyuncu -> pozisyon; positions.json varsa doldurulur


def pos_of(p) -> str:
    """Once oyuncunun kendi 'pos' alani, sonra positions.json.

    positions.json anahtari "Oyuncu|KULUP" (ayni isimli farkli oyuncular icin);
    bulunamazsa sade isimle de bakilir.
    """
    return (p.get("pos")
            or POS_FILE.get(f'{p["name"]}|{p["club"]}')
            or POS_FILE.get(p["name"], ""))


def formation(xi):
    """Ilk 11'i pozisyona gore satirlara boler; pozisyon yoksa kadro sirasina duser."""
    if not all(pos_of(p) for p in xi):
        return [xi[:1], xi[1:5], xi[5:9], xi[9:]] if len(xi) == 11 else [xi]
    lines = [[p for p in xi if pos_of(p) == k] for k in POS_ORDER]
    return [ln for ln in lines if ln]


def md(html: str):
    """HTML'i ham metne dusurmeden basar.

    Markdown'da HTML blogu bos satirda biter ve devami duz yazi olarak
    gorunur; 4+ bosluk girinti de kod blogu sayilir. Bu yuzden satir basi
    bosluklarini kirpip bos satirlari tamamen atiyoruz.
    """
    clean = [line.strip() for line in html.splitlines()]
    st.markdown("\n".join(l for l in clean if l), unsafe_allow_html=True)


md(CSS)  # bos satirlar md() icinde temizleniyor


def load_positions():   # cache YOK: dosya sonradan eklenince hemen gorunsun
    """Ortak pozisyon sozlugu: {"Osimhen": "FOR", ...}"""
    for d in SEARCH_DIRS:
        fp = os.path.join(d, "positions.json")
        if os.path.exists(fp):
            with open(fp, encoding="utf-8") as f:
                return json.load(f)
    return {}


@st.cache_data
def load_weeks():
    paths = {}
    for d in SEARCH_DIRS:
        for p in glob.glob(os.path.join(d, "gw*.json")):
            paths.setdefault(os.path.basename(p), p)
    ws = []
    for name in sorted(paths):
        with open(paths[name], encoding="utf-8") as f:
            ws.append(json.load(f))
    ws.sort(key=lambda w: w["week"])
    return ws


def team_points(sq):
    m = sq["multiplier"]
    t = sum(p["points"] * (m if p["name"] == sq["captain"] else 1) for p in sq["xi"])
    if sq["card"] == "tum_takim":
        t += sum(p["points"] for p in sq["bench"])
    return t + sq["nostradamus"]


def build_table(weeks, upto=None):
    tbl = defaultdict(lambda: dict(O=0, G=0, B=0, M=0, A=0, Y=0, form=[]))
    for w in weeks:
        if upto is not None and w["week"] > upto:
            continue
        for f in w["fixtures"]:
            for nm, sf, sa in ((f["home"], f["home_score"], f["away_score"]),
                               (f["away"], f["away_score"], f["home_score"])):
                r = tbl[nm]
                r["O"] += 1; r["A"] += sf; r["Y"] += sa
                if sf > sa:
                    r["G"] += 1; r["form"].append("W")
                elif sf == sa:
                    r["B"] += 1; r["form"].append("D")
                else:
                    r["M"] += 1; r["form"].append("L")
    rows = [dict(t=n, **r, AV=r["A"] - r["Y"], P=r["G"] * 3 + r["B"]) for n, r in tbl.items()]
    rows.sort(key=lambda r: (-r["P"], -r["AV"], -r["A"], r["t"]))
    return rows


def player_stats(weeks):
    pl = defaultdict(lambda: dict(name="", club="", pos="", sec=0, xi=0, cap=0, katki=0,
                                  bosa=0, best=0, teams=set(),
                                  by=defaultdict(lambda: {"w": [], "c": 0, "cw": set()})))
    for w in weeks:
        for tn, sq in w["teams"].items():
            m, cb = sq["multiplier"], sq["card"] == "tum_takim"
            for p in sq["xi"]:
                d = pl[(p["name"], p["club"])]
                d["name"], d["club"] = p["name"], p["club"]
                d["pos"] = d["pos"] or pos_of(p)
                d["sec"] += 1; d["xi"] += 1
                d["teams"].add(tn); d["best"] = max(d["best"], p["points"])
                d["katki"] += p["points"] * (m if p["name"] == sq["captain"] else 1)
                d["by"][tn]["w"].append(w["week"])
                if p["name"] == sq["captain"]:
                    d["cap"] += 1
                    d["by"][tn]["c"] += 1
                    d["by"][tn]["cw"].add(w["week"])
            for p in sq["bench"]:
                d = pl[(p["name"], p["club"])]
                d["name"], d["club"] = p["name"], p["club"]
                d["pos"] = d["pos"] or pos_of(p)
                d["sec"] += 1
                d["teams"].add(tn); d["best"] = max(d["best"], p["points"])
                d["by"][tn]["w"].append(w["week"])
                if cb:
                    d["katki"] += p["points"]
                else:
                    d["bosa"] += p["points"]
    return pl


POS_FILE.update(load_positions())


def pos_warning():
    """positions.json yoksa nerelere bakildigini soyler."""
    st.warning("positions.json bulunamadı, pozisyonlar boş görünüyor.")
    for d in SEARCH_DIRS:
        try:
            var = "positions.json" in os.listdir(d)
        except OSError:
            var = None
        st.write(f"- `{d}` → " + ("klasör yok" if var is None
                                  else "VAR (okunamadı?)" if var else "yok"))
weeks = load_weeks()
if not weeks:
    st.error("gw*.json dosyası bulunamadı.")
    for d in SEARCH_DIRS:
        try:
            f = [x for x in sorted(os.listdir(d)) if x.startswith("gw")]
        except OSError:
            f = None
        st.write(f"- `{d}` → " + ("klasör yok" if f is None else ", ".join(f) or "gw dosyası yok"))
    st.stop()

LAST = weeks[-1]["week"]
NT = max(len(w["teams"]) for w in weeks)
table = build_table(weeks)
prev_rank = ({r["t"]: i for i, r in enumerate(build_table(weeks, LAST - 1))}
             if len(weeks) > 1 else {})
rank_of = {r['t']: i for i, r in enumerate(table)}
pl = player_stats(weeks)
_name_count = defaultdict(int)
for _k in pl:
    _name_count[_k[0]] += 1


def label_of(key) -> str:
    """Tabloda/başlıkta görünen ad: sade isim (kulüp ayrı sütunda)."""
    return key[0]


def picker_label(key) -> str:
    """Açılır listede ayrım gerekiyorsa kulübü de yazar (aynı isimli oyuncular)."""
    name, club = key
    return f"{name} · {club}" if _name_count[name] > 1 else name

md(f"""<div class="hero"><h1>Lobinasyon</h1>
<p>TFF FANTASY MİNİ LİG &nbsp;·&nbsp; MAÇ HAFTASI {LAST} &nbsp;·&nbsp; {NT} TAKIM</p></div>""")

medals = ["🥇", "🥈", "🥉"]
pod = "".join(
    f'<div class="p p{i+1}"><div class="medal">{medals[i]}</div>'
    f'<div class="nm">{r["t"]}</div><div class="pts">{r["P"]}</div>'
    f'<div class="sub">{r["G"]}G {r["B"]}B {r["M"]}M · AV {r["AV"]:+d}</div></div>'
    for i, r in enumerate(table[:3]))
md(f'<div class="pod">{pod}</div>')

week_scores = {t: sq["mh"] for t, sq in weeks[-1]["teams"].items()}
best_t = max(week_scores, key=week_scores.get)
season_best = max((sq["mh"], t, w["week"]) for w in weeks for t, sq in w["teams"].items())
top_pl = max(pl.items(), key=lambda kv: kv[1]["katki"])
top_pl_name = label_of(top_pl[0])
cap_hit = sum(1 for w in weeks for sq in w["teams"].values()
              if next((p["points"] for p in sq["xi"] if p["name"] == sq["captain"]), 0)
              == max(p["points"] for p in sq["xi"]))
cap_tot = sum(len(w["teams"]) for w in weeks)
cards_used = sum(1 for w in weeks for sq in w["teams"].values() if sq["card"])

md(f"""<div class="strip">
<div class="s"><div class="l">Haftanın takımı</div><div class="v">{best_t}</div>
<div class="n">{week_scores[best_t]} puan · MH{LAST}</div></div>
<div class="s"><div class="l">Sezon rekoru</div><div class="v">{season_best[0]}</div>
<div class="n">{season_best[1]} · MH{season_best[2]}</div></div>
<div class="s"><div class="l">Kral</div><div class="v">{top_pl_name}</div>
<div class="n">{top_pl[1]['katki']} puan üretti</div></div>
<div class="s"><div class="l">Kaptan isabeti</div><div class="v">{cap_hit}/{cap_tot}</div>
<div class="n">%{round(100*cap_hit/cap_tot)} doğru seçim</div></div>
<div class="s"><div class="l">Yakılan kart</div><div class="v">{cards_used}</div>
<div class="n">{NT*PER_TYPE*len(CARD_KEYS)} hakkın içinden</div></div>
</div>""")

t1, t2, t3, t4, t5 = st.tabs(["PUAN DURUMU", "OYUNCULAR", "TAKIM DETAYI", "KARTLAR", "SONUÇLAR"])

with t1:
    STD_SORTS = {
        "Puan":        lambda r: (r["P"], r["AV"], r["A"]),
        "Averaj":      lambda r: (r["AV"], r["A"]),
        "Attığı":      lambda r: (r["A"], r["AV"]),
        "Yediği":      lambda r: (r["Y"], -r["AV"]),
        "Galibiyet":   lambda r: (r["G"], r["AV"]),
        "Beraberlik":  lambda r: (r["B"], r["AV"]),
        "Mağlubiyet":  lambda r: (r["M"], -r["AV"]),
        "Form":        lambda r: (sum({"W": 3, "D": 1, "L": 0}[c] for c in r["form"][-5:]),
                                  r["AV"]),
        "Takım":       lambda r: r["t"].lower(),
    }
    k1, k2 = st.columns([2, 1])
    std_opts = sorted(STD_SORTS, key=tr_key)
    std_by = k1.selectbox("Sırala", std_opts,
                          index=std_opts.index("Puan"), key="stdsort")
    std_ord = k2.radio("Yön", ["Azalan", "Artan"], horizontal=True, key="stdord")
    std_asc = std_ord == "Artan"
    view = sorted(table, key=STD_SORTS[std_by], reverse=not std_asc)
    st_arw = " ▲" if std_asc else " ▼"

    def sth(label):
        act = ' class="on"' if label == std_by else ""
        return f"<th{act}>{label}{st_arw if label == std_by else ''}</th>"

    rows = ""
    for r in view:
        i = rank_of[r["t"]]
        cls = ["g", "s", "b"][i] if i < 3 else ""
        d = prev_rank.get(r["t"], i) - i
        mv = (f'<span class="up">▲{d}</span>' if d > 0 else
              f'<span class="dn">▼{-d}</span>' if d < 0 else '<span class="eq">–</span>')
        fm = "".join(f'<span class="f{c.lower()}">{FORM_TR[c]}</span>' for c in r["form"][-5:])
        rows += (f'<tr><td><span class="rk {cls}">{i+1}</span></td>'
                 f'<td class="tm">{r["t"]}</td><td>{mv}</td>'
                 f'<td class="form">{fm}</td>'
                 f'<td>{r["O"]}</td><td>{r["G"]}</td><td>{r["B"]}</td><td>{r["M"]}</td>'
                 f'<td>{r["A"]}</td><td>{r["Y"]}</td><td>{r["AV"]:+d}</td>'
                 f'<td class="pz">{r["P"]}</td></tr>')
    heads = ("<th>#</th>" + sth("Takım") + "<th></th>" + sth("Form")
             + "<th>O</th>" + sth("Galibiyet") + sth("Beraberlik") + sth("Mağlubiyet")
             + sth("Attığı") + sth("Yediği") + sth("Averaj") + sth("Puan"))
    md(f'<div class="scroll"><table class="tbl t-std"><tr>{heads}</tr>{rows}</table></div>')

with t2:
    slots = NT * len(weeks)
    c1, c2, c3 = st.columns([1, 1, 2])
    club = c1.selectbox("Kulüp",
                        ["Hepsi"] + sorted({d["club"] for d in pl.values()}, key=tr_key))
    pos_f = c2.selectbox("Pozisyon", ["Hepsi"] + POS_ORDER,
                         format_func=lambda x: POS_LABEL.get(x, x))
    q = c3.text_input("Oyuncu ara", "")

    items = [(k, d) for k, d in pl.items()
             if (club == "Hepsi" or d["club"] == club)
             and (pos_f == "Hepsi" or d["pos"] == pos_f)
             and q.lower() in d["name"].lower()]

    who = st.selectbox("Oyuncu detayı",
                       ["—"] + sorted((k for k, _ in items),
                                      key=lambda k: tr_key(picker_label(k))),
                       format_func=lambda k: "—" if k == "—" else picker_label(k),
                       key="who")
    if who != "—":
        d = pl[who]
        chips = "".join(
            f'<span class="own{" cap" if v["c"] else ""}">{t}'
            f'<i>{weeks_label(v)}</i></span>'
            for t, v in sorted(d["by"].items(), key=lambda kv: tr_key(kv[0])))
        md(f'<div class="sec">{d["name"]} <span class="of">{d["club"]}'
           f'{" · " + d["pos"] if d["pos"] else ""}</span> — '
           f'{len(d["by"])}/{NT} takımda</div>'
           f'<div class="owns">{chips}</div>')

    SORTS = {
        "Katkı":      lambda n, d: d["katki"],
        "Seçim":      lambda n, d: d["sec"],
        "Oran":       lambda n, d: d["sec"],
        "Kaç takım":  lambda n, d: len(d["teams"]),
        "Kaptanlık":  lambda n, d: d["cap"],
        "En iyi":     lambda n, d: d["best"],
        "Boşa":       lambda n, d: d["bosa"],
        "İlk 11":     lambda n, d: d["xi"],
        "Oyuncu":     lambda n, d: tr_key(d["name"]),
        "Kulüp":      lambda n, d: (d["club"], -d["katki"]),
        "Pozisyon":   lambda n, d: (POS_ORDER.index(d["pos"]) if d["pos"] in POS_ORDER
                                    else 9, -d["katki"]),
    }
    s1, s2 = st.columns([2, 1])
    sort_opts = sorted(SORTS, key=tr_key)
    sort_by = s1.selectbox("Sırala", sort_opts,
                           index=sort_opts.index("Katkı"))
    order = s2.radio("Yön", ["Azalan", "Artan"], horizontal=True, label_visibility="visible")

    asc = order == "Artan"
    key = SORTS[sort_by]
    if sort_by in ("Oyuncu", "Kulüp", "Pozisyon"):
        items.sort(key=lambda kv: key(*kv), reverse=asc)
    else:
        items.sort(key=lambda kv: (key(*kv), kv[1]["katki"]), reverse=not asc)
    mx = max([d["katki"] for _, d in items], default=1) or 1
    arw = " ▲" if asc else " ▼"

    def th(label, width=""):
        act = ' class="on"' if label == sort_by else ""
        return f"<th{act}{width}>{label}{arw if label == sort_by else ''}</th>"
    if not POS_FILE:
        pos_warning()
    PER_PAGE = 50
    total = len(items)
    pages = max(1, -(-total // PER_PAGE))
    if pages > 1:
        pg = st.radio(f"Sayfa ({total} oyuncu)",
                      list(range(1, pages + 1)),
                      horizontal=True, key="plpage",
                      format_func=lambda x: f"{(x-1)*PER_PAGE+1}-"
                                            f"{min(x*PER_PAGE, total)}")
    else:
        pg = 1
    start = (pg - 1) * PER_PAGE
    page_items = items[start:start + PER_PAGE]

    rows = ""
    for i, (k, d) in enumerate(page_items, start + 1):
        n = label_of(k)
        pct = round(100 * d["sec"] / slots)
        tip = "".join(
            f'<b>{t}</b> <i>{weeks_label(v)}</i><br>'
            for t, v in sorted(d["by"].items(), key=lambda kv: tr_key(kv[0])))
        rows += (f'<tr><td><span class="rk">{i}</span></td>'
                 f'<td class="tm"><span class="tip">{n}'
                 f'<span class="tipbox"><u>{n}</u> — {len(d["by"])} takımda<br>{tip}</span>'
                 f'</span></td>'
                 f'<td>{d["club"]}</td>'
                 f'<td><span class="pz-{d["pos"] or "NA"}">{d["pos"] or "—"}</span></td>'
                 f'<td><b>{d["sec"]}</b><span class="of">/{slots}</span></td><td>%{pct}</td>'
                 f'<td>{len(d["teams"])}<span class="of">/{NT}</span></td>'
                 f'<td>{d["cap"] or ""}</td>'
                 f'<td>{d["best"]}</td><td>{d["bosa"] or ""}</td>'
                 f'<td class="pz">{d["katki"]}</td>'
                 f'<td style="width:110px"><div class="bar">'
                 f'<i style="width:{max(3, round(100*d["katki"]/mx))}%"></i></div></td></tr>')
    heads = ("<th>#</th>" + th("Oyuncu") + th("Kulüp") + th("Pozisyon") + th("Seçim") + th("Oran")
             + th("Kaç takım") + th("Kaptanlık") + th("En iyi") + th("Boşa")
             + th("Katkı") + "<th></th>")
    md(f'<div class="scroll"><table class="tbl t-pl"><tr>{heads}</tr>{rows}</table></div>')
    st.caption(f"Listede en az bir kez seçilmiş {total} oyuncunun tamamı var. "
               "Oyuncu adının üstüne gelince hangi takımlarda olduğu çıkar; "
               "telefonda yukarıdaki detay kutusunu kullan. "
               f"Seçim = {slots} kadro slotunun kaçında yer aldığı "
               f"({NT} takım × {len(weeks)} hafta). Katkı kaptan çarpanı dahil. "
               "Boşa = yedekte kalan puan.")

with t3:
    c1, c2 = st.columns(2)
    tsel = c1.selectbox("Takım", sorted(weeks[-1]["teams"], key=tr_key))
    wsel = c2.selectbox("Maç haftası", [w["week"] for w in reversed(weeks)])
    wk = next(w for w in weeks if w["week"] == wsel)
    sq = wk["teams"].get(tsel)
    if not sq:
        st.info("Bu hafta bu takıma ait kadro yok.")
    else:
        rival = next((f["away"] if f["home"] == tsel else f["home"]
                      for f in wk["fixtures"] if tsel in (f["home"], f["away"])), "—")
        pill = (f'<span class="pill {CARD_CLS.get(sq["card"], "c-none")}">'
                f'{CARD_LABEL[sq["card"]]}</span>')
        md(f"""<div class="strip">
        <div class="s"><div class="l">MH Toplam</div><div class="v">{sq['mh']}</div>
        <div class="n">rakip: {rival}</div></div>
        <div class="s"><div class="l">Kart</div>
        <div class="v" style="font-size:15px;margin-top:7px">{pill}</div></div>
        <div class="s"><div class="l">Kaptan</div><div class="v">{sq['captain']}</div>
        <div class="n">vice: {sq['vice']}</div></div>
        <div class="s"><div class="l">Nostradamus</div><div class="v">{sq['nostradamus']}</div></div>
        </div>""")

        mult = sq["multiplier"]

        def chip(p, dim=False):
            """Kartta oyuncunun ekrana yansiyan puani gosterilir.

            Kaptan icin taban puan carpanla carpilir (x2/x3/x4); kucuk yazi
            olarak taban deger ve carpan da yazilir.
            """
            b, extra = "", ""
            if p["name"] == sq["captain"]:
                b = '<div class="badge bc">C</div>'
                if mult > 1:
                    extra = f'<span class="mx">{p["points"]}×{mult}</span>'
            elif p["name"] == sq["vice"]:
                b = '<div class="badge bv">V</div>'
            eff = p["points"] * mult if p["name"] == sq["captain"] else p["points"]
            return (f'<div class="pl{" dim" if dim else ""}">{b}'
                    f'<div class="p">{eff}{extra}</div><div class="n">{p["name"]}</div>'
                    f'<div class="c">{pos_of(p) + " · " if pos_of(p) else ""}{p["club"]}</div></div>')

        if not POS_FILE:
            pos_warning()
        lines = formation(sq["xi"])
        has_pos = all(pos_of(p) for p in sq["xi"])
        shape = ("-".join(str(len(ln)) for ln in lines[1:])
                 if has_pos and len(lines) > 1 else "")
        pitch = "".join(f'<div class="row">{"".join(chip(p) for p in ln)}</div>'
                        for ln in lines)
        md((f'<div class="sec">Diziliş {shape}</div>' if shape else '')
           + f'<div class="pitch">{pitch}</div>')
        counted = sq["card"] == "tum_takim"
        md(f'<div class="sec">Yedekler {"— sayıldı" if counted else "— sayılmadı"}</div>')
        md(f'<div class="row">{"".join(chip(p, not counted) for p in sq["bench"])}</div>')
        calc = team_points(sq)
        if calc != sq["mh"]:
            st.warning(f"Hesaplanan {calc}, ekrandaki {sq['mh']} ile uyuşmuyor.")

with t4:
    used = defaultdict(lambda: defaultdict(int))
    for w in weeks:
        for t, sq in w["teams"].items():
            if sq["card"]:
                used[t][sq["card"]] += 1
    allt = sorted({t for w in weeks for t in w["teams"]},
                  key=lambda t: (sum(used[t].values()), t), reverse=True)
    rows = ""
    for t in allt:
        cells = ""
        for k in CARD_KEYS:
            left = PER_TYPE - used[t][k]
            cells += ("<td>" + "".join(
                f'<span class="stk {"on" if j < left else "off"}"></span>'
                for j in range(PER_TYPE)) + "</td>")
        tot = PER_TYPE * len(CARD_KEYS) - sum(used[t].values())
        rows += f'<tr><td class="tm">{t}</td>{cells}<td class="pz">{tot}</td></tr>'
    heads = "".join(f"<th>{CARD_LABEL[k]}</th>" for k in CARD_KEYS)
    md(f'<div class="scroll"><table class="tbl t-card"><tr><th>Takım</th>{heads}<th>Kalan</th></tr>{rows}</table></div>')
    st.caption(f"Dolu nokta kalan hakkı gösterir. Her karttan {PER_TYPE}, "
               f"toplam {PER_TYPE*len(CARD_KEYS)}.")

    md('<div class="sec">Kart kullanım geçmişi</div>')
    log = ""
    for w in reversed(weeks):
        for t, sq in sorted(w["teams"].items(), key=lambda kv: -kv[1]["mh"]):
            if sq["card"]:
                log += (f'<tr><td>MH{w["week"]}</td><td class="tm">{t}</td>'
                        f'<td><span class="pill {CARD_CLS[sq["card"]]}">'
                        f'{CARD_LABEL[sq["card"]]}</span></td>'
                        f'<td class="pz">{sq["mh"]}</td></tr>')
    md('<div class="scroll"><table class="tbl t-log"><tr><th>Hafta</th><th>Takım</th><th>Kart</th>'
                f'<th>O hafta</th></tr>{log}</table></div>')

with t5:
    for w in reversed(weeks):
        with st.expander(f"Maç Haftası {w['week']}", expanded=(w["week"] == LAST)):
            rows = ""
            for f in w["fixtures"]:
                h, a = f["home_score"], f["away_score"]
                hc = "pz" if h > a else ("dn" if h < a else "eq")
                ac = "pz" if a > h else ("dn" if a < h else "eq")
                rows += (f'<tr><td class="{hc}" style="text-align:right">{f["home"]}</td>'
                         f'<td style="text-align:center;color:#fff;font-weight:800">{h} - {a}</td>'
                         f'<td class="{ac}" style="text-align:left">{f["away"]}</td></tr>')
            md(f'<div class="scroll"><table class="tbl t-res">{rows}</table></div>')
