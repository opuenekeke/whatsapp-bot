from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# --- WhatsApp API Credentials ---
VERIFY_TOKEN = "litewaybot"  # same verify token used on Facebook
ACCESS_TOKEN = "EAAP8aDUKLqMBPpUhajH05oSDD5559K1VRuillmSK5SeqOFp4gkyBVF2G9ggQ2wdg9wZCElZAUShbYNjZAIf1JDg2wZCJEM4Ya5dD47ZAkF35r6ifx0VIBXDCOX74qlOhdNMLPhR9qSZC27zmm5mnW3lm2NNw0rhce2g6Rl6iEAZCthlJ8ZAH1WYCDsY2RvIZBHG64cbgt2kvgRjovZCHvt7iJkNNRDFC25vnpgnnlZBqXnB8QZDZD"

@app.route('/', methods=['GET'])
def home():
    return "WhatsApp Bot is live!", 200


# --- Webhook verification (GET request) ---
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully!")
        return challenge, 200
    else:
        return "Verification failed", 403


# --- Handle incoming messages (POST request) ---
@app.route('/webhook', methods=['POST'])
def handle_message():
    data = request.get_json()
    print("Incoming data:", data)

    try:
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender = message["from"]
            text = message.get("text", {}).get("body", "")

            # --- Send a reply ---
            reply = f"You said: {text}"
            send_message(sender, reply)

    except Exception as e:
        print("Error:", e)

    return jsonify(success=True), 200


# --- Function to send message back to user ---
def send_message(to, message):
    url = "https://graph.facebook.com/v22.0/823077057555789/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Response:", response.text)


# --- Run the Flask app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
