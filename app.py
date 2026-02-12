import streamlit as st
import firebase_admin
from firebase_admin import db, credentials
import time

# ၁။ Firebase ချိတ်ဆက်မှု (URL ကို အသစ်နဲ့ လဲပေးပါ)
if not firebase_admin._apps:
    cred = credentials.Certificate("my-key-123.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'ဒီနေရာမှာ_သင့်ရဲ့_URL_အသစ်ကိုထည့်ပါ'
    })

st.title("📟 Walkie-Talkie Test")

# ၂။ စာရိုက်ပြီး ပို့တဲ့အပိုင်း
chat_msg = st.chat_input("စမ်းသပ်စာ ရိုက်ပို့ကြည့်ပါ...")
if chat_msg:
    ref = db.reference('/test_chat')
    ref.push({
        'name': "Admin",
        'msg': chat_msg,
        'time': time.time()
    })
    st.success("စာပို့ပြီးပါပြီ!")
    st.rerun()

# ၃။ ဒေတာ ပြန်ထုတ်ပြတဲ့အပိုင်း
st.subheader("စာရင်း")
try:
    data = db.reference('/test_chat').get()
    if data:
        for key in data:
            st.write(f"💬 {data[key]['msg']}")
    else:
        st.write("ဒေတာ မရှိသေးပါ။")
except Exception as e:
    st.error(f"Error: {e}")
