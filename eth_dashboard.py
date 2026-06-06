#!/usr/bin/env python3
"""
💎 Ethereum Staking Dashboard - Streamlit Web UI
포트 8556에서 실행
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys, os

# eth_staking_compare 모듈 import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eth_staking_compare import (
    get_staking_options, get_eth_price, get_lido_apy, get_rocketpool_apy
)

# ── 페이지 설정 ──
st.set_page_config(
    page_title="💎 ETH 스테이킹 비교",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 데이터 로드 ──
@st.cache_data(ttl=300)
def load_data():
    options = get_staking_options()
    eth_price = get_eth_price()
    lido_apy = get_lido_apy()
    rp_apy = get_rocketpool_apy()
    if lido_apy:
        for o in options:
            if "Lido" in o.name:
                o.real_apy = float(lido_apy)
    if rp_apy:
        for o in options:
            if "Rocket Pool" in o.name and "rETH" in o.token_symbol:
                o.real_apy = float(rp_apy)
    return options, eth_price

options, eth_price = load_data()

# ── 사이드바 ──
# ETH 로고 (온라인 이미지 로드 실패 시 생략)
try:
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Ethereum_logo_2014.svg/250px-Ethereum_logo_2014.svg.png", width=80)
except:
    pass
st.sidebar.title("💎 ETH 스테이킹")
if eth_price:
    st.sidebar.metric("ETH 가격", f"${eth_price:,.2f}")
st.sidebar.markdown("---")

categories = list(dict.fromkeys(o.category for o in options))
sel_cats = st.sidebar.multiselect("카테고리", categories, default=categories)
risk_filter = st.sidebar.multiselect("리스크", ["LOW","MEDIUM","HIGH","VERY_HIGH"], default=["LOW","MEDIUM","HIGH","VERY_HIGH"])

filtered = [o for o in options if o.category in sel_cats and o.risk_level in risk_filter]

# ── 탭 ──
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 비교 테이블", "📈 시각화", "📋 프로토콜 상세", "🎯 추천 전략", "💰 수익 시뮬레이터"])

with tab1:
    st.title("📊 ETH 스테이킹 수익률 비교")
    rows = []
    for o in filtered:
        avg = (o.apy_low + o.apy_high) / 2
        rows.append({
            "프로토콜": o.name, "토큰": o.token_symbol, "카테고리": o.category,
            "평균 APY(%)": avg, "최소(%)": o.apy_low, "최대(%)": o.apy_high,
            "리스크": o.risk_level, "유동성": o.liquidity, "수수료(%)": o.commission,
            "최소금액(ETH)": o.min_stake, "언본딩": o.unbonding_period,
            "TVL(ETH)": o.tvl_eth or 0,
        })
    df = pd.DataFrame(rows)
    st.dataframe(df.style.format({"평균 APY(%)": "{:.1f}", "최소(%)": "{:.1f}", "최대(%)": "{:.1f}", "수수료(%)": "{:.1f}"}), width="stretch", height=600)

with tab2:
    st.title("📈 수익률 시각화")
    if filtered:
        df_chart = pd.DataFrame([{"name": o.name, "category": o.category, "apy": (o.apy_low+o.apy_high)/2, "risk": o.risk_level, "tvl": o.tvl_eth or 0, "liquidity": o.liquidity} for o in filtered])
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(df_chart.sort_values("apy", ascending=True), x="apy", y="name", color="category", title="APY 비교", orientation="h", height=500)
            st.plotly_chart(fig, width="stretch")
        with c2:
            risk_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "VERY_HIGH": 4}
            df_chart["risk_num"] = df_chart["risk"].map(risk_map)
            fig2 = px.scatter(df_chart, x="risk_num", y="apy", size="tvl", color="category", hover_name="name", title="리스크 vs 수익률", height=500)
            fig2.update_xaxes(tickvals=[1,2,3,4], ticktext=["LOW","MEDIUM","HIGH","V_HIGH"])
            st.plotly_chart(fig2, width="stretch")

with tab3:
    st.title("📋 프로토콜 상세")
    for cat in list(dict.fromkeys(o.category for o in filtered)):
        st.subheader(cat)
        cols = st.columns(3)
        cat_opts = [o for o in filtered if o.category == cat]
        for i, o in enumerate(cat_opts):
            with cols[i % 3]:
                apy_str = f"{o.apy_low:.1f}% ~ {o.apy_high:.1f}%"
                if o.real_apy: apy_str += f" (실시간: {o.real_apy:.2f}%)"
                st.markdown(f"**{o.name}** [{o.token_symbol}]")
                st.caption(o.description)
                st.write(f"📊 APY: {apy_str}")
                st.write(f"⚠️ 리스크: {o.risk_level} | 🔄 유동성: {o.liquidity}")
                st.write(f"💵 최소: {o.min_stake} ETH | 수수료: {o.commission}%")
                if o.pros: st.write("✅ " + ", ".join(o.pros[:2]))
                if o.cons: st.write("❌ " + ", ".join(o.cons[:2]))
                st.markdown(f"[🔗 공식사이트]({o.url})")
                st.markdown("---")

with tab4:
    st.title("🎯 투자 성향별 추천")
    profiles = {
        "🟢 보수형": {"desc": "70% Lido stETH + 30% Rocket Pool", "opts": [o for o in options if "Lido" in o.name or ("Rocket Pool" in o.name and "rETH" in o.token_symbol)]},
        "🟡 중립형": {"desc": "50% Lido + 30% EtherFi + 20% Frax", "opts": [o for o in options if any(k in o.name for k in ["Lido", "EtherFi", "Frax"])]},
        "🔴 공격형": {"desc": "40% EtherFi + 30% EigenLayer + 20% Puffer + 10% LP", "opts": [o for o in options if any(k in o.name for k in ["EtherFi", "EigenLayer", "Puffer"])]},
    }
    for name, p in profiles.items():
        st.subheader(name)
        st.info(p["desc"])
        for o in p["opts"]:
            st.write(f"- **{o.name}**: {(o.apy_low+o.apy_high)/2:.1f}% APY | {o.risk_level}")

with tab5:
    st.title("💰 수익 시뮬레이터")
    eth_amt = st.number_input("ETH 수량", value=10.0, min_value=0.01, step=1.0)
    period = st.selectbox("기간", ["30일","90일","180일","1년","3년"], index=3)
    period_map = {"30일": 30/365, "90일": 90/365, "180일": 180/365, "1년": 1.0, "3년": 3.0}
    compound = st.checkbox("복리 적용", value=True)
    yr = period_map[period]

    results = []
    for o in filtered:
        avg = (o.apy_low + o.apy_high) / 100
        if compound:
            final = eth_amt * (1 + avg) ** yr
        else:
            final = eth_amt * (1 + avg * yr)
        gain = final - eth_amt
        results.append({"프로토콜": o.name, "APY(%)": avg*100, "최종 ETH": final, "수익 ETH": gain, "수익 USD": gain * (eth_price or 0)})
    df_sim = pd.DataFrame(results).sort_values("수익 ETH", ascending=False)
    # 수익에 +/- 부호 포맷팅
    df_sim_display = df_sim.copy()
    df_sim_display["수익 ETH"] = df_sim_display["수익 ETH"].apply(lambda x: f"+{x:.4f}" if x >= 0 else f"{x:.4f}")
    df_sim_display["수익 USD"] = df_sim_display["수익 USD"].apply(lambda x: f"+${x:,.2f}" if x >= 0 else f"-${abs(x):,.2f}")
    df_sim_display["APY(%)"] = df_sim_display["APY(%)"].apply(lambda x: f"{x:.1f}")
    df_sim_display["최종 ETH"] = df_sim_display["최종 ETH"].apply(lambda x: f"{x:.4f}")
    st.dataframe(df_sim_display, width="stretch")

st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')} | 💎 ETH Staking Dashboard v1.0 | 포트 8556")