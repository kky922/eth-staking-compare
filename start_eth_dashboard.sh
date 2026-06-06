#!/bin/bash
cd "$(dirname "$0")"
echo "💎 ETH 스테이킹 비교 대시보드 시작 (포트 8556)..."
streamlit run eth_dashboard.py --server.port 8556 --server.address 0.0.0.0