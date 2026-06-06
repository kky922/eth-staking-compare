#!/usr/bin/env python3
"""
💎 이더리움(ETH) 스테이킹 수익률 비교 분석 도구
  - 네이티브 스테이킹, 리퀴드 스테이킹, DeFi 렌딩, 레스테이킹 등 비교
  - 실시간 데이터 수집 (가능한 경우) + 기준 수익률
"""

import json
import sys
import time

DATA_SNAPSHOT_DATE = "2026-06-07"


def effective_apy(option: "StakingOption") -> float:
    """Return live APY when available, otherwise the static midpoint."""
    if option.real_apy is not None:
        return option.real_apy
    return (option.apy_low + option.apy_high) / 2


def sort_by_effective_apy(options: list["StakingOption"]) -> list["StakingOption"]:
    return sorted(options, key=effective_apy, reverse=True)
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ═══════════════════════════════════════════════════
# 데이터 구조
# ═══════════════════════════════════════════════════

@dataclass
class StakingOption:
    """스테이킹 옵션 데이터 클래스"""
    name: str                    # 프로토콜/방식 이름
    category: str                # 카테고리 (네이티브, 리퀴드, DeFi, 레스테이킹 등)
    token_symbol: str            # LST 토큰 심볼
    apy_low: float               # 최소 예상 APY (%)
    apy_high: float              # 최대 예상 APY (%)
    tvl_eth: Optional[float]     # TVL (ETH 단위)
    risk_level: str              # LOW, MEDIUM, HIGH, VERY_HIGH
    liquidity: str               # HIGH, MEDIUM, LOW, NONE
    unbonding_period: str        # 언본딩 기간
    min_stake: float             # 최소 스테이킹 금액 (ETH)
    commission: float            # 수수료 (%)
    description: str             # 설명
    url: str                     # 공식 URL
    pros: list = field(default_factory=list)
    cons: list = field(default_factory=list)
    real_apy: Optional[float] = None  # API로 가져온 실시간 APY


# ═══════════════════════════════════════════════════
# 스테이킹 옵션 데이터베이스
# ═══════════════════════════════════════════════════

