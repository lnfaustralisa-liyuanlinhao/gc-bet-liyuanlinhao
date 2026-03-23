import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="GC Xpress 极简指令版", layout="centered")

# --- 侧边栏：只需填一次 ---
with st.sidebar:
    st.header("🔑 系统钥匙")
    api_key = st.text_input("1. API Key", type="password")
    t_token = st.text_input("2. Telegram Token")
    t_id = st.text_input("3. Telegram Chat ID")
    st.markdown("---")
    st.info("💡 当前设定：\n- 监控：AU/UK 赛马 & AU 灰狗\n- 频率：5分钟/次\n- 策略：每轮仅推送概率最大的一场")

st.title("🎯 GC Xpress 极简指令引擎")

if api_key and t_token and t_id:
    status_box = st.empty()
    result_display = st.empty()
    
    while True:
        url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=au,uk&apiKey={api_key}&oddsFormat=decimal"
        
        try:
            res = requests.get(url)
            remaining = res.headers.get('x-requests-remaining', 'N/A')
            status_box.write(f"✅ 正在扫描全球数据... (API 余额: {remaining})")

            if res.status_code == 200:
                events = res.json()
                all_candidates = []

                for event in events:
                    sport_key = event.get('sport_key', '').lower()
                    # 过滤项目：澳洲/英国赛马，澳洲灰狗
                    if any(k in sport_key for k in ['horse_racing', 'harness_racing']) or ('greyhounds' in sport_key and 'au' in sport_key):
                        venue = event.get('home_team', '未知赛场')
                        
                        for bookie in event.get('bookmakers', []):
                            if bookie['key'] in ['tab', 'sportsbet']: # 优先看你常用的公司
                                for market in bookie.get('markets', []):
                                    for outcome in market.get('outcomes', []):
                                        # 核心逻辑：找出每一场里赔率最低（概率最大）的那个
                                        all_candidates.append({
                                            "venue": venue,
                                            "name": outcome['name'],
                                            "price": outcome['price'],
                                            "bookie": bookie['title']
                                        })

                if all_candidates:
                    # 从所有选手中，选出赔率最稳（最低）且在1.5以上的那一个
                    # 按照赔率从小到大排序，取第一个
                    filtered_candidates = [c for c in all_candidates if c['price'] >= 1.5]
                    if filtered_candidates:
                        best_bet = min(filtered_candidates, key=lambda x: x['price'])

                        # 1. 网页显示
                        result_display.success(f"### 📍 下一场推荐：{best_bet['venue']}\n"
                                               f"**选手：** {best_bet['name']}  \n"
                                               f"**赔率：** {best_bet['price']}  \n"
                                               f"**平台：** {best_bet['bookie']}")

                        # 2. 推送最简单的指令
                        t_msg = (f"📢 【极简指令】\n"
                                 f"📍 赛场: {best_bet['venue']}\n"
                                 f"🐎 名字: {best_bet['name']}\n"
                                 f"💰 赔率: {best_bet['price']}\n"
                                 f"🏢 平台: {best_bet['bookie']}\n"
                                 f"⏰ 动作: 赔率合适请立即查看")
                        requests.get(f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={t_id}&text={t_msg}")
                    else:
                        result_display.info("当前暂无符合 1.5 以上稳健赔率的比赛。")
            else:
                st.error("连接失败，请检查 API Key 是否正确。")
        except Exception as e:
            st.error(f"引擎同步中... {e}")

        time.sleep(300) # 强制5分钟刷新一次
        st.rerun()
else:
    st.warning("👋 Mark，请在左侧填入必要信息开启引擎。")
