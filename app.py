# app.py (Updated with Google Docs Integration)
import streamlit as st
import os
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from transformers import pipeline
import base64
import pickle
from datetime import datetime

# --- Config ---
load_dotenv()
st.set_page_config(page_title="Gmail Summarizer", layout="wide")
st.title("Gmail Email Summarizer")

# Updated Scopes: Add Docs write access
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/documents'
]

# --- Sidebar Login + Docs Setup ---
st.sidebar.header("Gmail Login")
gmail_address = st.sidebar.text_input("Gmail Address", value=os.getenv("GMAIL_ADDRESS", ""))
app_password = st.sidebar.text_input("App Password", type="password", value=os.getenv("APP_PASSWORD", ""))

# New: Google Docs Setup
st.sidebar.subheader("Google Docs Log")
doc_id = st.sidebar.text_input("Document ID (from URL)", placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")  # Example ID
if not doc_id:
    st.sidebar.info("Paste your Doc URL → Extract ID after '/d/'")

if st.sidebar.button("Connect to Gmail"):
    if gmail_address and app_password:
        st.session_state.gmail = gmail_address
        st.session_state.app_password = app_password
        st.success(f"Connected as {gmail_address}")
    else:
        st.error("Enter both!")

if 'gmail' not in st.session_state:
    st.info("Login in the sidebar first.")
    st.stop()

# --- Authenticate (Same as before) ---
def get_gmail_service():
    creds = None
    token_path = 'token.pickle'
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

# New: Get Docs Service
def get_docs_service():
    creds = None
    token_path = 'token.pickle'
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return build('docs', 'v1', credentials=creds)

# --- Fetch Emails (Same as before) ---
@st.cache_data(ttl=300)
def fetch_emails(max_results=20):
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    emails = []
    for msg in messages:
        m = service.users().messages().get(userId='me', id=msg['id']).execute()
        payload = m['payload']
        headers = payload['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')  # New: Fetch date
        snippet = m.get('snippet', '')
        emails.append({'id': msg['id'], 'subject': subject, 'from': sender, 'date': date, 'snippet': snippet})
    return emails

# --- Get Full Email (Same) ---
def get_full_email(msg_id):
    service = get_gmail_service()
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = msg['payload']
    parts = payload.get('parts')
    data = ''
    if parts:
        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                break
    else:
        data = payload['body'].get('data', '')
    if data:
        text = base64.urlsafe_b64decode(data).decode('utf-8')
    else:
        text = msg.get('snippet', '')
    return text

# --- Summarize (Same) ---
@st.cache_data
def summarize_email(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    max_input = 1000
    text = text[:max_input]
    summary = summarizer(text, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
    return summary

# New: Append to Google Doc
def append_to_doc(doc_id, sender, date, subject, summary):
    service = get_docs_service()
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1,  # Append at end (index 1 for empty/new docs; grows automatically)
                },
                'text': f"""
Sender: {sender}
Received: {date}
Subject: {subject}

AI Summary: {summary}

---
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}

""".strip()
            }
        }
    ]
    body = {'requests': requests}
    service.documents().batchUpdate(documentId=doc_id, body=body).execute()
    return True

# --- Main (Updated with Checkbox) ---
st.header("Select Email to Summarize")
try:
    emails = fetch_emails()
    if not emails:
        st.warning("No emails found.")
    else:
        selected = st.selectbox(
            "Choose an email",
            options=emails,
            format_func=lambda x: f"{x['from']} - {x['subject'][:50]}..."
        )
        if selected:
            with st.expander("View Full Email", expanded=False):
                full_text = get_full_email(selected['id'])
                st.text_area("Body", full_text, height=300)

            # Updated: Add checkbox for Docs
            save_to_doc = st.checkbox("Also save to Google Doc?")

            if st.button("Generate Summary"):
                with st.spinner("Summarizing..."):
                    summary = summarize_email(full_text)
                    report = f"""# Email Summary\n\n**From**: {selected['from']}\n**Subject**: {selected['subject']}\n**Date**: {selected['date']}\n\n## AI Summary\n{summary}\n\n---\n*Generated by BART LLM*"""
                    st.markdown(report)
                    st.download_button("Download (MD)", data=report, file_name=f"summary_{selected['id'][:8]}.md")

                    # New: If checkbox checked and Doc ID provided, append
                    if save_to_doc and doc_id:
                        try:
                            append_to_doc(doc_id, selected['from'], selected['date'], selected['subject'], summary)
                            st.success("✅ Summary saved to Google Doc!")
                        except Exception as e:
                            st.error(f"Docs save failed: {e}. Check Doc ID and permissions.")
                    elif save_to_doc and not doc_id:
                        st.warning("Enter Document ID in sidebar to save to Docs.")

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Ensure `credentials.json` is in the folder.")