def get_staking_options() -> list[StakingOption]:
    """모든 스테이킹 옵션 목록 반환"""
    return [
        # ── 네이티브 스테이킹 ──
        StakingOption(
            name="네이티브 스테이킹 (직접 밸리데이터)",
            category="🏛️ 네이티브 스테이킹",
            token_symbol="ETH",
            apy_low=3.0, apy_high=4.0,
            tvl_eth=None,
            risk_level="LOW",
            liquidity="NONE",
            unbonding_period="출금 대기열 (수시간~수일)",
            min_stake=32.0,
            commission=0.0,
            description="32 ETH를 예치하여 밸리데이터를 직접 운영하는 가장 기본적인 방식",
            url="https://ethereum.org/staking/",
            pros=["가장 안전 (스마트 컨트랙트 리스크 없음)", "보상 직접 수령", "네트워크 보안에 직접 기여"],
            cons=["32 ETH 최소 요구 (대규모 자본)", "밸리데이터 운영 기술 필요", "슬래싱 리스크 (오프라인 시)"],
        ),
        StakingOption(
            name="네이티브 스테이킹 (SaaS / 풀)",
            category="🏛️ 네이티브 스테이킹",
            token_symbol="ETH",
            apy_low=2.8, apy_high=3.8,
            tvl_eth=None,
            risk_level="LOW",
            liquidity="NONE",
            unbonding_period="출금 대기열 (수시간~수일)",
            min_stake=32.0,
            commission=5.0,
            description="SaaS 제공자(비콘체인, Blox Staking 등)를 통한 밸리데이터 운영 위탁",
            url="https://beaconcha.in/",
            pros=["운영 부담 감소", "직접 스테이킹의 안전성", "출금 가능"],
            cons=["32 ETH 여전히 필요", "SaaS 수수료", "운영자 의존"],
        ),

        # ── 리퀴드 스테이킹 ──
        StakingOption(
            name="Lido (stETH)",
            category="💧 리퀴드 스테이킹",
            token_symbol="stETH",
            apy_low=3.0, apy_high=3.8,
            tvl_eth=9_500_000,
            risk_level="LOW",
            liquidity="HIGH",
            unbonding_period="즉시 (스왑 가능)",
            min_stake=0.001,
            commission=10.0,
            description="Lido 탈중앙화 리퀴드 스테이킹. 가장 큰 ETH 스테이킹 프로토콜",
            url="https://stake.lido.fi/",
            pros=["가장 큰 TVL (시장 지배적)", "DeFi 생태계 광범위 통합", "높은 유동성", "자동 컴파운딩"],
            cons=["노드 운영자 집중도 우려", "stETH/ETH 페깅 리스크", "10% 수수료"],
        ),
        StakingOption(
            name="Rocket Pool (rETH)",
            category="💧 리퀴드 스테이킹",
            token_symbol="rETH",
            apy_low=2.8, apy_high=3.6,
            tvl_eth=900_000,
            risk_level="LOW",
            liquidity="HIGH",
            unbonding_period="즉시 (스왑 가능)",
            min_stake=0.001,
            commission=0.0,
            description="Rocket Pool 탈중앙화 리퀴드 스테이킹. 노드 운영자는 16 ETH만 필요",
            url="https://rocketpool.net/",
            pros=["탈중앙화 중심 설계", "낮은 진입 장벽 (노드 16ETH)", "RPL 보너스", "검증된 프로토콜"],
            cons=["Lido 대비 낮은 TVL", "rETH/ETH 스프레드", "RPL 토큰 가격 변동"],
        ),
        StakingOption(
            name="Coinbase (cbETH)",
            category="💧 리퀴드 스테이킹",
            token_symbol="cbETH",
            apy_low=2.5, apy_high=3.2,
            tvl_eth=1_800_000,
            risk_level="LOW",
            liquidity="HIGH",
            unbonding_period="즉시 (스왑 가능) / 해지 (수일)",
            min_stake=0.001,
            commission=25.0,
            description="Coinbase 거래소 기반 리퀴드 스테이킹. 가장 간편한 접근",
            url="https://www.coinbase.com/earn/stake/ethereum",
            pros=["가장 간편한 UX", "높은 유동성", "Coinbase 보안", "초보자 친화적"],
            cons=["매우 높은 수수료 (25%)", "중앙화 위험", "Coinbase 계정 필요", "KYC 필요"],
        ),
        StakingOption(
            name="Frax Finance (sfrxETH)",
            category="💧 리퀴드 스테이킹",
            token_symbol="sfrxETH",
            apy_low=3.5, apy_high=4.5,
            tvl_eth=600_000,
            risk_level="LOW",
            liquidity="HIGH",
            unbonding_period="즉시 (스왑 가능)",
            min_stake=0.001,
            commission=0.0,
            description="Frax의 frxETH / sfrxETH 이자 누적 스테이킹. 높은 수익률",
            url="https://frax.com/",
            pros=["높은 수익률 (수수료 없음)", "자동 복리 (sfrxETH)", "DeFi 통합", "FRAX 생태계 시너지"],
            cons=["Frax 프로토콜 의존", "상대적으로 작은 TVL", "frxETH 베이스 APY 낮음"],
        ),
        StakingOption(
            name="StakeWise (OSETH)",
            category="💧 리퀴드 스테이킹",
            token_symbol="osETH",
            apy_low=3.0, apy_high=3.8,
            tvl_eth=200_000,
            risk_level="LOW",
            liquidity="MEDIUM",
            unbonding_period="즉시 (스왑 가능)",
            min_stake=0.001,
            commission=0.0,
            description="StakeWise 탈중앙화 리퀴드 스테이킹. 개별/풀 스테이킹 지원",
            url="https://stakewise.io/",
            pros=["유연한 스테이킹 옵션", "자동 컴파운딩", "출금 지원"],
            cons=["낮은 유동성", "작은 생태계", "인지도 낮음"],
        ),
        StakingOption(
            name="Mantle (mETH)",
            category="💧 리퀴드 스테이킹",
            token_symbol="mETH",
            apy_low=3.0, apy_high=3.6,
            tvl_eth=1_200_000,
            risk_level="LOW",
            liquidity="MEDIUM",
            unbonding_period="즉시 (스왑 가능)",
            min_stake=0.001,
            commission=0.0,
            description="Mantle 생태계 기반 리퀴드 스테이킹. Mantle L2와 통합",
            url="https://meth.mantle.xyz/",
            pros=["Mantle 생태계 시너지", "수수료 없음", "에어드랍 가능성"],
            cons=["Mantle L2 의존", "상대적으로 신규", "유동성 제한적"],
        ),

        # ── DeFi 렌딩 ──
        StakingOption(
            name="Aave V3 (ETH 렌딩)",
            category="🏦 DeFi 렌딩",
            token_symbol="ETH",
            apy_low=0.5, apy_high=3.0,
            tvl_eth=3_000_000,
            risk_level="MEDIUM",
            liquidity="HIGH",
            unbonding_period="즉시",
            min_stake=0.001,
            commission=0.0,
            description="Aave V3 렌딩 프로토콜에 ETH 예치. 대출 수요 기반 변동 금리",
            url="https://aave.com/",
            pros=["가장 큰 렌딩 프로토콜", "높은 유동성", "담보로 활용 가능", "다양한 네트워크"],
            cons=["낮은 수익률 (대출 수요 의존)", "변동 금리", "청산 리스크 (레버리지 시)"],
        ),
        StakingOption(
            name="Compound V3 (ETH)",
            category="🏦 DeFi 렌딩",
            token_symbol="ETH",
            apy_low=0.5, apy_high=2.5,
            tvl_eth=1_000_000,
            risk_level="MEDIUM",
            liquidity="HIGH",
            unbonding_period="즉시",
            min_stake=0.001,
            commission=0.0,
            description="Compound V3 렌딩 시장에 ETH 예치",
            url="https://compound.finance/",
            pros=["간편한 UX", "높은 유동성", "COMP 보너스 가능"],
            cons=["낮은 수익률", "대출 수요 의존", "V3는 단일 자산 시장"],
        ),
        StakingOption(
            name="Spark Protocol (Maker)",
            category="🏦 DeFi 렌딩",
            token_symbol="ETH",
            apy_low=1.0, apy_high=3.0,
            tvl_eth=1_500_000,
            risk_level="MEDIUM",
            liquidity="HIGH",
            unbonding_period="즉시",
            min_stake=0.001,
            commission=0.0,
            description="Spark Protocol (MakerDAO 하위) 렌딩에 ETH 예치",
            url="https://sparkprotocol.io/",
            pros=["MakerDAO 기반 안정성", "DAI 생태계 연동", "높은 유동성"],
            cons=["낮은 수익률", "상대적으로 신규 프로토콜", "Maker 거버넌스 의존"],
        ),

        # ── 레스테이킹 / AVS ──
        StakingOption(
            name="EigenLayer (ETH 레스테이킹)",
            category="🔄 레스테이킹",
            token_symbol="ETH",
            apy_low=4.0, apy_high=8.0,
            tvl_eth=4_000_000,
            risk_level="MEDIUM",
            liquidity="MEDIUM",
            unbonding_period="현재 제한적 (출금 활성화 예정)",
            min_stake=0.001,
            commission=0.0,
            description="EigenLayer 레스테이킹. AVS(Actively Validated Services)에 보안 제공",
            url="https://www.eigenlayer.xyz/",
            pros=["추가 보상 (AVS 인센티브)", "이더리움 보안 재활용", "성장 중인 생태계"],
            cons=["슬래싱 리스크 (AVS별)", "아직 초기 단계", "출금 제한 가능"],
        ),
        StakingOption(
            name="EtherFi (weETH)",
            category="🔄 레스테이킹",
            token_symbol="weETH",
            apy_low=4.5, apy_high=10.0,
            tvl_eth=2_000_000,
            risk_level="MEDIUM",
            liquidity="MEDIUM",
            unbonding_period="즉시 (스왑 가능)",
            min_stake=0.001,
            commission=0.0,
            description="EtherFi 비수탁형 레스테이킹. T-NFT 기반 노드 관리 + EigenLayer 통합",
            url="https://ether.fi/",
            pros=["비수탁형", "EigenLayer 자동 재스테이킹", "노드 서비스 수익", "에어드랍 가능"],
            cons=["복잡한 구조", "슬래싱 리스크", "신규 프로토콜"],
        ),
        StakingOption(
            name="Puffer Finance (pufETH)",
            category="🔄 레스테이킹",
            token_symbol="pufETH",
            apy_low=4.0, apy_high=10.0,
            tvl_eth=500_000,
            risk_level="HIGH",
            liquidity="MEDIUM",
            unbonding_period="즉시 (스왑 가능)",
            min_stake=0.001,
            commission=0.0,
            description="Puffer Finance Anti-Slashing 레스테이킹. 노드 운영자 2 ETH 진입 가능",
            url="https://www.puffer.fi/",
            pros=["Anti-Slashing 기술", "낮은 노드 진입 장벽 (2ETH)", "EigenLayer 통합", "에어드랍 기대"],
            cons=["신규 프로토콜", "높은 리스크", "아직 초기 단계"],
        ),
        StakingOption(
            name="Renzo (ezETH)",
            category="🔄 레스테이킹",
            token_symbol="ezETH",
            apy_low=4.0, apy_high=9.0,
            tvl_eth=1_200_000,
            risk_level="MEDIUM",
            liquidity="MEDIUM",
            unbonding_period="즉시 (스왑 가능)",
            min_stake=0.001,
            commission=0.0,
            description="Renzo Protocol 기반 LRT(Liquid Restaking Token). EigenLayer 자동 최적화",
            url="https://www.renzoprotocol.com/",
            pros=["자동 EigenLayer 전략", "LRT로 유동성 확보", "수수료 없음", "에어드랍 가능"],
            cons=["신규 프로토콜", "ezETH 탈페깅 사건 있었음", "AVS 리스크"],
        ),

        # ── Vault / 자동화 전략 ──
        StakingOption(
            name="Yearn Finance (yETH)",
            category="📈 Vault / 자동화",
            token_symbol="yETH",
            apy_low=3.5, apy_high=6.0,
            tvl_eth=100_000,
            risk_level="MEDIUM",
            liquidity="MEDIUM",
            unbonding_period="즉시 (풀 출금)",
            min_stake=0.001,
            commission=2.0,
            description="Yearn Finance 자동화 Vault. ETH 스테이킹 최적화 전략",
            url="https://yearn.fi/",
            pros=["자동 전략 최적화", "검증된 프로토콜", "다양한 전략 옵션"],
            cons=["수수료 (2% 퍼포먼스)", "낮은 TVL", "전략 리스크"],
        ),
        StakingOption(
            name="Pendle Finance (PT/YT)",
            category="📈 Vault / 자동화",
            token_symbol="PT-stETH",
            apy_low=4.0, apy_high=8.0,
            tvl_eth=500_000,
            risk_level="MEDIUM",
            liquidity="MEDIUM",
            unbonding_period="만기까지 보유 또는 스왑",
            min_stake=0.001,
            commission=0.3,
            description="Pendle의 PT(원금 토큰) / YT(수익 토큰) 분리 거래. 고정 수익률 확보 가능",
            url="https://www.pendle.finance/",
            pros=["고정 수익률 가능 (PT)", "수익률 거래 전략", "다양한 기간 옵션"],
            cons=["만기 관리 필요", "유동성 제한", "복잡한 메커니즘"],
        ),

        # ── DEX LP / 유동성 공급 ──
        StakingOption(
            name="Uniswap V3 (stETH/ETH)",
            category="🌊 DEX LP",
            token_symbol="LP",
            apy_low=3.0, apy_high=12.0,
            tvl_eth=None,
            risk_level="HIGH",
            liquidity="MEDIUM",
            unbonding_period="즉시 (풀 출금)",
            min_stake=0.1,
            commission=0.3,
            description="Uniswap V3 집중 유동성 풀에 stETH/ETH 쌍 공급",
            url="https://app.uniswap.org/",
            pros=["높은 거래 수수료 수익", "집중 유동성으로 효율적", "가장 큰 DEX"],
            cons=["비영구적 손실 (IL)", "가격 범위 관리 필요", "가스비 높음"],
        ),
        StakingOption(
            name="Curve Finance (stETH/ETH)",
            category="🌊 DEX LP",
            token_symbol="LP",
            apy_low=3.0, apy_high=10.0,
            tvl_eth=None,
            risk_level="MEDIUM",
            liquidity="HIGH",
            unbonding_period="즉시 (풀 출금)",
            min_stake=0.1,
            commission=0.04,
            description="Curve StableSwap 풀에 stETH/ETH 쌍 공급. 낮은 슬리피지",
            url="https://curve.fi/",
            pros=["낮은 IL (스테이블코인 페어)", "CRV 보상", "높은 유동성", "낮은 수수료"],
            cons=["낮은 거래 수수료", "CRV 가격 의존", "스마트 컨트랙트 리스크"],
        ),
    ]


