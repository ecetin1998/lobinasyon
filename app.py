# -*- coding: utf-8 -*-
"""Lobinasyon — TFF Fantasy mini lig takip paneli."""
import json, glob, os
from collections import defaultdict

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Lobinasyon", page_icon="⚽", layout="wide")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CARD_LABEL = {
    "tum_takim": "Tüm Takım Sahaya",
    "dort_dortluk": "Dört Dörtlük (x4)",
    "tripleks": "Tripleks (x3)",
    "hucum": "Hücum!",
    "limitsiz": "Limitsiz Bütçe",
    None: "—",
}
CARD_KEYS = ["tum_takim", "dort_dortluk", "tripleks", "hucum", "limitsiz"]
PER_TYPE = 2


@st.cache_data
def load_weeks():
    weeks = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "gw*.json"))):
        with open(path, encoding="utf-8") as f:
            weeks.append(json.load(f))
    return weeks


def team_points(sq):
    """Kadro puanını yeniden hesaplar; JSON'daki mh ile karşılaştırmak için."""
    mult = sq["multiplier"]
    total = sum(p["points"] * (mult if p["name"] == sq["captain"] else 1) for p in sq["xi"])
    if sq["card"] == "tum_takim":
        total += sum(p["points"] for p in sq["bench"])
    return total + sq["nostradamus"]


def standings(weeks, upto=None):
    tbl = defaultdict(lambda: dict(O=0, G=0, B=0, M=0, A=0, Y=0))
    for w in weeks:
        if upto is not None and w["week"] > upto:
            continue
        for f in w["fixtures"]:
            pairs = ((f["home"], f["home_score"], f["away_score"]),
                     (f["away"], f["away_score"], f["home_score"]))
            for name, sf, sa in pairs:
                r = tbl[name]
                r["O"] += 1; r["A"] += sf; r["Y"] += sa
                if sf > sa: r["G"] += 1
                elif sf == sa: r["B"] += 1
                else: r["M"] += 1
    rows = []
    for name, r in tbl.items():
        rows.append({"Takım": name, **r, "AV": r["A"] - r["Y"], "P": r["G"] * 3 + r["B"]})
    df = pd.DataFrame(rows).sort_values(["P", "AV", "A"], ascending=False).reset_index(drop=True)
    df.index += 1
    return df


def player_stats(weeks):
    pl = defaultdict(lambda: dict(club="", sec=0, xi=0, bench=0, cap=0,
                                  katki=0, bosa=0, best=0, teams=set()))
    for w in weeks:
        for tname, sq in w["teams"].items():
            mult, counts_bench = sq["multiplier"], sq["card"] == "tum_takim"
            for p in sq["xi"]:
                d = pl[p["name"]]; d["club"] = p["club"]
                d["sec"] += 1; d["xi"] += 1; d["teams"].add(tname)
                d["best"] = max(d["best"], p["points"])
                d["katki"] += p["points"] * (mult if p["name"] == sq["captain"] else 1)
                if p["name"] == sq["captain"]: d["cap"] += 1
            for p in sq["bench"]:
                d = pl[p["name"]]; d["club"] = p["club"]
                d["sec"] += 1; d["bench"] += 1; d["teams"].add(tname)
                d["best"] = max(d["best"], p["points"])
                if counts_bench: d["katki"] += p["points"]
                else: d["bosa"] += p["points"]
    n_teams = max(len(w["teams"]) for w in weeks)
    slots = n_teams * len(weeks)
    rows = [{
        "Oyuncu": n, "Kulüp": d["club"],
        "Seçim": f'{d["sec"]}/{slots}', "Oran %": round(100 * d["sec"] / slots),
        "Kaç takım": f'{len(d["teams"])}/{n_teams}',
        "11'de": d["xi"], "C": d["cap"], "Katkı": d["katki"],
        "En iyi hafta": d["best"], "Boşa": d["bosa"],
    } for n, d in pl.items()]
    return (pd.DataFrame(rows).sort_values("Katkı", ascending=False).reset_index(drop=True),
            n_teams, slots)


def card_stock(weeks):
    used = defaultdict(lambda: defaultdict(int))
    teams = set()
    for w in weeks:
        for t, sq in w["teams"].items():
            teams.add(t)
            if sq["card"]:
                used[t][sq["card"]] += 1
    rows = []
    for t in sorted(teams):
        row = {"Takım": t}
        for k in CARD_KEYS:
            row[CARD_LABEL[k]] = PER_TYPE - used[t][k]
        row["Kalan"] = PER_TYPE * len(CARD_KEYS) - sum(used[t].values())
        rows.append(row)
    return pd.DataFrame(rows).sort_values("Kalan").reset_index(drop=True)


