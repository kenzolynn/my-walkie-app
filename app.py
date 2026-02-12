import streamlit as st
import firebase_admin
from firebase_admin import db, credentials
import time

# --- ၁။ FIREBASE SETTINGS ---
if not firebase_admin._apps:
    cred = credentials.Certificate("my-key-123.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://talk-3f6ec-default-rtdb.firebaseio.com'
    })

st.set_page_config(page_title="1s Real-time Talk", layout="centered")
st.title("📟 Fast Real-time Talk")

# --- ၂။ USER INTERFACE ---
user_name = st.sidebar.text_input("သင့်အမည်", value="User")
st.sidebar.info("ဤ App သည် ၁ စက္ကန့်တစ်ခါ ဒေတာကို အလိုအလျောက် Update လုပ်ပေးနေပါသည်။")

# စာရိုက်ရန်
chat_msg = st.chat_input("တစ်ခုခု ပြောလိုက်ပါ...")
if chat_msg:
    ref = db.reference('/instant_talk')
    ref.push({
        'name': user_name,
        'msg': chat_msg,
        'timestamp': time.time()
    })

# --- ၃။ DISPLAY MESSAGES ---
st.subheader("ဝေမျှချက်များ")

try:
    # နောက်ဆုံး စာ ၁၀ စောင်ကို ယူပါမယ်
    messages = db.reference('/instant_talk').order_by_child('timestamp').limit_to_last(10).get()

    if messages:
        for key in reversed(messages):
            msg_data = messages[key]
            with st.chat_message(msg_data['name']):
                st.write(f"**{msg_data['name']}:** {msg_data['msg']}")
    else:
        st.write("စကားပြောထားသည်များ မရှိသေးပါ။")

except Exception as e:
    st.error(f"Error: {e}")

# --- ၄။ ၁ စက္ကန့်တစ်ခါ AUTO REFRESH ---
# time.sleep(1) က ၁ စက္ကန့် စောင့်ခိုင်းတာပါ
time.sleep(1)
st.rerun()
