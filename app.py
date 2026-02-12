import streamlit as st
from streamlit_mic_recorder import mic_recorder
import firebase_admin
from firebase_admin import db, credentials
import time

# --- ၁။ FIREBASE SETTINGS ---
if not firebase_admin._apps:
    try:
        # သင်ပေးထားသော JSON ဖိုင်နာမည်ကို အစားထိုးထားသည်
        cred = credentials.Certificate("my-key-123.json") 
        
        firebase_admin.initialize_app(cred, {
            # သင်ပေးထားသော Database URL ကို အစားထိုးထားသည်
            'databaseURL': 'https://talk-3f6ec-default-rtdb.firebaseio.com' 
        })
    except Exception as e:
        st.error(f"Firebase ချိတ်ဆက်မှု မှားယွင်းနေပါသည်: {e}")

# --- ၂။ APP DESIGN ---
st.set_page_config(page_title="Internal Walkie-Talkie", layout="centered")
st.title("📻 Walkie-Talkie App")

# အသုံးပြုသူ နာမည်သတ်မှတ်ရန်
user_name = st.sidebar.text_input("သင့်အမည်", value="Staff-1")
st.sidebar.markdown("---")
st.sidebar.info("အင်တာနက်ရှိလျှင် နေရာမရွေး အသုံးပြုနိုင်ပါသည်။")

# --- ၃။ WALKIE TALKIE BUTTON ---
st.subheader("စကားပြောရန် ခလုတ်ကို နှိပ်ပါ")
audio_data = mic_recorder(
    start_prompt="🎤 စကားပြောမည်",
    stop_prompt="🛑 ရပ်မည်",
    key='recorder'
)

# အသံဖမ်းပြီးလျှင် Database သို့ ပို့ခြင်း
if audio_data:
    try:
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
    except Exception as e:
        st.error(f"ပို့ဆောင်မှု မအောင်မြင်ပါ: {e}")

# --- ၄။ CHAT INPUT ---
chat_msg = st.chat_input("စာရေးပို့ရန်...")
if chat_msg:
    db.reference('/chat_messages').push({
        'name': user_name,
        'data': chat_msg,
        'type': 'text',
        'timestamp': time.time()
    })
    st.rerun()

# --- ၅။ DISPLAY MESSAGES ---
st.divider()
st.subheader("လတ်တလော ပြောဆိုချက်များ")

try:
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
    else:
        st.write("ပြောဆိုထားသည်များ မရှိသေးပါ။")
except Exception as e:
    st.info("Database ချိတ်ဆက်မှုကို စောင့်ဆိုင်းနေပါသည်။ Rules ကို True ပေးထားရန် လိုအပ်ပါသည်။")
