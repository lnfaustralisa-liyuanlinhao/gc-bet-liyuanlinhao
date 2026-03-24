import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="GC Xpress 灰狗强力版", layout="wide")

with st.sidebar:
    st.header("🐕 澳洲灰狗-强力监控")
    api_key = st.text_input("1. API Key", type="password")
    t_token = st.text_input("2. Telegram Token")
    t_id = st.text_input("3. Telegram Chat ID")
    st.markdown("---")
    st.write("📌 当前逻辑：全类目强制筛选灰狗")

st.title("🎯 澳洲灰狗-全量扫描中")

if api_key and t_token and t_id:
    placeholder = st.empty()
    
    # 强制获取所有运动，看看灰狗到底藏在哪
    url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=au&apiKey={api_key}&oddsFormat=decimal"
    
    try:
        res = requests.get(url)
        # 实时显示积分
        remaining = res.headers.get('x-requests-remaining', 'N/A')
        st.info(f"📊 实时 API 剩余积分: {remaining}")

        if res.status_code == 200:
            data = res.json()
            found_list = []
            
            for event in data:
                # 模糊匹配：只要名字里有 greyhound 就抓
                s_title = event.get('sport_title', '')
                s_key = event.get('sport_key', '')
                
                if 'greyhound' in s_title.lower() or 'greyhound' in s_key.lower():
                    venue = event.get('home_team', '未知赛场')
                    commence = event.get('commence_time', '')
                    found_list.append({"赛场": venue, "时间": commence})
                    
                    # 只要发现场次，立即推送最稳的赔率
                    for bookie in event.get('bookmakers', []):
                        if bookie['key'] in ['tab', 'sportsbet']:
                            for market in bookie.get('markets', []):
                                runners = market.get('outcomes', [])
                                if runners:
                                    # 自动生成 Win/Place/Quinella 指令
                                    sorted_r = sorted(runners, key=lambda x: x['price'])
                                    d1 = sorted_r[0]
                                    d2 = sorted_r[1] if len(sorted_r) > 1 else d1
                                    
                                    t_msg = (f"🐕 【灰狗指令】\n📍 赛场: {venue}\n🥇 WIN: {d1['name']} (@{d1['price']})\n🔢 QUINELLA: {d1['name']} & {d2['name']}")
                                    requests.get(f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={t_id}&text={t_msg}")

            if found_list:
                st.table(pd.DataFrame(found_list))
            else:
                st.warning("⚠️ 此时此刻 API 确实没发回灰狗数据。可能是当前没有临近 15 分钟开赛的场次，或者积分已耗尽。")
        else:
            st.error(f"API 报错: {res.status_code}。可能是积分用完了。")

    except Exception as e:
        st.write("连接中...")
    
    time.sleep(120) # 调回 120 秒，省着点花积分
    st.rerun()
