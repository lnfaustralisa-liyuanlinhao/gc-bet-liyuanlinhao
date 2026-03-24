import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import random

st.set_page_config(page_title="GC Xpress 灰狗全能版", layout="wide")

with st.sidebar:
    st.header("🐕 灰狗实战配置")
    api_key = st.text_input("1. API Key", type="password")
    t_token = st.text_input("2. Telegram Token")
    t_id = st.text_input("3. Telegram Chat ID")
    st.markdown("---")
    st.info("🕒 监控策略：全时段扫描澳洲灰狗")

st.title("🎯 澳洲灰狗全量实时分析")

if api_key and t_token and t_id:
    status_msg = st.empty()
    table_placeholder = st.empty()
    
    while True:
        # 【关键修改】：增加 random 参数防止 API 返回旧的缓存数据
        url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=au&apiKey={api_key}&oddsFormat=decimal&_unused={random.random()}"
        
        try:
            res = requests.get(url)
            if res.status_code == 200:
                events = res.json()
                now_utc = datetime.utcnow()
                all_greyhounds = []
                
                for event in events:
                    sport_title = event.get('sport_title', '').lower()
                    # 放宽过滤条件：只要是澳洲的灰狗
                    if 'greyhound' in sport_title:
                        commence_time = datetime.strptime(event['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
                        time_diff = (commence_time - now_utc).total_seconds() / 60
                        venue = event.get('home_team', '未知赛场')
                        
                        # 把所有能抓到的灰狗赛都放进列表，不管离比赛还有多久
                        all_greyhounds.append({
                            "赛场": venue,
                            "状态": "即将开赛" if time_diff > 0 else "正在进行/已结束",
                            "预计开赛(分)": round(time_diff, 1)
                        })
                        
                        # 【推送逻辑】：只要是 15 分钟内即将开始的，立即推送分析
                        if 0 < time_diff <= 15:
                            runners = []
                            for bookie in event.get('bookmakers', []):
                                if bookie['key'] in ['tab', 'sportsbet']:
                                    for market in bookie.get('markets', []):
                                        for outcome in market.get('outcomes', []):
                                            runners.append({"name": outcome['name'], "price": outcome['price']})
                            
                            if runners:
                                sorted_r = sorted(runners, key=lambda x: x['price'])
                                d1 = sorted_r[0]
                                d2 = sorted_r[1] if len(sorted_r) > 1 else d1
                                d3 = sorted_r[2] if len(sorted_r) > 2 else d2
                                
                                t_msg = (f"🐕 【灰狗临场推介】\n"
                                         f"📍 赛场: {venue}\n"
                                         f"⏰ 离赛前: {round(time_diff)} 分钟\n"
                                         f"🥇 WIN: {d1['name']} (@{d1['price']})\n"
                                         f"🥈 PLACE: {d1['name']}, {d2['name']}\n"
                                         f"🔢 QUINELLA: {d1['name']} & {d2['name']}\n"
                                         f"🎲 TRIFECTA (Box): {d1['name']}, {d2['name']}, {d3['name']}")
                                
                                requests.get(f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={t_id}&text={t_msg}")
                
                if all_greyhounds:
                    status_msg.success(f"📡 成功抓取到 {len(all_greyhounds)} 场澳洲灰狗赛事数据")
                    table_placeholder.table(pd.DataFrame(all_greyhounds))
                else:
                    status_msg.warning("⚠️ API 此时未返回任何灰狗数据。请检查 TAB 是否有即将开始（未开赛）的场次。")
                    
            else:
                st.error(f"API 请求失败: {res.status_code}")
        except Exception as e:
            st.write("数据同步中...")

        time.sleep(60) # 保持 1 分钟刷新一次
        st.rerun()
