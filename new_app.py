import streamlit as st
import google.generativeai as genai
import os
import tempfile
import time
import logging
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Page Configuration ---
st.set_page_config(
    page_title="تقييم مهارات كرة القدم - التمرير والاستقبال",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- CSS Styling (Arabic) ---
st.markdown("""
<style>
    /* RTL Direction and Main App Styling */
    body { direction: rtl; }
    .stApp { 
        background: linear-gradient(135deg, #0f1419 0%, #1a2332 50%, #2d3748 100%);
        color: white; 
    }
    
    /* Header Styling */
    .main-header { 
        text-align: center; 
        color: #00D4AA; 
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    
    /* Skill Options */
    .skill-option { 
        font-size: 18px; 
        margin: 10px 0; 
        color: #FFFFFF !important;
    }
    
    /* Assessment Results */
    .assessment-result { 
        font-size: 24px; 
        font-weight: bold; 
        text-align: center; 
        padding: 20px; 
        border-radius: 15px; 
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Result Colors - Updated for new rubric terminology */
    .مثالي { 
        background: linear-gradient(135deg, #38A169, #2F855A); 
        color: white; 
        border-color: #9AE6B4;
    }
    .جيد { 
        background: linear-gradient(135deg, #DD6B20, #C05621); 
        color: white; 
        border-color: #FBD38D;
    }
    .غيرمقبول { 
        background: linear-gradient(135deg, #E53E3E, #C53030); 
        color: white; 
        border-color: #FC8181;
    }
    /* Legacy colors for compatibility */
    .ضعيف { 
        background: linear-gradient(135deg, #E53E3E, #C53030); 
        color: white; 
        border-color: #FC8181;
    }
    .متوسط { 
        background: linear-gradient(135deg, #DD6B20, #C05621); 
        color: white; 
        border-color: #FBD38D;
    }
    
    /* Upload Section */
    .upload-section { 
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(45, 55, 72, 0.2)); 
        padding: 25px; 
        border-radius: 15px; 
        margin: 20px 0;
        border: 1px solid rgba(0, 212, 170, 0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Model Section */
    .model-section {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(45, 55, 72, 0.1));
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #00D4AA, #00B894) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3) !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5) !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00B894, #00A085) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 212, 170, 0.4) !important;
        color: #FFFFFF !important;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.6) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
        color: #FFFFFF !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5) !important;
    }
    
    .stButton > button:focus {
        color: #FFFFFF !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5) !important;
        outline: 2px solid rgba(0, 212, 170, 0.5) !important;
        outline-offset: 2px !important;
    }
    
    /* Primary Button (Special styling for main action buttons) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #E53E3E, #C53030) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 15px rgba(229, 62, 62, 0.3) !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5) !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #C53030, #B91C1C) !important;
        box-shadow: 0 6px 20px rgba(229, 62, 62, 0.4) !important;
        color: #FFFFFF !important;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.6) !important;
    }
    
    .stButton > button[kind="primary"]:active {
        color: #FFFFFF !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5) !important;
    }
    
    .stButton > button[kind="primary"]:focus {
        color: #FFFFFF !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5) !important;
        outline: 2px solid rgba(229, 62, 62, 0.5) !important;
        outline-offset: 2px !important;
    }
    
    /* Ensure button text is always visible */
    .stButton > button span {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        text-shadow: inherit !important;
    }
    
    /* Radio Buttons */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: rgba(45, 55, 72, 0.8) !important;
        border: 1px solid rgba(0, 212, 170, 0.3) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* File Uploader */
    .stFileUploader > div {
        background: rgba(45, 55, 72, 0.9) !important;
        border: 2px dashed rgba(0, 212, 170, 0.5);
        border-radius: 10px;
        padding: 20px;
    }
    
    /* File Uploader Text */
    .stFileUploader label, .stFileUploader span, .stFileUploader div, .stFileUploader p {
        color: #FFFFFF !important;
        background: transparent !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8) !important;
    }
    
    /* File Uploader Instructions */
    .stFileUploader .uploadedFileName {
        color: #00D4AA !important;
        font-weight: 600 !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8) !important;
    }
    
    /* Upload area text */
    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        background: rgba(45, 55, 72, 0.9) !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderDropzone"] * {
        color: #FFFFFF !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8) !important;
    }
    
    /* Success/Error/Info Messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(56, 161, 105, 0.2), rgba(47, 133, 90, 0.1)) !important;
        border: 1px solid #38A169 !important;
        border-radius: 10px !important;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(229, 62, 62, 0.2), rgba(197, 48, 48, 0.1)) !important;
        border: 1px solid #E53E3E !important;
        border-radius: 10px !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.2), rgba(0, 184, 148, 0.1)) !important;
        border: 1px solid #00D4AA !important;
        border-radius: 10px !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(45, 55, 72, 0.3) !important;
        border-radius: 10px !important;
        color: #00D4AA !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #FFFFFF !important;
        font-style: italic;
        margin-top: 30px;
    }
    
    /* Force ALL text to be white for better readability */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #FFFFFF !important;
    }
    
    .stMarkdown p, .stMarkdown div, .stMarkdown span, .stMarkdown li, .stMarkdown td, .stMarkdown th {
        color: #FFFFFF !important;
    }
    
    /* All general text elements */
    .stText, .stMarkdown, .stWrite {
        color: #FFFFFF !important;
    }
    
    /* Labels and form text */
    label, .stSelectbox label, .stRadio label, .stFileUploader label {
        color: #FFFFFF !important;
    }
    
    /* Radio button text */
    .stRadio > div > label > div {
        color: #FFFFFF !important;
    }
    
    /* Selectbox text */
    .stSelectbox > div > div > div {
        color: #FFFFFF !important;
    }
    
    /* Improve text contrast in form elements */
    .stTextInput > div > div > input {
        background-color: rgba(45, 55, 72, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(0, 212, 170, 0.3) !important;
    }
    
    .stNumberInput > div > div > input {
        background-color: rgba(45, 55, 72, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(0, 212, 170, 0.3) !important;
    }
    
    /* Enhance caption styling */
    .stCaption {
        color: #FFFFFF !important;
    }
    
    /* Comprehensive white text enforcement */
    *, *::before, *::after {
        color: #FFFFFF !important;
    }
    
    /* Streamlit specific elements */
    .stApp, .stApp * {
        color: #FFFFFF !important;
    }
    
    /* Widget text */
    .stWidget label, .stWidget span, .stWidget div {
        color: #FFFFFF !important;
    }
    
    /* Expander content */
    .streamlit-expanderContent {
        color: #FFFFFF !important;
    }
    
    /* Metric labels and values */
    .metric-container {
        color: #FFFFFF !important;
    }
    
    /* Sidebar text (if used) */
    .css-1d391kg, .css-1d391kg * {
        color: #FFFFFF !important;
    }
    
    /* Override any remaining dark text */
    .css-10trblm, .css-16idsys, .css-qbe2hs {
        color: #FFFFFF !important;
    }
    
    /* Code blocks */
    .stCode {
        color: #FFFFFF !important;
        background-color: rgba(45, 55, 72, 0.8) !important;
    }
    
    /* JSON and code display */
    pre, code {
        color: #FFFFFF !important;
        background-color: rgba(45, 55, 72, 0.8) !important;
    }
    
    /* Critical: Force text shadow for ALL text elements to ensure readability */
    * {
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7) !important;
    }
    
    /* Radio button text with strong contrast */
    .stRadio [data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9) !important;
        background: rgba(45, 55, 72, 0.3) !important;
        padding: 5px !important;
        border-radius: 5px !important;
    }
    
    /* Widget labels with strong visibility */
    [data-testid="stFileUploaderInstruction"] {
        color: #FFFFFF !important;
        background: rgba(45, 55, 72, 0.9) !important;
        padding: 10px !important;
        border-radius: 5px !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9) !important;
        font-weight: 600 !important;
    }
    
    /* Selectbox options */
    .stSelectbox [data-testid="stSelectboxLabel"] {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9) !important;
        background: rgba(45, 55, 72, 0.5) !important;
        padding: 5px !important;
        border-radius: 3px !important;
    }
    
    /* All markdown containers */
    [data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8) !important;
    }
    
    /* Upload instruction text */
    .stFileUploader small {
        color: #FFFFFF !important;
        background: rgba(45, 55, 72, 0.9) !important;
        padding: 8px !important;
        border-radius: 5px !important;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.9) !important;
        display: inline-block !important;
    }
    
    /* Form field labels */
    .stFormField label {
        color: #FFFFFF !important;
        background: rgba(45, 55, 72, 0.7) !important;
        padding: 5px 10px !important;
        border-radius: 5px !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9) !important;
        font-weight: 600 !important;
    }
    
    /* Ensure all widget containers have dark backgrounds */
    .stWidget {
        background: rgba(45, 55, 72, 0.1) !important;
        padding: 10px !important;
        border-radius: 8px !important;
        margin: 5px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Constants ---
NOT_CLEAR_AR = "غير واضح"

# Assessment options
ASSESSMENT_OPTIONS = {
    "تمرير": "Passing",
    "استقبال": "Receiving", 
    "كلاهما": "Both"
}

# Assessment grades in Arabic - Updated with new rubric terminology
GRADE_MAP = {
    "مثالي": "مثالي",
    "الزاوية المثالية": "مثالي",
    "جيد": "جيد",
    "النطاق الجيد": "جيد",
    "غير مقبول": "غير مقبول",
    "تحذير": "غير مقبول",
    "غير مقبول/تحذير": "غير مقبول",
    # Legacy mappings for compatibility
    "ضعيف": "غير مقبول",
    "متوسط": "جيد", 
    "poor": "غير مقبول",
    "average": "جيد",
    "good": "جيد",
    "weak": "غير مقبول",
    "medium": "جيد",
    "excellent": "مثالي",
    "ideal": "مثالي",
    "acceptable": "جيد",
    "unacceptable": "غير مقبول",
    "warning": "غير مقبول"
}

# Gemini Models - Updated with latest models
GEMINI_MODELS = [
    # Gemini 2.5 Series (Latest and Recommended)
    "models/gemini-2.5-flash",
    "models/gemini-2.5-pro",
    
    # Gemini 2.0 Series
    "models/gemini-2.0-flash",
    "models/gemini-2.0-pro", 
    "models/gemini-2.0-flash-exp",
    "models/gemini-2.0-flash-thinking-exp",
    
    # Gemini 1.5 Series (Legacy - for compatibility)
    "models/gemini-1.5-pro",
    "models/gemini-1.5-flash", 
    "models/gemini-1.5-flash-8b",
    "models/gemini-1.5-pro-exp-0827",
    "models/gemini-1.5-pro-exp-0801",
    "models/gemini-1.5-flash-exp-0827",
    "models/gemini-1.5-flash-8b-exp-0827",
    
    # Additional models
    "models/gemini-pro",
    "models/gemini-pro-vision"
]

# --- Gemini API Configuration ---
def configure_gemini_api():
    """Configure Gemini API with multiple fallback options"""
    api_key = None
    
    # Method 1: Try Streamlit secrets first
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        logging.info("Gemini API Key loaded from Streamlit secrets.")
    except (KeyError, FileNotFoundError):
        logging.info("Gemini API Key not found in Streamlit secrets, trying environment variables.")
    
    # Method 2: Try environment variables if secrets failed
    if not api_key:
        # Try GEMINI_API_KEY first
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            logging.info("Gemini API Key loaded from GEMINI_API_KEY environment variable.")
        else:
            # Try GOOGLE_API_KEY as fallback
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                logging.info("Gemini API Key loaded from GOOGLE_API_KEY environment variable.")
    
    # Configure API if key found
    if api_key and api_key != "your_gemini_api_key_here":
        try:
            genai.configure(api_key=api_key)
            logging.info("Gemini API configured successfully.")
            return True
        except Exception as e:
            st.error(f"فشل في إعداد Gemini API: {e}")
            logging.error(f"Gemini API configuration failed: {e}")
            return False
    else:
        st.error("لم يتم العثور على مفتاح Gemini API صالح.")
        st.info("**طرق إضافة مفتاح API:**")
        st.info("1. **Streamlit Secrets**: أضف `GEMINI_API_KEY` في ملف `.streamlit/secrets.toml`")
        st.info("2. **متغيرات البيئة**: ضع المفتاح في ملف `.env` أو متغيرات النظام")
        st.info("3. **احصل على مفتاح API من**: https://aistudio.google.com/app/apikey")
        st.code("""
# في ملف .env
GEMINI_API_KEY=your_actual_api_key_here

# أو في .streamlit/secrets.toml  
GEMINI_API_KEY = "your_actual_api_key_here"
        """, language="toml")
        return False

# Configure API
if not configure_gemini_api():
    st.stop()

# --- Session State ---
if "model_name" not in st.session_state:
    st.session_state.model_name = "models/gemini-2.5-flash"  # Updated to latest recommended model

@st.cache_resource
def load_gemini_model(model_name):
    """Loads the Gemini model with specific configurations."""
    try:
        generation_config = {
             "temperature": 0.2,
             "top_p": 1,
             "top_k": 1,
             "max_output_tokens": 400,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ]
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        logging.info(f"Gemini Model '{model_name}' loaded successfully.")
        return model
    except Exception as e:
        st.error(f"فشل تحميل نموذج Gemini '{model_name}': {e}")
        logging.error(f"Gemini model loading failed: {e}")
        return None

def test_gemini_connection():
    """Test basic Gemini API connectivity."""
    try:
        model = load_gemini_model(st.session_state.model_name)
        if not model:
            return False
            
        test_prompt = "اكتب الرقم 5 فقط لاختبار الاتصال"
        test_response = model.generate_content(test_prompt)

        st.success(f"اختبار Gemini API نجح. الاستجابة: {test_response.text}")
        logging.info(f"API test successful. Raw response: {test_response}")
        return True

    except Exception as e:
        st.error(f"فشل اختبار Gemini API: {e}")
        logging.error(f"API test failed: {e}", exc_info=True)
        return False

def create_assessment_prompt(skill_type):
    """Creates the prompt for skill assessment based on detailed biomechanical rubrics."""
    
    # Add safety preamble to avoid triggering filters
    safety_preamble = """
    هذا تحليل تعليمي لأغراض تحسين الأداء الرياضي في كرة القدم.
    الهدف هو تعزيز التدريب وتطوير المهارات في بيئة آمنة وصحية.
    """
    
    if skill_type == "تمرير":
        prompt = f"""
        مهمتك هي تقييم مهارة التمرير القصير في كرة القدم باستخدام المعايير التقنية المحددة.

        **المعايير التقنية للتقييم:**

        **1. ركبة القدم الضاربة:**
        - مثالي: القدم الداعمة بزاوية مناسبة (مرجع: 95°-110°) مع استقرار وتوازن واضح
        - جيد: زاوية مقبولة (مرجع: 111°-130°) مع توازن معقول
        - غير مقبول: زاوية غير مناسبة (>130° أو <95°) أو عدم استقرار واضح

        **2. ركبة القدم المرتكزة:**
        - مثالي: توازن ممتاز مع ركبة مرتكزة في وضع مستقر (مرجع: 130°-145°)
        - جيد: توازن جيد مع وضعية مقبولة (مرجع: 120°-129°)
        - غير مقبول: عدم توازن أو وضعية غير مستقرة (>150° أو <120°)

        **3. انحناء الجذع:**
        - مثالي: انحناء مناسب للأمام (مرجع: 15°-30°) يساعد في التحكم والتوازن
        - جيد: انحناء مقبول (مرجع: 10°-14° أو 31°-35°)
        - غير مقبول: انحناء غير مناسب (<10° أو >35°) أو وقوف مستقيم تماما

        **4. المسافة بين القدم الداعمة والكرة:**
        - مثالي: مسافة مثلى تحافظ على التوازن والدقة (مرجع: 10-15 سم)
        - جيد: مسافة مقبولة (مرجع: 8-9 سم أو 16-18 سم) مع توازن معقول
        - غير مقبول: قريب جدا (<8 سم) أو بعيد جدا (>18 سم) مما يقلل التحكم

        **تعليمات التقييم:**
        راقب الفيديو بعناية وركز على:
        - وضعية الجسم العامة أثناء التمرير
        - استقرار القدم الداعمة
        - انحناء الجذع للأمام
        - المسافة بين القدم والكرة
        - السلاسة العامة للحركة

        **طريقة الاستجابة:**
        قدم التقييم بالتنسيق التالي فقط:
        ركبة القدم الضاربة: [مثالي/جيد/غير مقبول]
        ركبة القدم المرتكزة: [مثالي/جيد/غير مقبول] 
        انحناء الجذع: [مثالي/جيد/غير مقبول]
        المسافة للكرة: [مثالي/جيد/غير مقبول]
        التقييم العام: [مثالي/جيد/غير مقبول]

        لا تكتب أي شيء آخر غير هذا التنسيق.
        """
        
    elif skill_type == "استقبال":
        prompt = safety_preamble + f"""
        prompt = f"""
        مهمتك هي تقييم مهارة استلام الكرة في كرة القدم باستخدام المعايير التقنية المحددة.

        **المعايير التقنية للتقييم:**

        **1. ركبة القدم المستلمة:**
        - مثالي: وضعية مناسبة تساعد على إبطاء استقبال الكرة وزيادة التحكم (مرجع: 100°-115°)
        - جيد: وضعية مقبولة للاستقبال (مرجع: 90°-99° أو 116°-125°)
        - غير مقبول: وضعية غير مناسبة (<90° أو >125°) تقلل التحكم

        **2. ركبة القدم المرتكزة:**
        - مثالي: توازن وثبات واضح للجسم (مرجع: 130°-150°)
        - جيد: توازن مقبول (مرجع: 120°-129°)
        - غير مقبول: عدم توازن أو ثبات (<120° أو >155°)

        **3. انحناء الجذع:**
        - مثالي: انحناء طفيف للأمام يساعد على الاستقبال السليم (مرجع: 10°-25°)
        - جيد: انحناء مقبول (مرجع: 5°-9° أو 26°-30°)
        - غير مقبول: وقوف مستقيم أو انحناء مفرط (<5° أو >30°)

        **4. زاوية الداخل:**
        - مثالي: تحكم ممتاز في الكرة ومنع ارتدادها (مرجع: 80°-100°)
        - جيد: تحكم مقبول (مرجع: 70°-79° أو 101°-110°)
        - غير مقبول: فقدان التحكم أو ارتداد الكرة (<70° أو >110°)

        **تعليمات التقييم:**
        راقب الفيديو بعناية وركز على:
        - وضعية الجسم عند استقبال الكرة
        - استقرار القدم الداعمة
        - انحناء الجذع قليلا للأمام
        - التحكم في الكرة بعد الاستقبال
        - السلاسة العامة للحركة

        **طريقة الاستجابة:**
        قدم التقييم بالتنسيق التالي فقط:
        ركبة القدم المستلمة: [مثالي/جيد/غير مقبول]
        ركبة القدم المرتكزة: [مثالي/جيد/غير مقبول]
        انحناء الجذع: [مثالي/جيد/غير مقبول]
        زاوية الداخل: [مثالي/جيد/غير مقبول]
        التقييم العام: [مثالي/جيد/غير مقبول]

        لا تكتب أي شيء آخر غير هذا التنسيق.
        """
        
    else:  # كلاهما
        prompt = safety_preamble + f"""
        مهمتك هي تقييم مهارتي التمرير القصير واستلام الكرة في كرة القدم باستخدام المعايير التقنية المحددة.

        **معايير التمرير:**
        - ركبة القدم الضاربة: توازن واستقرار مناسب (مرجع: 95°-110°)
        - ركبة القدم المرتكزة: وضعية متوازنة ومستقرة (مرجع: 130°-145°)
        - انحناء الجذع: انحناء مناسب للأمام للتحكم (مرجع: 15°-30°)
        - المسافة للكرة: مسافة مثلى للتوازن والدقة (مرجع: 10-15 سم)

        **معايير الاستلام:**
        - ركبة القدم المستلمة: وضعية تساعد على التحكم (مرجع: 100°-115°)
        - ركبة القدم المرتكزة: توازن وثبات للجسم (مرجع: 130°-150°)
        - انحناء الجذع: انحناء طفيف للأمام (مرجع: 10°-25°)
        - زاوية الداخل: تحكم في الكرة ومنع الارتداد (مرجع: 80°-100°)

        راقب الفيديو وقيّم كلا المهارتين بناء على جودة التنفيذ.

        **طريقة الاستجابة:**
        التمرير - ركبة القدم الضاربة: [مثالي/جيد/غير مقبول]
        التمرير - ركبة القدم المرتكزة: [مثالي/جيد/غير مقبول]
        التمرير - انحناء الجذع: [مثالي/جيد/غير مقبول]
        التمرير - المسافة للكرة: [مثالي/جيد/غير مقبول]
        التمرير - التقييم العام: [مثالي/جيد/غير مقبول]

        الاستلام - ركبة القدم المستلمة: [مثالي/جيد/غير مقبول]
        الاستلام - ركبة القدم المرتكزة: [مثالي/جيد/غير مقبول]
        الاستلام - انحناء الجذع: [مثالي/جيد/غير مقبول]
        الاستلام - زاوية الداخل: [مثالي/جيد/غير مقبول]
        الاستلام - التقييم العام: [مثالي/جيد/غير مقبول]

        لا تكتب أي شيء آخر غير هذا التنسيق.
        """
    
    return prompt

def upload_and_wait_gemini(video_path, display_name="video_upload", status_placeholder=st.empty()):
    """Upload video to Gemini and wait for processing."""
    uploaded_file = None
    status_placeholder.info(f"جاري رفع الفيديو '{os.path.basename(display_name)}'...")
    logging.info(f"Starting upload for {display_name}")
    
    try:
        safe_display_name = f"upload_{int(time.time())}_{os.path.basename(display_name)}"
        uploaded_file = genai.upload_file(path=video_path, display_name=safe_display_name)
        status_placeholder.info(f"اكتمل الرفع. برجاء الانتظار للمعالجة...")
        logging.info(f"Upload successful for {display_name}, file name: {uploaded_file.name}")

        timeout = 300
        start_time = time.time()
        while uploaded_file.state.name == "PROCESSING":
            if time.time() - start_time > timeout:
                logging.error(f"Timeout waiting for file processing")
                raise TimeoutError(f"انتهت مهلة معالجة الفيديو. حاول مرة أخرى.")
            time.sleep(10)
            uploaded_file = genai.get_file(uploaded_file.name)
            logging.debug(f"File {uploaded_file.name} state: {uploaded_file.state.name}")

        if uploaded_file.state.name == "FAILED":
            logging.error(f"File processing failed")
            raise ValueError(f"فشلت معالجة الفيديو من جانب Google.")
        elif uploaded_file.state.name != "ACTIVE":
             logging.error(f"Unexpected file state {uploaded_file.state.name}")
             raise ValueError(f"حالة ملف فيديو غير متوقعة: {uploaded_file.state.name}")

        status_placeholder.success(f"الفيديو جاهز للتحليل.")
        logging.info(f"File {uploaded_file.name} is ACTIVE.")
        return uploaded_file

    except Exception as e:
        status_placeholder.error(f"خطأ أثناء رفع/معالجة الفيديو: {e}")
        logging.error(f"Upload/Wait failed: {e}", exc_info=True)
        if uploaded_file and uploaded_file.state.name != "ACTIVE":
            try:
                genai.delete_file(uploaded_file.name)
                logging.info(f"Cleaned up failed file: {uploaded_file.name}")
            except Exception as del_e:
                 logging.warning(f"Failed to delete file: {del_e}")
        return None

def create_simple_fallback_prompt(skill_type):
    """Simple fallback prompt that's less likely to trigger safety filters"""
    if skill_type == "تمرير":
        return """
        قيم هذه مهارة كرة القدم للتدريب الرياضي. 
        الخيارات: مثالي أو جيد أو غير مقبول
        ارجع الرد بهذا التنسيق:
        ركبة القدم الضاربة: [مثالي/جيد/غير مقبول]
        التقييم العام: [مثالي/جيد/غير مقبول]
        """
    elif skill_type == "استقبال":
        return """
        قيم هذه مهارة استقبال الكرة للتدريب. 
        الخيارات: مثالي أو جيد أو غير مقبول
        ارجع الرد بهذا التنسيق:
        ركبة القدم المستلمة: [مثالي/جيد/غير مقبول]
        التقييم العام: [مثالي/جيد/غير مقبول]
        """
    else:
        return """
        قيم مهارات كرة القدم للتدريب. 
        الخيارات: مثالي أو جيد أو غير مقبول
        ارجع الرد بهذا التنسيق:
        التمرير - التقييم العام: [مثالي/جيد/غير مقبول]
        الاستلام - التقييم العام: [مثالي/جيد/غير مقبول]
        """

def analyze_video_skill(gemini_file_obj, skill_type, status_placeholder=st.empty()):
    """Analyze video for skill assessment."""
    model = load_gemini_model(st.session_state.model_name)
    if not model:
        return None
        
    prompt = create_assessment_prompt(skill_type)
    status_placeholder.info(f"Gemini يحلل مهارة {skill_type}...")
    logging.info(f"Requesting analysis for skill '{skill_type}' using file {gemini_file_obj.name}")

    try:
        response = model.generate_content([prompt, gemini_file_obj], request_options={"timeout": 180})

        # Check if response was blocked by safety filters
        if not response.candidates:
             status_placeholder.warning(f"استجابة Gemini فارغة لمهارة {skill_type}")
             logging.warning(f"No candidates returned for {skill_type}")
             return None
        
        # Check for safety blocking
        candidate = response.candidates[0]
        if hasattr(candidate, 'finish_reason'):
            finish_reason = candidate.finish_reason
            if finish_reason == 2:  # SAFETY
                status_placeholder.error(f"تم حظر المحتوى بواسطة مرشحات الأمان - يرجى استخدام فيديو مختلف")
                logging.error(f"Content blocked by safety filters for {skill_type}, finish_reason: {finish_reason}")
                return None
            elif finish_reason == 3:  # RECITATION
                status_placeholder.error(f"تم حظر المحتوى بسبب مخاوف النسخ - يرجى استخدام فيديو مختلف")
                logging.error(f"Content blocked by recitation filter for {skill_type}, finish_reason: {finish_reason}")
                return None
            elif finish_reason == 4:  # OTHER
                status_placeholder.error(f"فشل في التحليل لأسباب أخرى - يرجى المحاولة مرة أخرى")
                logging.error(f"Content blocked for other reasons for {skill_type}, finish_reason: {finish_reason}")
                return None

        # Try to get text, with error handling for safety blocks
        try:
            raw_text = response.text.strip()
            logging.info(f"Raw response for {skill_type}: {raw_text}")
        except ValueError as ve:
            if "finish_reason" in str(ve):
                status_placeholder.warning(f"لم يتمكن Gemini من تحليل هذا الفيديو - جاري المحاولة بطريقة مختلفة...")
                logging.warning(f"Primary prompt blocked, trying fallback for {skill_type}: {ve}")
                
                # Try with simpler fallback prompt
                fallback_prompt = create_simple_fallback_prompt(skill_type)
                status_placeholder.info(f"جاري المحاولة بطريقة مبسطة...")
                
                try:
                    fallback_response = model.generate_content([fallback_prompt, gemini_file_obj], request_options={"timeout": 180})
                    if fallback_response.candidates and hasattr(fallback_response.candidates[0], 'content'):
                        raw_text = fallback_response.text.strip()
                        logging.info(f"Fallback successful for {skill_type}: {raw_text}")
                        status_placeholder.success(f"تم التحليل بنجاح باستخدام طريقة مبسطة")
                    else:
                        status_placeholder.error(f"فشل في تحليل الفيديو - يرجى استخدام فيديو أوضح")
                        logging.error(f"Both primary and fallback prompts failed for {skill_type}")
                        return None
                except Exception as fallback_error:
                    status_placeholder.error(f"فشل في تحليل الفيديو - يرجى استخدام فيديو مختلف")
                    logging.error(f"Fallback also failed for {skill_type}: {fallback_error}")
                    return None
            else:
                raise ve
        
        # Parse response based on skill type
        if skill_type == "كلاهما":
            # Parse both skills with detailed criteria
            results = {
                'التمرير': {},
                'الاستلام': {}
            }
            
            lines = raw_text.split('\n')
            for line in lines:
                line = line.strip()
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        key = parts[0].strip()
                        value = parts[1].strip().replace('[', '').replace(']', '')
                        
                        # Map the grade using GRADE_MAP
                        mapped_value = GRADE_MAP.get(value.lower(), value)
                        
                        # Parse passing criteria
                        if 'التمرير -' in key:
                            criterion = key.replace('التمرير -', '').strip()
                            results['التمرير'][criterion] = mapped_value
                        # Parse receiving criteria
                        elif 'الاستلام -' in key:
                            criterion = key.replace('الاستلام -', '').strip()
                            results['الاستلام'][criterion] = mapped_value
            
            # If no detailed results, try fallback parsing
            if not results['التمرير'] and not results['الاستلام']:
                for grade in ['مثالي', 'جيد', 'غير مقبول']:
                    if grade in raw_text:
                        results['التمرير']['التقييم العام'] = grade
                        results['الاستلام']['التقييم العام'] = grade
                        break
                        
            return results if results['التمرير'] or results['الاستلام'] else {'التمرير': {'التقييم العام': NOT_CLEAR_AR}, 'الاستلام': {'التقييم العام': NOT_CLEAR_AR}}
        else:
            # Parse single skill with detailed criteria
            results = {}
            lines = raw_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        key = parts[0].strip()
                        value = parts[1].strip().replace('[', '').replace(']', '')
                        
                        # Map the grade using GRADE_MAP
                        mapped_value = GRADE_MAP.get(value.lower(), value)
                        results[key] = mapped_value
            
            # If no detailed results, try simple grade parsing
            if not results:
                for grade in ['مثالي', 'جيد', 'غير مقبول']:
                    if grade in raw_text:
                        results['التقييم العام'] = grade
                        break
                        
            return results if results else {'التقييم العام': NOT_CLEAR_AR}

    except Exception as e:
        status_placeholder.error(f"حدث خطأ أثناء تحليل مهارة {skill_type}: {e}")
        logging.error(f"Analysis failed for {skill_type}: {e}", exc_info=True)
        return None

def display_assessment_result(skill, result):
    """Display the assessment result with styling for detailed rubric evaluation."""
    
    # Get CSS class based on grade
    def get_css_class(grade):
        if grade == 'مثالي':
            return 'جيد'  # Use green styling
        elif grade == 'جيد':
            return 'متوسط'  # Use orange styling
        elif grade == 'غير مقبول':
            return 'ضعيف'  # Use red styling
        else:
            return 'متوسط'  # Default to orange
    
    if isinstance(result, dict):
        # Check if this is the new detailed format
        if 'التمرير' in result and 'الاستلام' in result:
            # Both skills with detailed criteria
            st.markdown("### نتائج التقييم المفصلة")
            
            # Display passing results
            if result['التمرير']:
                st.markdown("#### نتائج التمرير")
                for criterion, grade in result['التمرير'].items():
                    css_class = get_css_class(grade)
                    icon = '[مثالي]' if grade == 'مثالي' else '[جيد]' if grade == 'جيد' else '[غير مقبول]'
                    st.markdown(f"""
                    <div class="assessment-result {css_class}">
                        {icon} {criterion}: {grade}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Display receiving results
            if result['الاستلام']:
                st.markdown("#### نتائج الاستلام")
                for criterion, grade in result['الاستلام'].items():
                    css_class = get_css_class(grade)
                    icon = '[مثالي]' if grade == 'مثالي' else '[جيد]' if grade == 'جيد' else '[غير مقبول]'
                    st.markdown(f"""
                    <div class="assessment-result {css_class}">
                        {icon} {criterion}: {grade}
                    </div>
                    """, unsafe_allow_html=True)
                    
        elif len(result) > 1 and any(':' not in str(k) for k in result.keys()):
            # Single skill with detailed criteria
            st.markdown("### نتائج التقييم المفصلة")
            for criterion, grade in result.items():
                css_class = get_css_class(grade)
                icon = '[مثالي]' if grade == 'مثالي' else '[جيد]' if grade == 'جيد' else '[غير مقبول]'
                st.markdown(f"""
                <div class="assessment-result {css_class}">
                    {icon} {criterion}: {grade}
                </div>
                """, unsafe_allow_html=True)
        else:
            # Legacy format - simple skill results
            st.markdown("### نتائج التقييم")
            for skill_name, grade in result.items():
                css_class = get_css_class(grade)
                st.markdown(f"""
                <div class="assessment-result {css_class}">
                    {skill_name}: {grade}
                </div>
                """, unsafe_allow_html=True)
    else:
        # Single result - could be simple grade or detailed format
        if isinstance(result, str):
            css_class = get_css_class(result)
            st.markdown("### نتيجة التقييم")
            st.markdown(f"""
            <div class="assessment-result {css_class}">
                {skill}: {result}
            </div>
            """, unsafe_allow_html=True)
        else:
            # This shouldn't happen, but handle it gracefully
            st.markdown("### نتيجة التقييم")
            st.markdown(f"""
            <div class="assessment-result متوسط">
                {skill}: {str(result)}
            </div>
            """, unsafe_allow_html=True)

# --- Main App ---
def main():
    # Header
    st.markdown('<h1 class="main-header">تقييم مهارات كرة القدم - التمرير والاستقبال</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 18px;">تطبيق بسيط لتقييم مهارات التمرير والاستقبال باستخدام الذكاء الاصطناعي</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Skill Selection
    st.markdown("### 1️⃣ اختر المهارة المراد تقييمها")
    selected_skill = st.radio(
        "نوع التقييم:",
        options=list(ASSESSMENT_OPTIONS.keys()),
        key="skill_selection",
        horizontal=True
    )
    
    st.markdown("---")
    
    # Video Upload
    st.markdown("### 2️⃣ ارفع فيديو المهارة")
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📂 اختر ملف الفيديو",
        type=["mp4", "avi", "mov", "mkv", "webm"],
        help="ارفع فيديو يظهر مهارة التمرير و/أو الاستقبال"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Analysis Button
    if uploaded_file:
        st.markdown("### 3️⃣ ابدأ التحليل")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 تحليل المهارة", use_container_width=True, type="primary"):
                # Process video
                local_temp_file_path = None
                analysis_error = False
                
                status_placeholder = st.empty()
                
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        local_temp_file_path = tmp_file.name
                    
                    # Upload to Gemini
                    gemini_file = upload_and_wait_gemini(
                        local_temp_file_path, 
                        uploaded_file.name, 
                        status_placeholder
                    )
                    
                    if gemini_file:
                        # Analyze skill
                        result = analyze_video_skill(
                            gemini_file, 
                            selected_skill, 
                            status_placeholder
                        )
                        
                        if result:
                            status_placeholder.success("اكتمل التحليل!")
                            time.sleep(1)
                            status_placeholder.empty()
                            
                            # Display result
                            display_assessment_result(selected_skill, result)
                            
                            # Add some celebration for excellent results
                            celebration_triggered = False
                            if isinstance(result, dict):
                                # Check for detailed rubric results
                                if 'التمرير' in result and 'الاستلام' in result:
                                    # Check if any criteria got 'مثالي'
                                    for skill_results in result.values():
                                        if isinstance(skill_results, dict) and any(grade == 'مثالي' for grade in skill_results.values()):
                                            celebration_triggered = True
                                            break
                                elif any(grade == 'مثالي' or grade == 'جيد' for grade in (result.values() if isinstance(result, dict) else [result])):
                                    celebration_triggered = True
                            elif result == 'مثالي' or result == 'جيد':
                                celebration_triggered = True
                                
                            if celebration_triggered:
                                st.balloons()
                        else:
                            st.error("فشل في تحليل المهارة")
                            
                        # Cleanup Gemini file
                        try:
                            genai.delete_file(gemini_file.name)
                            logging.info(f"Cleaned up Gemini file: {gemini_file.name}")
                        except Exception as e:
                            logging.warning(f"Could not delete Gemini file: {e}")
                    else:
                        analysis_error = True
                        
                except Exception as e:
                    st.error(f"حدث خطأ في معالجة الفيديو: {e}")
                    logging.error(f"Video processing error: {e}", exc_info=True)
                    analysis_error = True
                    
                finally:
                    # Cleanup local temp file
                    if local_temp_file_path and os.path.exists(local_temp_file_path):
                        try:
                            os.remove(local_temp_file_path)
                            logging.info(f"Deleted local temp file: {local_temp_file_path}")
                        except Exception as e:
                            logging.warning(f"Could not delete local temp file: {e}")
    
    st.markdown("---")
    
    # Advanced Options (Model Selection)
    with st.expander("⚙️ خيارات متقدمة - اختيار نموذج Gemini"):
        st.markdown('<div class="model-section">', unsafe_allow_html=True)
        
        st.markdown("#### اختر نموذج Gemini:")
        
        # Get current model index
        try:
            current_index = GEMINI_MODELS.index(st.session_state.model_name)
        except ValueError:
            current_index = 0
            
        selected_model = st.selectbox(
            "النموذج المتاح:",
            options=GEMINI_MODELS,
            index=current_index,
            key="model_selector"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("استخدم هذا النموذج", use_container_width=True):
                if selected_model != st.session_state.model_name:
                    st.session_state.model_name = selected_model
                    # Clear cache
                    try:
                        st.cache_resource.clear()
                    except:
                        pass
                    st.success(f"تم تغيير النموذج إلى: {selected_model}")
                    st.rerun()
                else:
                    st.info("النموذج المحدد مستخدم بالفعل")
        
        with col2:
            if st.button("🧪 اختبر النموذج الحالي", use_container_width=True):
                test_gemini_connection()
        
        st.markdown(f"**النموذج الحالي:** `{st.session_state.model_name}`")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown('<div class="footer">تطبيق تقييم مهارات كرة القدم | مدعوم بتقنية Google Gemini AI</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
