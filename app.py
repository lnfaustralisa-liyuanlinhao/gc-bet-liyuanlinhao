import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="GC Xpress 灰狗实战版", layout="wide")

with st.sidebar:
    st.header("🐕 灰狗专用配置")
    api_key = st.text_input("1. API Key", type="password")
    t_token = st.text_input("2. Telegram Token")
    t_id = st.text_input("3. Telegram Chat ID")
    st.markdown("---")
    st.info("🕒 监控：仅限澳洲灰狗\n🚀 触发：开赛前 15 分钟")

st.title("🎯 澳洲灰狗临场精准分析")

if api_key and t_token and t_id:
    status_msg = st.empty()
    table_placeholder = st.empty()
    
    while True:
        # 获取数据
        url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=au&apiKey={api_key}&oddsFormat=decimal"
        
        try:
            res = requests.get(url)
            if res.status_code == 200:
                events = res.json()
                # 统一使用 UTC 时间进行计算，防止时差错误
                now_utc = datetime.utcnow()
                
                upcoming_greyhounds = []
                
                for event in events:
                    sport_title = event.get('sport_title', '').lower()
                    # 只要包含 greyhound 就抓取
                    if 'greyhound' in sport_title:
                        commence_time = datetime.strptime(event['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
                        # 计算剩余分钟数
                        time_diff = (commence_time - now_utc).total_seconds() / 60
                        
                        # 只要是未来 20 分钟内的比赛都显示在网页上供参考
                        if -2 < time_diff < 20:
                            venue = event.get('home_team', '未知赛场')
                            upcoming_greyhounds.append({"赛场": venue, "剩余分钟": round(time_diff, 1)})
                            
                            # 【触发推送】：开赛前 2 到 15 分钟
                            if 2 <= time_diff <= 15:
                                runners = []
                                for bookie in event.get('bookmakers', []):
                                    if bookie['key'] in ['tab', 'sportsbet']:
                                        for market in bookie.get('markets', []):
                                            for outcome in market.get('outcomes', []):
                                                runners.append({"name": outcome['name'], "price": outcome['price']})
                                
                                if len(runners) >= 3:
                                    # 模拟胜率分析逻辑
                                    sorted_r = sorted(runners, key=lambda x: x['price'])
                                    d1, d2, d3 = sorted_r[0], sorted_r[1], sorted_r[2]
                                    
                                    t_msg = (f"🐕 【灰狗临场推介】\n"
                                             f"📍 赛场: {venue}\n"
                                             f"⏰ 还有 {round(time_diff)} 分钟开赛\n"
                                             f"----------------\n"
                                             f"🥇 WIN: {d1['name']} (@{d1['price']})\n"
                                             f"🥈 PLACE: {d1['name']}, {d2['name']}\n"
                                             f"🔢 QUINELLA: {d1['name']} & {d2['name']}\n"
                                             f"🎲 TRIFECTA (Box): {d1['name']}, {d2['name']}, {d3['name']}\n"
                                             f"----------------\n"
                                             f"📌 提示: 请在 TAB 确认箱号后下单")
                                    
                                    requests.get(f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={t_id}&text={t_msg}")
                                    st.toast(f"已推送: {venue}")
                                    time.sleep(5) # 简单防重发

                # 在网页上实时显示排队中的场次
                if upcoming_greyhounds:
                    status_msg.success(f"📡 正在监控中... 发现 {len(upcoming_greyhounds)} 场即将开始的灰狗赛")
                    table_placeholder.table(pd.DataFrame(upcoming_greyhounds))
                else:
                    status_msg.warning("🕒 当前 20 分钟内暂无澳洲灰狗赛事，请稍候。")
                    
            else:
                st.error(f"API 报错: {res.status_code}")
        except Exception as e:
            st.error(f"系统同步中... {e}")

        time.sleep(60)
        st.rerun()
