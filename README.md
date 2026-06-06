# Ethereum Staking Compare

Ethereum 스테이킹·리퀴드 스테이킹·DeFi 옵션의 수익률과 위험을 비교하는 CLI 및
Streamlit 대시보드입니다.

## 기능

- 정적 기준 범위와 실행 시 조회한 API 값을 구분
- APY, 유동성, 언본딩 기간, 최소 예치액, 위험 수준 비교
- API 장애 시 정적 데이터로 계속 동작
- CLI 리포트와 웹 대시보드

## 설치

```bash
git clone https://github.com/kky922/eth-staking-compare.git
cd eth-staking-compare
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 설정

API 키는 필요하지 않습니다. 외부 공개 API를 사용할 수 없으면 저장소의 기준 범위를 표시합니다.

## 실행

```bash
python eth_staking_compare.py
streamlit run eth_dashboard.py --server.port 8556
```

## 테스트

```bash
pytest -q
```

## 주의사항

표시된 수익률은 보장되지 않으며 프로토콜, 스마트 컨트랙트, 유동성, 슬래싱과 가격
변동 위험이 있습니다. 투자·세무 자문이 아닙니다.

## 라이선스

MIT
