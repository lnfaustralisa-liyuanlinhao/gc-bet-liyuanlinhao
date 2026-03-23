import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="GC Xpress 赚钱引擎-澳洲版", layout="wide")

# --- 侧边栏配置 ---
with st.sidebar:
    st.header("⚙️ 自动化配置")
    api_key = st.text_input("1. The Odds API Key", type="password")
    t_token = st.text_input("2. Telegram Bot Token")
    t_id = st.text_input("3. Telegram Chat ID")
    st.markdown("---")
    threshold = st.slider("预警赔率下限", 2.0, 20.0, 5.0)
    refresh_rate = st.slider("刷新频率 (秒)", 60, 600, 120)
    st.info("💡 填完记得按回车(Enter)才能生效")

st.title("💰 GC Xpress 澳洲赛场实时套利")

# 核心监控逻辑
if api_key and t_token and t_id:
    st.success(f"🚀 监控引擎已启动，每 {refresh_rate} 秒扫描一次澳洲全赛场...")
    
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            # 抓取澳洲赛场数据（包含赛马、灰狗、马车）
            url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=au&apiKey={api_key}&oddsFormat=decimal"
            
            try:
                res = requests.get(url)
                if res.status_code == 200:
                    data = res.json()
                    now_time = datetime.now().strftime("%H:%M:%S")
                    st.write(f"🔍 最后更新: {now_time} | 扫描到 {len(data)} 场赛事")
                    
                    found_opportunities = []
                    
                    for event in data:
                        # 提取参数：sport_title (项目), home_team (通常是赛场名)
                        sport = event.get('sport_title', '未知项目')
                        venue = event.get('home_team', '未知赛场')
                        
                        for bookmaker in event.get('bookmakers', []):
                            # 锁定澳洲三大平台
                            if bookmaker['key'] in ['tab', 'sportsbet', 'betfair']:
                                for market in bookmaker.get('markets', []):
                                    for outcome in market.get('outcomes', []):
                                        name = outcome['name'] # 马/狗名字
                                        price = outcome['price'] # 赔率
                                        
                                        # 如果达到预警赔率
                                        if price >= threshold:
                                            found_opportunities.append({
                                                "地点": venue,
                                                "选手": name,
                                                "公司": bookmaker['title'],
                                                "赔率": price,
                                                "项目": sport
                                            })
                                            
                                            # 发送 Telegram 详细指令
                                            t_msg = (f"🚩 【赚钱指令】\n"
                                                     f"项目: {sport}\n"
                                                     f"地点: {venue}\n"
                                                     f"名字: {name}\n"
                                                     f"公司: {bookmaker['title']}\n"
                                                     f"赔率: {price}\n"
                                                     f"📌 搜法: 打开 TAB -> Racing -> 搜地点 [{venue}]")
                                            requests.get(f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={t_id}&text={t_msg}")

                    if found_opportunities:
                        st.table(pd.DataFrame(found_opportunities))
                    else:
                        st.info("当前暂无符合赔率要求的机会，持续监控中...")
                
                elif res.status_code == 429:
                    st.error("🚨 API 频率达到上限，请调高刷新频率或更换 Key。")
                else:
                    st.error(f"API 报错: {res.status_code}")
                    
            except Exception as e:
                st.write(f"连接波动，稍后重试... {e}")
            
            # 循环冷却
            time.sleep(refresh_rate)
            st.rerun()
else:
    st.warning("👋 Mark，请在左侧填入 API Key, Token 和 Chat ID 开始赚钱。")
