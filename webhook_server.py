import os
from dotenv import load_dotenv
import re
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

load_dotenv()

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Get secrets from Environment Variables ---
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

# --- LINE Bot API and Webhook Handler Setup ---
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
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
    reply_text = ""
    
    # Try to find a 6-digit number in the user's message
    otp_match = re.search(r'\b\d{6}\b', message_text)
    
    if otp_match:
        otp_code = otp_match.group(0)
        print(f"✅ OTP Found: {otp_code}. Saving to otp.txt")
        with open("otp.txt", "w") as f:
            f.write(otp_code)
        # Set the success reply message
        reply_text = f"Thank you! OTP {otp_code} received."
    else:
        print(f"ℹ️ No 6-digit OTP found in message: '{message_text}'")
        # Set the failure reply message
        reply_text = "That does not look like a 6-digit code. Please try again."

    # Send the reply message back to the user
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )


# This part is for local testing; Gunicorn will run the app in production.
if __name__ == "__main__":
    app.run(port=5000)