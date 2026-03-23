import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="GC Xpress 赚钱分析仪", layout="wide")

# 强制侧边栏展开
with st.sidebar:
    st.header("🛠️ 核心配置")
    api_key = st.text_input("1. The Odds API Key", type="password")
    t_token = st.text_input("2. Telegram Bot Token")
    t_id = st.text_input("3. Telegram Chat ID")
    st.info("💡 填完每一项请按回车 (Enter)")

st.title("💰 GC Xpress 套利扫描中心")

if api_key:
    # 路径改为最稳妥的“即将开赛”路径
    url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=au&apiKey={api_key}&oddsFormat=decimal"
    
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            if data:
                st.success(f"✅ 成功抓取 {len(data)} 场赛事！数据如下：")
                
                all_odds = []
                for event in data:
                    for bookmaker in event.get('bookmakers', []):
                        for market in bookmaker.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                all_odds.append({
                                    "时间": event['commence_time'],
                                    "赛事": event['sport_title'],
                                    "选手/马名": outcome['name'],
                                    "公司": bookmaker['title'],
                                    "赔率": outcome['price']
                                })
                                # 如果赔率大于 5.0，自动发给 Telegram
                                if t_token and t_id and outcome['price'] >= 5.0:
                                    t_msg = f"🚩 发现机会！\n选手: {outcome['name']}\n赔率: {outcome['price']}\n公司: {bookmaker['title']}"
                                    requests.get(f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={t_id}&text={t_msg}")

                st.dataframe(pd.DataFrame(all_odds), use_container_width=True)
            else:
                st.warning("目前没有即将开赛的澳洲场次，请稍后再试。")
        else:
            st.error(f"API 报错：{res.status_code} - {res.text}")
    except Exception as e:
        st.error(f"发生故障: {e}")
else:
    st.info("👋 你好 Mark！请在左侧填入你的新 API Key 开始扫描。")
