import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="GC Xpress 全能监控", layout="wide")

st.sidebar.header("🛠️ 配置中心")
API_KEY = st.sidebar.text_input("The Odds API Key", type="password")
TELEGRAM_TOKEN = st.sidebar.text_input("Telegram Bot Token")
CHAT_ID = st.sidebar.text_input("Telegram Chat ID")

st.title("🏇 GC Xpress 澳洲全赛场监控")

if API_KEY:
    try:
        # 第一步：动态获取当前所有可用的澳洲运动分类
        all_sports_url = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}"
        all_sports = requests.get(all_sports_url).json()
        
        # 筛选出包含 'au' 的赛马或灰狗分类
        au_sports = [s['key'] for s in all_sports if 'au' in s['key'] and ('racing' in s['key'] or 'greyhounds' in s['key'])]
        
        if not au_sports:
            st.warning("⚠️ 当前 API 未返回任何活跃的澳洲赛马或灰狗场次，可能是空档期。")
        else:
            # 第二步：只抓取第一个“活着的”分类数据
            target_sport = au_sports[0]
            st.success(f"✅ 发现活跃赛场: {target_sport}")
            
            odds_url = f"https://api.the-odds-api.com/v4/sports/{target_sport}/odds/?regions=au&apiKey={API_KEY}&oddsFormat=decimal"
            odds_res = requests.get(odds_url).json()
            
            if odds_res:
                df_list = []
                for event in odds_res:
                    df_list.append({
                        "项目": target_sport,
                        "比赛": event['sport_title'],
                        "选手": event['home_team'],
                        "时间": event['commence_time']
                    })
                st.table(pd.DataFrame(df_list))
            else:
                st.info(f"分类 {target_sport} 存在，但暂无实时赔率。")
                
    except Exception as e:
        st.error(f"发生错误: {e}")
else:
    st.info("请在左侧填入 API Key。")

if st.sidebar.button("测试 Telegram"):
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text=GC_Xpress_测试成功")
