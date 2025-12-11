# Gmail Email Summarizer with AI + Auto Google Docs Export

An intelligent Streamlit app that **reads your Gmail inbox**, **summarizes emails using AI**, and **automatically appends the summary to a Google Doc** — all in one click.

Perfect for developers, freelancers, students, or anyone drowning in emails.

## Features

- Fetch latest emails directly from Gmail
- AI-powered summarization using Facebook's **BART-large-cnn**
- View full email body in an expandable section
- Download summary as Markdown (.md)
- One-click save to **Google Docs** (with proper formatting & timestamp)
- Fully local & secure OAuth 2.0 authentication

## Live Screenshot

![App Preview](https://i.imgur.com/0bL2e5K.png)  
*(Your app is already working perfectly!)*

## Quick Start (Local Run)

### 1. Clone the repo
```bash
git clone https://github.com/Turjoy01/Gmail-Email-Summarizer-with-AI-.git
cd gmail-summarizer
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Google Cloud Setup (One-time)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project → Enable **Gmail API** + **Google Docs API**
3. OAuth consent screen → External → Create
4. Credentials → Create OAuth Client ID → **Desktop Application**
5. Download the JSON file → rename it to `credentials.json` → place in project folder

### 5. Create `.env` file
```env
GMAIL_ADDRESS=your_email@gmail.com
APP_PASSWORD=your_16_digit_app_password
```
> Generate App Password here: https://myaccount.google.com/apppasswords (2FA must be ON)

### 6. Run the app
```bash
streamlit run app.py
```

First run → Google login window → Allow access → `token.pickle` will be created automatically.

From second run onward: no login needed!

## Google Docs Integration

1. Create a blank Google Doc
2. Copy the Document ID from the URL:  
   `https://docs.google.com/document/d/DOCUMENT_ID_HERE/edit`
3. Paste it in the sidebar → Check "Also save to Google Doc?"

Your summaries will be appended beautifully with sender, date, subject & AI summary.

## Project Structure
```
gmail-summarizer/
├── app.py                  # Main Streamlit application
├── credentials.json        # Google OAuth credentials (gitignore)
├── token.pickle            # Auto-generated login token (gitignore)
├── .env                    # Your secrets
├── requirements.txt
├── README.md               # This file
└── .gitignore
```
<img width="1866" height="930" alt="image" src="https://github.com/user-attachments/assets/57b2fadb-d906-4dd0-a715-2c81fdc91e53" />
