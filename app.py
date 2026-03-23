import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="GC Xpress 监控", layout="wide")

st.sidebar.header("🛠️ 配置")
API_KEY = st.sidebar.text_input("The Odds API Key", type="password")
TELEGRAM_TOKEN = st.sidebar.text_input("Telegram Bot Token")
CHAT_ID = st.sidebar.text_input("Telegram Chat ID")

st.title("🏇 GC Xpress 实时监控")

if API_KEY:
    # 尝试获取所有可用运动项目，这不消耗积分，专门用来测试 Key 是否有效
    test_url = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}"
    
    try:
        response = requests.get(test_url)
        if response.status_code == 200:
            st.success("✅ Key 验证通过！正在抓取澳洲赛马数据...")
            
            # 如果 Key 没问题，再抓取具体赔率
            odds_url = f"https://api.the-odds-api.com/v4/sports/horse_racing_au/odds/?regions=au&apiKey={API_KEY}&oddsFormat=decimal"
            odds_res = requests.get(odds_url)
            
            if odds_res.status_code == 200:
                data = odds_res.json()
                if data:
                    st.write(f"当前监控到 {len(data)} 场赛事：")
                    st.json(data[:2]) # 先显示两条原始数据看看
                else:
                    st.info("目前澳洲赛场暂时没有活跃的赔率数据（可能是空档期）。")
            else:
                st.error(f"赔率抓取失败！错误代码: {odds_res.status_code}")
                st.write(f"详情: {odds_res.text}")
        else:
            st.error(f"❌ Key 无效或额度耗尽 (错误码: {response.status_code})")
            st.write(f"服务器返回信息: {response.text}")
    except Exception as e:
        st.error(f"网络连接异常: {e}")
else:
    st.warning("请在左侧填入 API Key。")

# 测试按钮
if st.sidebar.button("测试 Telegram"):
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text=测试成功")
