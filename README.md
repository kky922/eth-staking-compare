# 💎 Ethereum Staking Yield Comparison

이더리움(ETH) 스테이킹 수익률 비교 분석 도구

## 📁 파일 구조

```
ethereum/
├── eth_staking_compare.py   # CLI 비교 분석 도구 (20개 프로토콜)
├── eth_dashboard.py          # Streamlit 웹 대시보드 (포트 8556)
├── start_eth_dashboard.sh    # 대시보드 실행 스크립트
└── README.md                 # 이 파일
```

## 🚀 실행 방법

### CLI 분석 도구
```bash
cd ~/ethereum
python3 eth_staking_compare.py
```

### 웹 대시보드
```bash
cd ~/ethereum
chmod +x start_eth_dashboard.sh
./start_eth_dashboard.sh
# 브라우저에서 http://localhost:8556 접속
```

## 📊 비교 카테고리 (20개 프로토콜)

| 카테고리 | 프로토콜 | 예상 APY |
|---------|---------|---------|
| 🏛️ 네이티브 스테이킹 | 직접 밸리데이터, SaaS/풀 | 2.8~4.0% |
| 💧 리퀴드 스테이킹 | Lido, Rocket Pool, Coinbase, Frax, StakeWise, Mantle | 2.5~4.5% |
| 🏦 DeFi 렌딩 | Aave V3, Compound V3, Spark | 0.5~3.0% |
| 🔄 레스테이킹 | EigenLayer, EtherFi, Puffer, Renzo | 4.0~10.0% |
| 📈 Vault / 자동화 | Yearn, Pendle | 3.5~8.0% |
| 🌊 DEX LP | Uniswap V3, Curve | 3.0~12.0% |

## 🔌 실시간 API 연동

- **ETH 가격**: CoinGecko API
- **Lido stETH APR**: Lido API
- **Rocket Pool rETH APR**: Rocket Pool API

## 📋 대시보드 탭

1. **📊 비교 테이블** - 전체 프로토콜 정렬/필터
2. **📈 시각화** - APY 바차트, 리스크-수익률 스캐터
3. **📋 프로토콜 상세** - 카드 형태 상세 정보
4. **🎯 추천 전략** - 보수형/중립형/공격형
5. **💰 수익 시뮬레이터** - 단리/복리 계산