# ═══════════════════════════════════════════════════
# 실시간 데이터 수집
# ═══════════════════════════════════════════════════

def get_eth_price() -> Optional[float]:
    """CoinGecko에서 ETH 가격 가져오기"""
    if not HAS_REQUESTS:
        return None
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()["ethereum"]["usd"]
    except Exception:
        pass
    return None


def get_lido_apy() -> Optional[float]:
    """Lido API에서 stETH APR 가져오기"""
    if not HAS_REQUESTS:
        return None
    try:
        url = "https://eth-api.lido.fi/v1/protocol/steth/apr/sma"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("data", {}).get("smaApr") or data.get("smaApr")
    except Exception:
        pass
    return None


def get_rocketpool_apy() -> Optional[float]:
    """Rocket Pool API에서 rETH APR 가져오기"""
    if not HAS_REQUESTS:
        return None
    try:
        url = "https://api.rocketpool.net/api/network?network=mainnet"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # Try different response structures
            if "networkBalances" in data:
                return data.get("networkBalances", {}).get("rethAPR")
            elif "rethAPR" in data:
                return data["rethAPR"]
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════
# 출력 함수
# ═══════════════════════════════════════════════════

# 터미널 색상
class C:
    """ANSI Color Codes"""
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BG_DARK = '\033[48;5;236m'

    @staticmethod
    def risk_color(level: str) -> str:
        colors = {
            "LOW": C.GREEN,
            "MEDIUM": C.YELLOW,
            "HIGH": C.RED,
            "VERY_HIGH": f"{C.RED}{C.BOLD}",
        }
        return colors.get(level, C.WHITE)

    @staticmethod
    def liquidity_color(level: str) -> str:
        colors = {
            "HIGH": C.GREEN,
            "MEDIUM": C.YELLOW,
            "LOW": C.RED,
            "NONE": f"{C.RED}{C.BOLD}",
        }
        return colors.get(level, C.WHITE)


