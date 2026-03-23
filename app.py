import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="GC Xpress Racing 专用版", layout="wide")

# --- 侧边栏配置 ---
with st.sidebar:
    st.header("⚙️ Racing 专用配置")
    api_key = st.text_input("1. The Odds API Key", type="password")
    t_token = st.text_input("2. Telegram Bot Token")
    t_id = st.text_input("3. Telegram Chat ID")
    st.markdown("---")
    threshold = st.slider("预警赔率下限", 2.0, 15.0, 5.0)
    refresh_rate = st.slider("扫描频率 (秒)", 60, 300, 120)

st.title("🏇 GC Xpress 澳洲全赛马/灰狗实时监控")

if api_key and t_token and t_id:
    st.success(f"🚀 监控已启动：只看澳洲 Racing (赛马/灰狗/马车)...")
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            # 这里的路径改为 upcoming，但我们在后面代码里加了硬核过滤
            url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=au&apiKey={api_key}&oddsFormat=decimal"
            
            try:
                res = requests.get(url)
                if res.status_code == 200:
                    data = res.json()
                    st.write(f"🔍 扫描时间: {datetime.now().strftime('%H:%M:%S')} | 正在比对澳洲赛场...")
                    
                    for event in data:
                        sport_key = event.get('sport_key', '').lower()
                        
                        # 【核心过滤】：只准 Racing 类通过
                        if 'racing' in sport_key or 'greyhounds' in sport_key:
                            venue = event.get('home_team', '未知赛场') # 赛场名
                            sport_title = event.get('sport_title', 'Racing')
                            
                            for bookmaker in event.get('bookmakers', []):
                                if bookmaker['key'] in ['tab', 'sportsbet', 'betfair']:
                                    for market in bookmaker.get('markets', []):
                                        for outcome in market.get('outcomes', []):
                                            name = outcome['name']
                                            price = outcome['price']
                                            
                                            if price >= threshold:
                                                # 发送更清爽的指令
                                                t_msg = (f"🏇 【Racing 机会】\n"
                                                         f"📍 地点: {venue}\n"
                                                         f"🐎 名字: {name}\n"
                                                         f"💰 赔率: {price}\n"
                                                         f"🏢 公司: {bookmaker['title']}\n"
                                                         f"🏷️ 类型: {sport_title}\n"
                                                         f"----------------\n"
                                                         f"📌 搜法: TAB -> Racing -> 搜地点 [{venue}]")
                                                
                                                requests.get(f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={t_id}&text={t_msg}")
                    
                    st.info("本轮扫描已完成，手机没响说明暂无符合要求的高赔率马/狗。")
                else:
                    st.error(f"API 报错: {res.status_code}")
            except Exception as e:
                st.write("正在连接服务器...")
            
            time.sleep(refresh_rate)
            st.rerun()
else:
    st.warning("👋 Mark，请在左侧填入配置信息。")
