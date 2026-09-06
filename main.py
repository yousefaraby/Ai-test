from ollama import chat
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email import message_from_bytes
import base64


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


# Load Gmail authentication
creds = Credentials.from_authorized_user_file(
    "token.json",
    SCOPES
)

# Connect to Gmail
service = build(
    "gmail",
    "v1",
    credentials=creds
)


# Get latest 3 emails
results = service.users().messages().list(
    userId="me",
    maxResults=3
).execute()

messages = results.get("messages", [])


emails_text = ""


for i, message in enumerate(messages, 1):

    msg = service.users().messages().get(
        userId="me",
        id=message["id"],
        format="raw"
    ).execute()

    raw_email = base64.urlsafe_b64decode(msg["raw"])

    email = message_from_bytes(raw_email)

    sender = email.get("From", "Unknown")
    subject = email.get("Subject", "No Subject")

    body = ""

    if email.is_multipart():

        for part in email.walk():

            if part.get_content_type() == "text/plain":

                payload = part.get_payload(decode=True)

                if payload:
                    body = payload.decode(
                        "utf-8",
                        errors="ignore"
                    )

                    break

    else:

        payload = email.get_payload(decode=True)

        if payload:
            body = payload.decode(
                "utf-8",
                errors="ignore"
            )

    emails_text += f"""
EMAIL {i}

From: {sender}
Subject: {subject}

Body:
{body[:3000]}

-------------------------
"""


# Send emails to Ollama
response = chat(
    model="phi3:3.8b",
    messages=[
        {
            "role": "user",
            "content": f"""
You are an email summarization assistant.

Summarize the following 3 emails.

For each email:
- Mention the sender.
- Mention the subject.
- Give 2-3 clear bullet points summarizing the important information.
- Keep the summary concise.

Emails:

{emails_text}
"""
        }
    ],
)


print("\n" + "=" * 60)
print("EMAIL SUMMARY")
print("=" * 60)

print(response["message"]["content"])