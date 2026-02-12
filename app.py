import streamlit as st
from streamlit_mic_recorder import mic_recorder
import firebase_admin
from firebase_admin import db, credentials
import time

# --- ၁။ FIREBASE SETTINGS ---
if not firebase_admin._apps:
    try:
        # သင့် JSON ဖိုင်နာမည် မှန်ကန်ပါစေ
        cred = credentials.Certificate("my-key-123.json") 
        firebase_admin.initialize_app(cred, {
            # URL အဆုံးမှာ / မပါအောင် သေချာစစ်ပါ
            'databaseURL': 'https://talk-3f6ec-default-rtdb.firebaseio.com' 
        })
    except Exception as e:
        st.error(f"Firebase ချိတ်ဆက်မှု မှားယွင်းနေပါသည်: {e}")

# --- ၂။ APP DESIGN ---
st.set_page_config(page_title="Walkie-Talkie App", layout="centered")
st.title("📻 Walkie-Talkie App")

# အသုံးပြုသူ နာမည်
user_name = st.sidebar.text_input("သင့်အမည်", value="Staff-1")
st.sidebar.markdown("---")

# --- ၃။ WALKIE TALKIE BUTTON (အသံပို့ရန်) ---
st.subheader("စကားပြောရန် ခလုတ်ကို နှိပ်ပါ")
audio_data = mic_recorder(
    start_prompt="🎤 စကားပြောမည်",
    stop_prompt="🛑 ရပ်မည်",
    key='recorder'
)

if audio_data:
    try:
        ref = db.reference('/chat_messages')
        ref.push({
            'name': user_name,
            'data': audio_data['bytes'].hex(),
            'type': 'audio',
            'timestamp': time.time()
        })
        st.rerun() # ပို့ပြီးတာနဲ့ screen ကိုချက်ချင်း refresh လုပ်ခိုင်းတာပါ
    except Exception as e:
        st.error(f"အသံပို့၍မရပါ: {e}")

# --- ၄။ CHAT INPUT (စာရေးပို့ရန်) ---
# ဒီအပိုင်းက စာပို့ပြီးရင် ချက်ချင်းပေါ်လာအောင် လုပ်ထားပါတယ်
chat_msg = st.chat_input("ဒီမှာ စာရေးပို့နိုင်ပါတယ်...")
if chat_msg:
    try:
        ref = db.reference('/chat_messages')
        ref.push({
            'name': user_name,
            'data': chat_msg,
            'type': 'text',
            'timestamp': time.time()
        })
        st.rerun() # စာပို့ပြီးတာနဲ့ ချက်ချင်းမြင်ရအောင် refresh လုပ်တာပါ
    except Exception as e:
        st.error(f"စာပို့၍မရပါ: {e}")

# --- ၅။ DISPLAY MESSAGES (စကားပြောထားသည်များကို ပြသခြင်း) ---
st.divider()
st.subheader("လတ်တလော ပြောဆိုချက်များ")

try:
    # နောက်ဆုံးပြောထားတဲ့ စာ/အသံ ၁၀ ခုကို ယူပါတယ်
    messages = db.reference('/chat_messages').order_by_child('timestamp').limit_to_last(10).get()

    if messages:
        # အသစ်ဆုံးကို အပေါ်မှာ ပြချင်ရင် reversed(messages) သုံးပါ
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
    st.info("ဒေတာများ ဖတ်ယူနေဆဲဖြစ်သည်။ Firebase Rules ကို True ပေးထားရန် လိုအပ်ပါသည်။")
