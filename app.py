import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="GC Xpress - 赔率监控", layout="wide")

# --- 侧边栏配置 ---
st.sidebar.header("🛠️ 配置中心")
API_KEY = st.sidebar.text_input("The Odds API Key", type="password")
TELEGRAM_TOKEN = st.sidebar.text_input("Telegram Bot Token")
CHAT_ID = st.sidebar.text_input("Telegram Chat ID")
threshold = st.sidebar.slider("预警门槛 (Edge %)", 0.0, 15.0, 3.0)

st.title("🏇 GC Xpress 实时赔率套利监控")

if API_KEY and TELEGRAM_TOKEN and CHAT_ID:
    # 扫描澳洲赛马和灰狗 (Regions=au)
    url = f"https://api.the-odds-api.com/v4/sports/horse_racing_au/odds/?regions=au&apiKey={API_KEY}&oddsFormat=decimal"
    
    try:
        res = requests.get(url)
        if res.status_code == 200:
            events = res.json()
            st.success(f"✅ 正在实时扫描 {len(events)} 场澳洲赛事...")
            
            results = []
            for event in events:
                # 获取不同博彩公司的赔率
                for bookmaker in event.get('bookmakers', []):
                    # 我们重点对比 TAB, Sportsbet 和 Betfair
                    title = bookmaker['title']
                    markets = bookmaker.get('markets', [])
                    if markets:
                        for runner in markets[0].get('outcomes', []):
                            results.append({
                                "比赛名称": event['sport_title'],
                                "参赛选手": runner['name'],
                                "博彩公司": title,
                                "当前赔率": runner['price']
                            })
            
            if results:
                df = pd.DataFrame(results)
                # 只显示赔率最高的几项，方便你对比
                st.dataframe(df.sort_values(by="当前赔率", ascending=False), use_container_width=True)
            else:
                st.info("目前场次暂无赔率数据，请稍等刷新。")
        else:
            st.error(f"API 获取失败，请检查 Key 是否过期。")
    except Exception as e:
        st.error(f"运行出错: {e}")
else:
    st.warning("请在左侧填入所有 Key 以激活自动扫描。")

if st.sidebar.button("测试 Telegram 通知"):
    test_msg = "GC_Xpress_测试: 你的分析仪已经正式上线了！"
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={test_msg}")
    st.sidebar.success("已发送测试！请检查手机。")
