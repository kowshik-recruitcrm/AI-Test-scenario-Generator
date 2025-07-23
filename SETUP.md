# 🔧 Setup Guide - Test Scenario Generator

## 📋 Environment Configuration

### Step 1: Create .env File

Create a `.env` file in the project root directory with the following content:

```env
# Test Scenario Generator - Environment Configuration

# =============================================================================
# GOOGLE GEMINI API CONFIGURATION (REQUIRED)
# =============================================================================
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here

# =============================================================================
# CONFLUENCE CONFIGURATION (OPTIONAL - only if using Confluence)
# =============================================================================
# Your Confluence instance URL
CONFLUENCE_URL=https://your-company.atlassian.net

# Your Confluence username (usually your email)
CONFLUENCE_USERNAME=your_username@company.com

# Your Confluence API token
# Generate from: https://id.atlassian.com/manage-profile/security/api-tokens
CONFLUENCE_API_TOKEN=your_confluence_api_token

# =============================================================================
# OUTPUT CONFIGURATION (OPTIONAL)
# =============================================================================
# Directory where generated files will be saved
OUTPUT_DIR=./output
```

### Step 2: Get Your API Keys

#### 🔑 Google Gemini API Key (REQUIRED)

1. **Visit Google AI Studio**: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. **Sign in** with your Google account
3. **Click "Create API Key"**
4. **Copy the generated key**
5. **Paste it in your .env file** replacing `your_google_api_key_here`

#### 🔑 Confluence API Token (OPTIONAL)

Only needed if you want to load PRD data from Confluence:

1. **Visit Atlassian Account Settings**: [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. **Click "Create API token"**
3. **Give it a descriptive name** (e.g., "Test Scenario Generator")
4. **Copy the generated token**
5. **Update your .env file** with:
   - Your email address as `CONFLUENCE_USERNAME`
   - The token as `CONFLUENCE_API_TOKEN`
   - Your Confluence URL as `CONFLUENCE_URL`

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Test Your Setup

#### Quick Test (No API keys needed initially)
```bash
python main.py
```

#### Web Interface
```bash
streamlit run streamlit_app.py
```

## 🚀 Model Configuration

The system now uses **Gemini 2.5 Pro** - Google's advanced language model.

**Model Details:**
- **Model Name**: `gemini-2.5-pro`
- **Temperature**: 0.3 (for consistent results)
- **Max Tokens**: 4096

## 🛡️ Security Notes

- ⚠️ **Never commit your .env file** to version control
- 🔒 **Keep your API keys secure** and don't share them
- 📁 **The .env file should be in your .gitignore**
- 🔄 **Rotate your API keys periodically** for better security

## 🧪 Testing Without Confluence

You can test the entire system without Confluence credentials:

1. **Set only the Google API key** in your .env file
2. **Use the Quick Test feature** which uses sample data
3. **Upload images and Excel files** directly through the web interface

## 📁 Project Structure After Setup

```
Test scenario generator/
├── .env                    # Your environment variables (CREATE THIS)
├── output/                 # Generated files will appear here
├── agents/                 # AI agents
├── tools/                  # Data processing tools
├── main.py                 # Main application
├── streamlit_app.py       # Web interface
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

## 🆘 Troubleshooting

### Common Issues:

**1. "Missing environment variables" error**
- Make sure your .env file exists in the project root
- Check that GOOGLE_API_KEY is set correctly

**2. "Invalid API key" error**
- Verify your Google API key is correct
- Make sure the API key has the necessary permissions

**3. "Confluence connection failed"**
- Verify your Confluence URL format (should include https://)
- Check your username (should be your email)
- Ensure your API token is valid and has the right permissions

**4. Module import errors**
- Run `pip install -r requirements.txt` to install all dependencies
- Make sure you're using Python 3.8 or higher

### Need Help?

1. Check the logs in `test_scenario_generator.log`
2. Try the quick test first to verify basic functionality
3. Use the web interface for easier setup and debugging

## ✅ Setup Complete!

Once your .env file is configured with at least the Google API key, you're ready to generate test scenarios! 🎉 