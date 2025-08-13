# ⚽ تقييم مهارات كرة القدم - Football Skills Assessment App

تطبيق Streamlit لتقييم مهارات التمرير والاستقبال في كرة القدم باستخدام الذكاء الاصطناعي (Google Gemini).

## 🚀 Installation and Setup

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. API Key Configuration

You have two options to configure your Gemini API key:

#### Option A: Environment File (.env)
1. Copy the example file: `cp .env.example .env`
2. Edit `.env` and replace `your_gemini_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

#### Option B: Streamlit Secrets
1. Create `.streamlit/secrets.toml` file
2. Add your API key:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```

### 4. Get API Key
- Visit: https://aistudio.google.com/app/apikey
- Create a new API key for Gemini

### 5. Run the Application
```bash
streamlit run new_app.py
```

## 📋 Features

- ✅ Multiple Gemini model support (including latest 2.5 series)
- ✅ Dual API key configuration (Environment variables + Streamlit secrets)
- ✅ Video file upload and analysis
- ✅ Arabic UI with RTL support
- ✅ Skill assessment for passing and receiving
- ✅ Real-time video processing with status updates

## 🤖 Supported Models

The app includes all the latest Gemini models:

### Recommended (Latest)
- `gemini-2.5-flash` - General text & multimodal tasks
- `gemini-2.5-pro` - Coding and complex reasoning

### Gemini 2.0 Series
- `gemini-2.0-flash`
- `gemini-2.0-pro`
- `gemini-2.0-flash-exp`
- `gemini-2.0-flash-thinking-exp`

### Legacy Support
- `gemini-1.5-pro`
- `gemini-1.5-flash`
- And more...

## 🔧 Troubleshooting

### API Key Issues
If you see API key errors:
1. Check your API key is valid at Google AI Studio
2. Ensure it's properly set in `.env` or `secrets.toml`
3. Make sure you haven't left the placeholder text

### Import Errors
If you see import errors, make sure you're in the virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 📁 File Structure

```
.
├── new_app.py              # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment file template
├── .env                   # Your environment variables (create this)
└── README.md              # This file
```

## ⚠️ Note

Make sure to keep your API key secure and never commit it to version control!