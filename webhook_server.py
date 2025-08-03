import os
import re
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Get secrets from Environment Variables ---
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

if not CHANNEL_SECRET:
    print("❌ Error: Missing CHANNEL_SECRET environment variable.")
    exit()

# --- LINE Webhook Handler Setup ---
handler = WebhookHandler(CHANNEL_SECRET)


# --- Webhook Endpoint ---
# This is the URL that LINE will send messages to (e.g., https://your-app.onrender.com/callback)
@app.route("/callback", methods=['POST'])
def callback():
    # Get the X-Line-Signature header value for security
    signature = request.headers['X-Line-Signature']
    # Get the request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # Handle the webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel secret.")
        abort(400)
    return 'OK'


# --- Message Event Handler ---
# This function runs when your bot receives a text message
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    message_text = event.message.text
    print(f"Received message from user: {message_text}")
    
    # Use regex to find a 6-digit number in the message
    otp_match = re.search(r'\b\d{6}\b', message_text)
    
    if otp_match:
        otp_code = otp_match.group(0)
        print(f"✅ OTP Found: {otp_code}. Saving to otp.txt")
        # Save the extracted OTP to a file for the main script to read
        with open("otp.txt", "w") as f:
            f.write(otp_code)
    else:
        print("ℹ️ No 6-digit OTP found in the message.")

# This part is for local testing; Gunicorn will run the app in production.
if __name__ == "__main__":
    app.run(port=5000)