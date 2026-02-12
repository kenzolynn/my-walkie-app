import streamlit as st
from streamlit_mic_recorder import mic_recorder
import firebase_admin
from firebase_admin import db, credentials
import time

# --- ၁။ FIREBASE SETTINGS ---
# ချိတ်ဆက်မှု အသစ်ပြန်စရန်
if not firebase_admin._apps:
    try:
        # သင့် GitHub ထဲက JSON ဖိုင်နာမည်နဲ့ တူပါစေ
        cred = credentials.Certificate("my-key-123.json") 
        firebase_admin.initialize_app(cred, {
            # သင့်ရဲ့ Database URL အသစ်ကို ဒီမှာ ထည့်ပါ (အဆုံးမှာ / မပါစေနဲ့)
            'databaseURL': 'https://talk-3f6ec-default-rtdb.firebaseio.com' 
        })
    except Exception as e:
        st.error(f"Firebase ချိတ်ဆက်မှု Error: {e}")

# --- ၂။ APP DESIGN ---
st.set_page_config(page_title="Walkie-Talkie App", layout="centered")
st.title("📻 Walkie-Talkie Pro")

# Sidebar မှာ အမည်ပြောင်းရန်
user_name = st.sidebar.text_input("သင့်အမည်", value="User-1")
st.sidebar.markdown("---")
st.sidebar.write("App ကို အသုံးပြုနိုင်ပါပြီ!")

# --- ၃။ WALKIE TALKIE (အသံပို့ရန်) ---
st.subheader("🎤 စကားပြောရန်")
audio_data = mic_recorder(
    start_prompt="နှိပ်ပြီး စကားပြောပါ",
    stop_prompt="ရပ်မည် (ပို့မည်)",
    key='recorder'
)

if audio_data:
    try:
        ref = db.reference('/walkie_talkie_chat')
        ref.push({
            'name': user_name,
            'data': audio_data['bytes'].hex(),
            'type': 'audio',
            'timestamp': time.time()
        })
        st.success("အသံပို့ပြီးပါပြီ!")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"အသံပို့၍မရပါ: {e}")

# --- ၄။ CHAT INPUT (စာပို့ရန်) ---
st.divider()
chat_msg = st.chat_input("ဒီမှာ စာရေးပို့နိုင်ပါတယ်...")
if chat_msg:
    try:
        ref = db.reference('/walkie_talkie_chat')
        ref.push({
            'name': user_name,
            'data': chat_msg,
            'type': 'text',
            'timestamp': time.time()
        })
        st.rerun()
    except Exception as e:
        st.error(f"စာပို့၍မရပါ: {e}")

# --- ၅။ DISPLAY MESSAGES (ပြန်လည်ပြသခြင်း) ---
st.subheader("💬 လတ်တလော ပြောဆိုချက်များ")

try:
    # နောက်ဆုံး ပြောဆိုချက် ၁၀ ခုကို ယူပါမယ်
    messages = db.reference('/walkie_talkie_chat').order_by_child('timestamp').limit_to_last(10).get()

    if messages:
        # အသစ်ဆုံးကို အပေါ်မှာ ပြရန် reversed သုံးထားပါတယ်
        for key in reversed(messages):
            msg = messages[key]
            with st.chat_message(msg['name']):
                if msg.get('type') == 'text':
                    st.write(f"**{msg['name']}:** {msg['data']}")
                elif msg.get('type') == 'audio':
                    st.write(f"**{msg['name']} (Voice):**")
                    audio_bytes = bytes.fromhex(msg['data'])
                    st.audio(audio_bytes)
    else:
        st.info("ပြောဆိုထားသည်များ မရှိသေးပါ။ စတင် စကားပြောနိုင်ပါပြီ!")
except Exception as e:
    st.error(f"ဒေတာဖတ်ရာတွင် အခက်အခဲရှိနေသည်: {e}")
