import streamlit as st
from streamlit_mic_recorder import mic_recorder
import firebase_admin
from firebase_admin import db, credentials
import time

# --- ၁။ FIREBASE SETTINGS ---
if not firebase_admin._apps:
    try:
        # သင့် JSON သော့ဖိုင်နာမည်ကို ဒီနေရာမှာ အမှန်ထည့်ပါ
        cred = credentials.Certificate("my-key-123.json") 
        firebase_admin.initialize_app(cred, {
            # သင့် Firebase Database URL ကို ဒီနေရာမှာ အမှန်ထည့်ပါ
            'databaseURL': 'https://talk-3f6ec-default-rtdb.firebaseio.com/' 
        })
    except Exception as e:
        st.error(f"Firebase ချိတ်ဆက်မှု မှားယွင်းနေပါသည်: {e}")

# --- ၂။ APP INTERFACE ---
st.set_page_config(page_title="Business Walkie-Talkie", layout="centered")
st.title("📻 Internal Walkie-Talkie")

# Sidebar တွင် နာမည်သတ်မှတ်ခြင်း
user_name = st.sidebar.text_input("သင့်အမည် (Staff Name)", value="Staff-1")
st.sidebar.write("Status: Online 🟢")

# --- ၃။ စကားပြောရန် (MIC) ---
st.write(f"မင်္ဂလာပါ **{user_name}**၊ စကားပြောရန် အောက်ကခလုတ်ကို နှိပ်ပါ။")
audio_data = mic_recorder(
    start_prompt="🎤 ပြောမည် (Start)",
    stop_prompt="🛑 ရပ်မည် (Stop)",
    key='recorder'
)

if audio_data:
    # အသံဖိုင်ကို Database သို့ ပို့ခြင်း
    ref = db.reference('/chat_messages')
    ref.push({
        'name': user_name,
        'data': audio_data['bytes'].hex(),
        'type': 'audio',
        'timestamp': time.time()
    })
    st.success("အသံပို့ပြီးပါပြီ!")
    time.sleep(1)
    st.rerun()

# --- ၄။ စာပို့ရန် (CHAT) ---
chat_msg = st.chat_input("စာရေးပို့ရန်...")
if chat_msg:
    db.reference('/chat_messages').push({
        'name': user_name,
        'data': chat_msg,
        'type': 'text',
        'timestamp': time.time()
    })
    st.rerun()

# --- ၅။ စကားပြောထားသည်များကို ပြသခြင်း ---
st.divider()
messages = db.reference('/chat_messages').order_by_child('timestamp').limit_to_last(10).get()

if messages:
    for key in reversed(messages):
        msg = messages[key]
        with st.chat_message(msg['name']):
            if msg['type'] == 'text':
                st.write(f"**{msg['name']}:** {msg['data']}")
            else:
                st.write(f"**{msg['name']} (Voice):**")
                audio_bytes = bytes.fromhex(msg['data'])
                st.audio(audio_bytes)
