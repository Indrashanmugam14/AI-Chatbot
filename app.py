import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
import os

# Set Streamlit Page Configuration (MUST be the first command)
st.set_page_config(page_title="Customer Support", layout="wide")

# Set up API key securely
API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=API_KEY)

# Initialize model
MODEL_NAME = "gemini-1.5-flash-001"
model = genai.GenerativeModel(MODEL_NAME)
translator = Translator()

# Supported Languages
LANGUAGES = {
    "English": "en",
    "Hindi (हिन्दी)": "hi",
    "Tamil (தமிழ்)": "ta",
    "Telugu (తెలుగు)": "te",
    "Marathi (मराठी)": "mr",
    "Bengali (বাংলা)": "bn",
    "Gujarati (ગુજરાતી)": "gu",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Malayalam (മലയാളം)": "ml",
    "Kannada (ಕನ್ನಡ)": "kn"
}

# Brand Selection
selected_brand = st.sidebar.selectbox("Choose Support", ["Crocs🥿", "Apple🍎"])

# Language Selection
selected_language = st.sidebar.selectbox("Select Language", list(LANGUAGES.keys()))
selected_lang_code = LANGUAGES[selected_language]

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to provide brand-specific responses
def get_brand_response(user_query, language_code):
    system_prompt = (
        f"You are {selected_brand}'s customer support assistant. "
        "Answer accurately about their products, returns, refunds, sizing, and shipping. "
        "Provide structured, **concise responses (6 lines max)** in English. "
        "If unsure, recommend contacting human support."
    )
    
    response = model.generate_content(f"{system_prompt}\nUser: {user_query}\n{selected_brand} Support:")
    english_response = '\n'.join(response.text.split('\n')[:6])  # Limit response to 6 lines

    # Translate response to selected language
    if language_code != "en":
        translated_response = translator.translate(english_response, dest=language_code).text
        return translated_response
    return english_response

# Function to convert text to speech
def text_to_speech(response_text, language="en"):
    tts = gTTS(text=response_text, lang=language)
    audio_file = "response.mp3"
    tts.save(audio_file)
    return audio_file

if st.button("Finish Chat"):
    st.markdown("✅ Thank you for contacting Crocsbot! Have a great day!😊")
    st.stop()

# Streamlit UI
st.title(f"{selected_brand} - AI Customer Support🤖🚀")
st.write(f"Welcome Ask me anything about🌍{selected_brand} products, orders, returns, or policies!")
st.write(f"Hi! how can I help you👋")


# Initialize session state for voice input
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""

# Voice input button
if st.button("Tap To Speak🔊"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now.")
        try:
            audio = recognizer.listen(source, timeout=5)
            st.session_state.voice_input = recognizer.recognize_google(audio, language="en")
            st.success(f"You said: {st.session_state.voice_input}")
        except sr.UnknownValueError:
            st.error("Sorry, I couldn't understand your voice.")
        except sr.RequestError:
            st.error("Speech recognition service is unavailable.")

# Chat input (text or voice)
user_query = st.text_input("🗨️Type a query...", st.session_state.voice_input)

# File uploader for images
uploaded_file = st.file_uploader("Upload an image (e.g., damaged product, wrong item received)", type=["jpg", "png", "jpeg"])

# Process user input
if st.button("▶️") and user_query:
    with st.spinner(f"{selected_brand} Support is typing..."):
        response = get_brand_response(user_query, selected_lang_code)
        st.session_state.chat_history.append((user_query, response))

    # Display chat messages in WhatsApp style
    st.write("### Chat")
    for query, reply in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(f"{query}")
        with st.chat_message("assistant"):
            st.write(f"{reply}")
        
    # Convert response to speech if voice input was used
    if st.session_state.voice_input:
        audio_file = text_to_speech(response, selected_lang_code)
        st.audio(audio_file, format="audio/mp3")
        st.session_state.voice_input = ""

    # Handle uploaded images
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        st.success("Your image has been uploaded successfully. Our team will review it and assist you accordingly.")

# Sidebar for quick links
st.sidebar.header(f"{selected_brand} - Support")
st.sidebar.write(f"Your AI-powered shopping assistant for all things {selected_brand}! 🏪📦")

if selected_brand == "Crocs🥿":
    st.sidebar.markdown("[Visit Crocs Official Website](https://www.crocs.com/)")
    st.sidebar.markdown("[Return Policy](https://www.crocs.com/customer-service/returns.html)")
    st.sidebar.markdown("[Contact Us](https://www.crocs.com/customer-service/contact-us.html)")
elif selected_brand == "Apple🍎":
    st.sidebar.markdown("[Visit Apple Official Website](https://www.apple.com/)")
    st.sidebar.markdown("[Apple Support](https://support.apple.com/)")
    st.sidebar.markdown("[Apple Repair Services](https://support.apple.com/repair)")

st.sidebar.info(f"Need human support? Visit our [Contact Us page](https://www.{selected_brand.lower()}.com/) or email us at **support@{selected_brand.lower()}.com**")