weeks = load_weeks()
if not weeks:
    st.error("data/ klasöründe gw*.json bulunamadı.")
    st.stop()

last = weeks[-1]["week"]
st.title("⚽ Lobinasyon")
st.caption(f"TFF Fantasy mini lig · Maç Haftası 1–{last} · {len(weeks[-1]['teams'])} takım")

tab_std, tab_pl, tab_team, tab_card, tab_res = st.tabs(
    ["Puan Durumu", "Oyuncular", "Takım Detayı", "Kartlar", "Sonuçlar"])

with tab_std:
    df = standings(weeks)
    if len(weeks) > 1:
        prev = {r["Takım"]: i for i, r in standings(weeks, last - 1).iterrows()}
        cur = {r["Takım"]: i for i, r in df.iterrows()}
        df.insert(1, "±", [
            ("–" if prev.get(t, cur[t]) == cur[t]
             else f"▲{prev[t]-cur[t]}" if prev.get(t, cur[t]) > cur[t]
             else f"▼{cur[t]-prev[t]}")
            for t in df["Takım"]])
    st.dataframe(df, use_container_width=True)
    st.caption("± sütunu bir önceki maç haftasına göre sıra değişimi.")

    weekly = pd.DataFrame({
        w["week"]: {t: sq["mh"] for t, sq in w["teams"].items()} for w in weeks})
    sel = st.multiselect("Haftalık puan grafiği", sorted(weekly.index),
                         default=list(df["Takım"].head(4)))
    if sel:
        st.line_chart(weekly.loc[sel].T)

with tab_pl:
    pdf, n_teams, slots = player_stats(weeks)
    c1, c2 = st.columns(2)
    min_sec = c1.slider("En az kaç kez seçilmiş", 1, 20, 1)
    club = c2.selectbox("Kulüp", ["Hepsi"] + sorted(pdf["Kulüp"].unique()))
    f = pdf[pdf["Seçim"].str.split("/").str[0].astype(int) >= min_sec]
    if club != "Hepsi":
        f = f[f["Kulüp"] == club]
    st.dataframe(f, use_container_width=True, height=560)
    st.caption(f"Seçim = {slots} kadro slotunun kaçında yer aldığı ({n_teams} takım × {len(weeks)} hafta). "
               "Katkı, kaptan çarpanı dahil toplam getirisi. Boşa = yedekte kalan puan.")

with tab_team:
    names = sorted(weeks[-1]["teams"])
    tsel = st.selectbox("Takım", names)
    wsel = st.selectbox("Maç haftası", [w["week"] for w in reversed(weeks)])
    sq = next(w for w in weeks if w["week"] == wsel)["teams"].get(tsel)
    if not sq:
        st.info("Bu hafta bu takıma ait kadro yok.")
    else:
        a, b, c, d = st.columns(4)
        a.metric("MH Toplam", sq["mh"])
        b.metric("Kart", CARD_LABEL[sq["card"]])
        c.metric("Kaptan", sq["captain"])
        d.metric("Nostradamus", sq["nostradamus"])
        st.write("**İlk 11**")
        st.dataframe(pd.DataFrame(sq["xi"]).rename(
            columns={"name": "Oyuncu", "club": "Kulüp", "points": "Puan"}),
            use_container_width=True, hide_index=True)
        st.write("**Yedekler**")
        st.dataframe(pd.DataFrame(sq["bench"]).rename(
            columns={"name": "Oyuncu", "club": "Kulüp", "points": "Puan"}),
            use_container_width=True, hide_index=True)
        calc = team_points(sq)
        if calc != sq["mh"]:
            st.warning(f"Hesaplanan {calc}, ekrandaki {sq['mh']} ile uyuşmuyor.")

with tab_card:
    st.dataframe(card_stock(weeks), use_container_width=True)
    st.caption(f"Her karttan {PER_TYPE} hak, toplam {PER_TYPE*len(CARD_KEYS)}. "
               "Sayılar kalan hakkı gösterir.")
    log = [{"Hafta": w["week"], "Takım": t, "Kart": CARD_LABEL[sq["card"]], "O hafta": sq["mh"]}
           for w in weeks for t, sq in w["teams"].items() if sq["card"]]
    st.write("**Kart kullanım geçmişi**")
    st.dataframe(pd.DataFrame(log).sort_values(["Hafta", "O hafta"], ascending=[False, False]),
                 use_container_width=True, hide_index=True)

with tab_res:
    for w in reversed(weeks):
        with st.expander(f"Maç Haftası {w['week']}", expanded=(w["week"] == last)):
            st.dataframe(pd.DataFrame([
                {"Ev": f["home"], "Skor": f'{f["home_score"]} - {f["away_score"]}',
                 "Deplasman": f["away"]} for f in w["fixtures"]]),
                use_container_width=True, hide_index=True)
