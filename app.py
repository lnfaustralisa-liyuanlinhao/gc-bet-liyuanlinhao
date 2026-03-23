import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="GC Xpress 终极监控", layout="wide")

# 侧边栏
API_KEY = st.sidebar.text_input("The Odds API Key", type="password")
TELEGRAM_TOKEN = st.sidebar.text_input("Telegram Bot Token")
CHAT_ID = st.sidebar.text_input("Telegram Chat ID")

st.title("🏇 GC Xpress 澳洲全能扫描仪")

if API_KEY:
    # 强制扫描所有运动，看看哪个有数据
    st.info("正在全量扫描澳洲所有活跃赛场...")
    # 我们试一个最稳的路径：澳洲足球、板球、赛马全包含的通用路径
    url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=au&apiKey={API_KEY}&oddsFormat=decimal"
    
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            if data:
                st.success(f"✅ 成功！抓取到 {len(data)} 场即将开赛的数据")
                df = pd.DataFrame([{"时间": e['commence_time'], "项目": e['sport_title'], "对阵": f"{e['home_team']} vs {e['away_team']}"} for e in data])
                st.table(df)
                
                # 只要抓到数据，就强制发一条 Telegram 证明程序活了
                if TELEGRAM_TOKEN and CHAT_ID:
                    t_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text=GC_Xpress:成功发现{len(data)}场数据！"
                    requests.get(t_url)
            else:
                st.warning("API 响应成功，但目前确实没有任何即将开赛的项目。可能是深夜空档期。")
        else:
            st.error(f"API 报错，代码: {res.status_code}")
    except Exception as e:
        st.error(f"连接失败: {e}")

# 这是一个独立的按钮，专门用来救急测试
if st.button("🆘 点击这里：强制发测试信息到手机"):
    if TELEGRAM_TOKEN and CHAT_ID:
        r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text=手动测试响应成功")
        st.write(f"服务器返回：{r.text}")
