import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="GC Xpress Betting Agent", layout="wide")

# 侧边栏配置
st.sidebar.header("🛠️ 核心配置")
API_KEY = st.sidebar.text_input("The Odds API Key", type="password")
TELEGRAM_TOKEN = st.sidebar.text_input("Telegram Bot Token")
CHAT_ID = st.sidebar.text_input("Telegram Chat ID")

st.sidebar.markdown("---")
threshold = st.sidebar.slider("预警门槛 (Edge %)", 0.0, 15.0, 5.0)

st.title("🏇 GC Xpress 赔率监控中心")

if not API_KEY:
    st.warning("请在左侧填入 API Key 开始运行")
else:
    st.info("系统正在实时扫描澳洲赛场 (Horse Racing & Greyhounds)...")
    # 这里是简化版逻辑，确保页面能先跑起来
    st.write("等待数据接入...")
    
    if st.button("手动测试 Telegram 通知"):
        if TELEGRAM_TOKEN and CHAT_ID:
            test_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text=GC_Xpress_测试成功!_代理已上线"
            requests.get(test_url)
            st.success("测试指令已发送，请检查手机 Telegram！")
import streamlit as st
import requests

# 这一段专门用来诊断为什么“没反应”
st.title("🛡️ 系统诊断模式")

api_key = st.text_input("填入你的 API Key 并回车", type="password")

if api_key:
    test_url = f"https://api.the-odds-api.com/v4/sports/?apiKey={api_key}"
    res = requests.get(test_url)
    if res.status_code == 200:
        st.success("✅ API 连接完全正常！正在加载赛事...")
        st.json(res.json()[:3]) # 显示前三条赛事证明通了
    else:
        st.error(f"❌ API 报错了！错误代码: {res.status_code}")
        st.write(res.text)