def print_header():
    """헤더 출력"""
    print(f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   💎  이더리움(ETH) 스테이킹 수익률 비교 분석 리포트                       ║
║       Ethereum Staking Yield Comparison Dashboard                         ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝{C.RESET}
""")
    print(f"  기준 데이터: {DATA_SNAPSHOT_DATE} | API 값은 실행 시 조회, 실패 시 정적 범위 사용\n")


def print_eth_price(price: Optional[float]):
    """ETH 가격 출력"""
    if price:
        print(f"  {C.YELLOW}💰 ETH 현재 가격: ${price:,.2f}{C.RESET}\n")
    else:
        print(f"  {C.DIM}💰 ETH 가격: (API 연결 불가 - CoinGecko){C.RESET}\n")


def print_summary_table(options: list[StakingOption]):
    """요약 비교 테이블 출력"""
    print(f"  {C.BOLD}📊 스테이킹 수익률 비교 요약{C.RESET}")
    print(f"  {'='*90}")
    print(f"  {C.BOLD}{'프로토콜':<28} {'카테고리':<16} {'예상 APY':>12} {'리스크':>10} {'유동성':>10} {'수수료':>8}{C.RESET}")
    print(f"  {'-'*28} {'-'*16} {'-'*12} {'-'*10} {'-'*10} {'-'*8}")

    categories_order = [
        "🏛️ 네이티브 스테이킹",
        "💧 리퀴드 스테이킹",
        "🏦 DeFi 렌딩",
        "🔄 레스테이킹",
        "📈 Vault / 자동화",
        "🌊 DEX LP",
    ]

    for cat in categories_order:
        cat_options = [o for o in options if o.category == cat]
        if not cat_options:
            continue

        print(f"  {C.CYAN}{C.BOLD}{cat}{C.RESET}")

        for opt in cat_options:
            apy_str = f"{opt.apy_low:.1f}~{opt.apy_high:.1f}%"
            if opt.real_apy is not None:
                apy_str = f"{opt.real_apy:.2f}%*"

            risk_c = C.risk_color(opt.risk_level)
            liq_c = C.liquidity_color(opt.liquidity)

            name_display = opt.name[:26]
            if opt.token_symbol not in ("ETH", "LP"):
                name_display += f" ({opt.token_symbol})"

            print(f"    {name_display:<28} {opt.category.split(' ')[1] if ' ' in opt.category else '':<16} "
                  f"{C.GREEN}{apy_str:>12}{C.RESET} "
                  f"{risk_c}{opt.risk_level:>10}{C.RESET} "
                  f"{liq_c}{opt.liquidity:>10}{C.RESET} "
                  f"{opt.commission:>7.1f}%")

        print()

    print(f"  {'='*90}")


def print_detailed_analysis(options: list[StakingOption]):
    """상세 분석 출력"""
    print(f"\n  {C.BOLD}📋 상세 분석{C.RESET}")
    print(f"  {'='*90}")

    categories_order = [
        "🏛️ 네이티브 스테이킹",
        "💧 리퀴드 스테이킹",
        "🏦 DeFi 렌딩",
        "🔄 레스테이킹",
        "📈 Vault / 자동화",
        "🌊 DEX LP",
    ]

    for cat in categories_order:
        cat_options = [o for o in options if o.category == cat]
        if not cat_options:
            continue

        print(f"\n  {C.CYAN}{C.BOLD}{cat}{C.RESET}")
        print(f"  {'─'*80}")

        for opt in cat_options:
            risk_c = C.risk_color(opt.risk_level)
            liq_c = C.liquidity_color(opt.liquidity)

            apy_str = f"{opt.apy_low:.1f}% ~ {opt.apy_high:.1f}%"
            if opt.real_apy is not None:
                apy_str += f" (실시간: {opt.real_apy:.2f}%)"

            print(f"""
  {C.BOLD}{opt.name}{C.RESET} [{opt.token_symbol}]
    📊 예상 APY    : {C.GREEN}{apy_str}{C.RESET}
    💰 TVL (ETH)   : {f"{opt.tvl_eth:,.0f}" if opt.tvl_eth else "N/A":>12}
    ⚠️  리스크     : {risk_c}{opt.risk_level}{C.RESET}
    🔄 유동성      : {liq_c}{opt.liquidity}{C.RESET}
    ⏰ 언본딩      : {opt.unbonding_period}
    💵 최소 금액   : {opt.min_stake} ETH
    📝 설명        : {opt.description}
    🔗 URL         : {C.BLUE}{opt.url}{C.RESET}
    ✅ 장점        : {', '.join(opt.pros)}
    ❌ 단점        : {', '.join(opt.cons)}""")

        print()


def print_risk_matrix():
    """리스크 매트릭스 출력"""
    print(f"""
  {C.BOLD}⚖️ 리스크 vs 수익률 매트릭스{C.RESET}
  {'='*90}

  수익률 ↑
   12% │                                         {C.RED}■{C.RESET} EtherFi    {C.RED}■{C.RESET} Puffer
       │                               {C.RED}■{C.RESET} Renzo
   10% │              {C.RED}■{C.RESET} EigenLayer    {C.RED}■{C.RESET} DEX LP (Uni)
       │
    8% │                               {C.YELLOW}■{C.RESET} Pendle
       │
    6% │              {C.YELLOW}■{C.RESET} Yearn        {C.MAGENTA}■{C.RESET} Frax
       │
    4% │ {C.GREEN}■{C.RESET} Native   {C.GREEN}■{C.RESET} Lido    {C.GREEN}■{C.RESET} Rocket Pool
       │ {C.GREEN}■{C.RESET} Coinbase {C.GREEN}■{C.RESET} Mantle  {C.GREEN}■{C.RESET} StakeWise
    3% │              {C.YELLOW}■{C.RESET} Aave         {C.YELLOW}■{C.RESET} Compound
       │              {C.YELLOW}■{C.RESET} Spark
    1% │
       └──────────────────────────────────────────────────→ 리스크
          {C.GREEN}LOW{C.RESET}          {C.YELLOW}MEDIUM{C.RESET}              {C.RED}HIGH{C.RESET}         {C.RED}VERY_HIGH{C.RESET}
""")


def print_recommendations():
    """투자 성향별 추천 출력"""
    print(f"""
  {C.BOLD}🎯 투자 성향별 추천 전략{C.RESET}
  {'='*90}

  {C.GREEN}{C.BOLD}🟢 보수형 (안전 최우선){C.RESET}
  ──────────────────────────────────────
  1위: {C.BOLD}네이티브 스테이킹{C.RESET} - 스마트 컨트랙트 리스크 제로
  2위: {C.BOLD}Lido (stETH){C.RESET} - 가장 검증된 리퀴드 스테이킹
  3위: {C.BOLD}Rocket Pool (rETH){C.RESET} - 탈중앙화 중심

  💡 추천: 자본의 70% Lido stETH + 30% Rocket Pool

  {C.YELLOW}{C.BOLD}🟡 중립형 (수익/안정 균형){C.RESET}
  ──────────────────────────────────────
  1위: {C.BOLD}Lido (stETH){C.RESET} - 최고의 유동성과 안정성
  2위: {C.BOLD}EtherFi (weETH){C.RESET} - 레스테이킹 보너스
  3위: {C.BOLD}Frax (sfrxETH){C.RESET} - 높은 수익률

  💡 추천: 50% Lido + 30% EtherFi + 20% Frax

  {C.RED}{C.BOLD}🔴 공격형 (최대 수익 추구){C.RESET}
  ──────────────────────────────────────
  1위: {C.BOLD}EtherFi (weETH){C.RESET} - 레스테이킹 + 에어드랍
  2위: {C.BOLD}Puffer (pufETH){C.RESET} - 높은 인센티브 기대
  3위: {C.BOLD}Uniswap V3 LP{C.RESET} - 거래 수수료 수익

  💡 추천: 40% EtherFi + 30% EigenLayer + 20% Puffer + 10% LP

  {C.MAGENTA}{C.BOLD}🟣 DeFi 파워 유저{C.RESET}
  ──────────────────────────────────────
  1위: {C.BOLD}stETH → Curve LP{C.RESET} - 낮은 IL + CRV 보상
  2위: {C.BOLD}stETH → Aave 담보{C.RESET} - 대출 + 레버리지 루핑
  3위: {C.BOLD}PT-stETH (Pendle){C.RESET} - 고정 수익률 확보

  💡 추천: LST를 담보로 레버리지 루핑 (청산 리스크 주의!)
""")


def print_tax_tips():
    """세금/주의사항 출력"""
    print(f"""
  {C.BOLD}⚠️ 주의사항 & 세금{C.RESET}
  {'='*90}

  📌 세금 (한국 기준)
  • 스테이킹 보상은 {C.YELLOW}기타소득{C.RESET}으로 분류 가능 (2025년 이전)
  • 2025년부터 {C.YELLOW}가상자산소득세{C.RESET} 과세 (연 250만원 이상)
  • LST 토큰 스왑 시 {C.YELLOW}양도소득세{C.RESET} 발생 가능
  • 실현 수익만 과세 (미실현 보상은 X)

  📌 리스크 체크리스트
  • {C.GREEN}□{C.RESET} 밸리데이터 평판/성과 확인
  • {C.GREEN}□{C.RESET} 프로토콜 감사(audit) 여부
  • {C.GREEN}□{C.RESET} TVL 규모와 유동성
  • {C.GREEN}□{C.RESET} 스마트 컨트랙트 버그 리스크
  • {C.GREEN}□{C.RESET} 슬래싱 가능 여부
  • {C.GREEN}□{C.RESET} 언본딩 기간 숙지

  📌 모니터링 추천 도구
  • Lido: https://stake.lido.fi/ (stETH 스테이킹)
  • Rocket Pool: https://rocketpool.net/ (rETH 스테이킹)
  • EigenLayer: https://www.eigenlayer.xyz/ (레스테이킹)
  • DeFiLlama: https://defillama.com/chain/Ethereum (TVL)
  • Beacon Chain: https://beaconcha.in/ (밸리데이터 모니터링)
""")


def print_simulation(options: list[StakingOption], eth_price: Optional[float]):
    """수익 시뮬레이션"""
    print(f"\n  {C.BOLD}💰 수익 시뮬레이션 (10 ETH 기준, 1년){C.RESET}")
    print(f"  {'='*90}")

    if eth_price:
        eth_val = 10 * eth_price
        print(f"  투자금액: 10 ETH = ${eth_val:,.2f}\n")

    principal_eth = 10

    picks = {
        "🏛️ 네이티브 스테이킹": next((o for o in options if o.category == "🏛️ 네이티브 스테이킹"), None),
        "💧 Lido (stETH)": next((o for o in options if "Lido" in o.name), None),
        "💧 Rocket Pool": next((o for o in options if "Rocket Pool" in o.name and "rETH" in o.token_symbol), None),
        "💧 Frax (sfrxETH)": next((o for o in options if "Frax" in o.name), None),
        "🏦 DeFi 렌딩": next((o for o in options if o.category == "🏦 DeFi 렌딩"), None),
        "🔄 EtherFi": next((o for o in options if "EtherFi" in o.name), None),
        "🔄 EigenLayer": next((o for o in options if "EigenLayer" in o.name), None),
        "📈 Pendle": next((o for o in options if "Pendle" in o.name), None),
    }

    print(f"  {'방식':<24} {'APY(평균)':>10} {'1년 후 ETH':>12} {'ETH 수익':>10} {'USD 수익*':>14}")
    print(f"  {'-'*24} {'-'*10} {'-'*12} {'-'*10} {'-'*14}")

    for label, opt in picks.items():
        if not opt:
            continue
        avg_apy = (opt.apy_low + opt.apy_high) / 2
        final_eth = principal_eth * (1 + avg_apy / 100)
        eth_gain = final_eth - principal_eth
        usd_gain = eth_gain * eth_price if eth_price else 0

        apy_str = f"{avg_apy:.1f}%"
        final_str = f"{final_eth:.4f}"
        gain_str = f"+{eth_gain:.4f}"
        usd_str = f"${usd_gain:,.2f}" if eth_price else "N/A"

        print(f"  {label:<24} {C.GREEN}{apy_str:>10}{C.RESET} {final_str:>12} "
              f"{C.GREEN}{gain_str:>10}{C.RESET} {C.YELLOW}{usd_str:>14}{C.RESET}")

    print(f"\n  {C.DIM}* 복리 효과 미적용 (단리 기준). 월 복리 시 수익 약 5~15% 추가{C.RESET}")
    if eth_price:
        print(f"  {C.DIM}* USD 수익은 현재 ETH 가격 기준. 실제 수익은 ETH 가격 변동에 따라 다름{C.RESET}")


def print_category_summary():
    """카테고리별 요약"""
    print(f"""
  {C.BOLD}📋 카테고리별 한 줄 요약{C.RESET}
  {'='*90}

  {C.GREEN}🏛️ 네이티브 스테이킹{C.RESET}
     → {C.BOLD}가장 안전{C.RESET}. 스마트 컨트랙트 리스크 없음. 3.0~4.0% APY.
     → 추천 대상: 대규모 자본 보유자, 장기 홀더

  {C.CYAN}💧 리퀴드 스테이킹{C.RESET}
     → {C.BOLD}안전 + 유동성{C.RESET}. Lido가 시장 지배적. 3.0~4.5% APY.
     → 추천 대상: 대부분의 투자자 (가장 인기)

  {C.YELLOW}🏦 DeFi 렌딩{C.RESET}
     → {C.BOLD}낮은 수익, 높은 유동성{C.RESET}. 담보로 활용 가능. 0.5~3.0% APY.
     → 추천 대상: 레버리지 전략, 단기 예치

  {C.RED}🔄 레스테이킹{C.RESET}
     → {C.BOLD}높은 수익, 중간 리스크{C.RESET}. EigenLayer 기반. 4.0~10.0% APY.
     → 추천 대상: 공격적 투자자, 에어드랍 헌터

  {C.MAGENTA}📈 Vault / 자동화{C.RESET}
     → {C.BOLD}전략형 수익{C.RESET}. 자동 복리. 3.5~8.0% APY (리스크 다양).
     → 추천 대상: 수동 관리 피하고 싶은 투자자

  {C.BLUE}🌊 DEX LP{C.RESET}
     → {C.BOLD}높은 변동 수익{C.RESET}. IL 리스크. 3.0~12.0% APY.
     → 추천 대상: DeFi 숙련자, 적극적 관리 가능
""")


# ═══════════════════════════════════════════════════
# 메인 실행
# ═══════════════════════════════════════════════════

def main():
    print_header()

    # 데이터 수집
    eth_price = get_eth_price()
    print_eth_price(eth_price)

    # 스테이킹 옵션 로드
    options = get_staking_options()

    # 실시간 데이터 시도
    print(f"  {C.DIM}📡 실시간 데이터 수집 중...{C.RESET}")
    lido_apy = get_lido_apy()
    if lido_apy and isinstance(lido_apy, (int, float)):
        for opt in options:
            if "Lido" in opt.name:
                opt.real_apy = float(lido_apy)
                print(f"  {C.GREEN}✅ Lido 실시간 APR: {lido_apy:.2f}%{C.RESET}")
    else:
        print(f"  {C.DIM}⚠️ Lido API: 연결 불가{C.RESET}")

    rp_apy = get_rocketpool_apy()
    if rp_apy and isinstance(rp_apy, (int, float)):
        for opt in options:
            if "Rocket Pool" in opt.name and "rETH" in opt.token_symbol:
                opt.real_apy = float(rp_apy)
                print(f"  {C.GREEN}✅ Rocket Pool 실시간 APR: {rp_apy:.2f}%{C.RESET}")
    else:
        print(f"  {C.DIM}⚠️ Rocket Pool API: 연결 불가{C.RESET}")

    print()

    # 출력
    print_summary_table(options)
    print_risk_matrix()
    print_category_summary()
    print_simulation(options, eth_price)
    print_detailed_analysis(options)
    print_recommendations()
    print_tax_tips()

    # 푸터
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"  {C.DIM}분석 일시: {now} | 데이터 출처: CoinGecko, Lido API, Rocket Pool API, 프로토콜 공식 자료{C.RESET}")
    print(f"  {C.DIM}※ 수익률은 예상치이며 실제와 다를 수 있습니다. 투자 전 DYOR!{C.RESET}")
    print(f"  {C.DIM}※ API로 가져온 실시간 데이터는 * 표시{C.RESET}\n")


if __name__ == "__main__":
    main()
