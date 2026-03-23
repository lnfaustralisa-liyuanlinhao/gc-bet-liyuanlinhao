import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="GC Xpress 精准监控版", layout="wide")

# --- 侧边栏配置 ---
with st.sidebar:
    st.header("⚙️ 澳洲/英国 精准配置")
    api_key = st.text_input("1. The Odds API Key", type="password")
    t_token = st.text_input("2. Telegram Bot Token")
    t_id = st.text_input("3. Telegram Chat ID")
    st.markdown("---")
    # 按照你的要求：1.5 起步
    threshold = st.slider("预警赔率下限", 1.0, 10.0, 1.5)
    # 按照你的要求：5 分钟 (300 秒)
    refresh_rate = st.slider("扫描频率 (秒)", 60, 600, 300)
    st.info("📌 监控范围：\n- 赛马: 澳洲 + 英国\n- 灰狗: 澳洲专用")

st.title("🏇 GC Xpress 精准套利扫描 (AU/UK)")

if api_key and t_token and t_id:
    st.success(f"🚀 引擎已启动：盯准澳洲/英国赛场，每 {refresh_rate} 秒扫描一次...")
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            # 【关键修改】：regions=au,uk 锁定你需要的区域
            url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=au,uk&apiKey={api_key}&oddsFormat=decimal"
            
            try:
                res = requests.get(url)
                if res.status_code == 200:
                    data = res.json()
                    st.write(f"🔍 扫描时间: {datetime.now().strftime('%H:%M:%S')} | 正在过滤...")
                    
                    found_count = 0
                    for event in data:
                        sport_key = event.get('sport_key', '').lower()
                        sport_title = event.get('sport_title', '').lower()
                        
                        # 【核心过滤逻辑】：
                        # 1. 如果是赛马 (horse_racing)，允许澳洲和英国
                        # 2. 如果是灰狗 (greyhounds)，只允许澳洲 (通过 sport_key 或标题判断)
                        is_racing = 'horse_racing' in sport_key or 'harness_racing' in sport_key
                        is_au_greyhound = 'greyhounds' in sport_key and 'au' in sport_key
                        
                        if is_racing or is_au_greyhound:
                            venue = event.get('home_team', '未知赛场') 
                            
                            for bookmaker in event.get('bookmakers', []):
                                # 锁定主流平台
                                if bookmaker['key'] in ['tab', 'sportsbet', 'betfair', 'williamhill_au', 'ladbrokes_au']:
                                    for market in bookmaker.get('markets', []):
                                        for outcome in market.get('outcomes', []):
                                            name = outcome['name']
                                            price = outcome['price']
                                            
                                            if price >= threshold:
                                                found_count += 1
                                                # Telegram 信息发送
                                                t_msg = (f"🎯 【精准机会】\n"
                                                         f"📍 地点: {venue}\n"
                                                         f"🐎 名字: {name}\n"
                                                         f"💰 赔率: {price}\n"
                                                         f"🏢 公司: {bookmaker['title']}\n"
                                                         f"----------------\n"
                                                         f"📌 搜法: TAB -> Racing -> 搜 [{venue}]")
                                                
                                                requests.get(f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={t_id}&text={t_msg}")
                    
                    if found_count == 0:
                        st.info("监控中：当前暂无符合条件的 AU/UK 比赛。")
                else:
                    st.error(f"API 限制或异常，请检查 Key。代码返回: {res.status_code}")
            except Exception as e:
                st.write(f"等待数据同步中...")
            
            # 循环冷却 300 秒
            time.sleep(refresh_rate)
            st.rerun()
else:
    st.warning("👋 Mark，请在左侧填入配置信息并回车。")
