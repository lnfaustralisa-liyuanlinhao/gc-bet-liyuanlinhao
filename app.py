import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="GC Xpress $200 盈利计划", layout="wide")

# --- 侧边栏 ---
with st.sidebar:
    st.header("🎯 盈利目标：$200/日")
    api_key = st.text_input("1. API Key", type="password")
    t_token = st.text_input("2. Telegram Token")
    t_id = st.text_input("3. Telegram Chat ID")
    st.markdown("---")
    st.warning("💡 建议在下午 2点-9点 开启，其余时间关机省积分。")

st.title("🐕 澳洲灰狗高胜率决策引擎")

if api_key and t_token and t_id:
    info_box = st.empty()
    table_box = st.empty()
    
    # 强制请求所有澳洲赔率，防止标签漏抓
    url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=au&apiKey={api_key}&oddsFormat=decimal"
    
    try:
        res = requests.get(url)
        remaining = res.headers.get('x-requests-remaining', 'N/A')
        info_box.info(f"📡 引擎监控中... | API 剩余积分: {remaining} | 最后扫描: {datetime.now().strftime('%H:%M:%S')}")

        if res.status_code == 200:
            events = res.json()
            recommendations = []

            for event in events:
                sport_title = event.get('sport_title', '').lower()
                # 只要是澳洲的灰狗
                if 'greyhound' in sport_title:
                    venue = event.get('home_team', '未知赛场')
                    
                    for bookie in event.get('bookmakers', []):
                        if bookie['key'] == 'tab': # 锁定澳洲 TAB 数据
                            for market in bookie.get('markets', []):
                                runners = market.get('outcomes', [])
                                if len(runners) >= 5: # 确保是有竞争力的完整场次
                                    sorted_r = sorted(runners, key=lambda x: x['price'])
                                    fav = sorted_r[0] # 头号热门
                                    sec = sorted_r[1] # 二号热门
                                    
                                    # --- 最高胜率分析逻辑 ---
                                    # 策略：头号热门赔率在 1.5 - 2.8 之间，且领先第二名至少 0.5 以上
                                    if 1.5 <= fav['price'] <= 2.8 and (sec['price'] - fav['price'] > 0.5):
                                        recommendations.append({
                                            "赛场": venue,
                                            "最强狗": fav['name'],
                                            "赔率": fav['price'],
                                            "信心度": "🔥 高 (热门领先)"
                                        })
                                        
                                        # 发送一键指令
                                        t_msg = (f"💰 【$200 盈利机会】\n"
                                                 f"📍 赛场: {venue}\n"
                                                 f"🐕 目标: {fav['name']}\n"
                                                 f"💵 赔率: {fav['price']}\n"
                                                 f"📊 策略: 强力单选 (Win)\n"
                                                 f"🔢 组合建议: Quinella ({fav['name']} & {sec['name']})\n"
                                                 f"----------------\n"
                                                 f"📌 动作: 立即打开 TAB 确认地点后下单")
                                        requests.get(f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={t_id}&text={t_msg}")

            if recommendations:
                table_box.table(pd.DataFrame(recommendations))
            else:
                table_box.warning("🕒 当前暂未发现‘高胜率’信号场次。系统只会在机会极佳时推送，请耐心等待。")
        elif res.status_code == 401:
            st.error("🔑 API Key 错误，请检查。")
        elif res.status_code == 429:
            st.error("🚨 积分已耗尽！请等到下个月或更换新 Key。")
            
    except Exception as e:
        st.write("系统唤醒中...")

    # 3分钟扫描一次，平衡实时性与积分消耗
    time.sleep(180)
    st.rerun()
else:
    st.warning("👋 Mark，请填入配置信息以启动盈利引擎。")
