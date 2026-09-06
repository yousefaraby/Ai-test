from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email import message_from_bytes
import base64
import os

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

TOKEN_FILE = "token.json"


# Get Gmail credentials
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(
        TOKEN_FILE,
        SCOPES
    )
else:
    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json",
        SCOPES
    )

    creds = flow.run_local_server(port=0)

    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())


# Connect to Gmail
service = build("gmail", "v1", credentials=creds)


# Get latest 3 emails
results = service.users().messages().list(
    userId="me",
    maxResults=3
).execute()

messages = results.get("messages", [])

print(f"\nFound {len(messages)} messages.\n")


for i, message in enumerate(messages, 1):

    msg = service.users().messages().get(
        userId="me",
        id=message["id"],
        format="raw"
    ).execute()

    raw_email = base64.urlsafe_b64decode(msg["raw"])

    email = message_from_bytes(raw_email)

    print("=" * 60)
    print(f"EMAIL {i}")

    print("From:", email.get("From"))
    print("Subject:", email.get("Subject"))

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

    print("\nBody:")
    print(body[:3000])
    print()