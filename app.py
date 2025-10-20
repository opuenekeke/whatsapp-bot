from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# --- WhatsApp API Credentials ---
VERIFY_TOKEN = "litewaybot"  # same verify token used on Facebook
ACCESS_TOKEN = "EAAV8xZCoaLukBPqIg6XNacZA7nsjaBX2arJ1votPolGPtKBvP6unirusvvRxYFTyLvDKdJ5AlEYAjNSrz58H34JS2MZA0ReLim0ZACVlxUKQyPZAIML5vQqnWARced0BYdeqWXjzMrvQkFZBmSYilsGz6ZA66Jx3NbZAUlUKu3EUrKDyxpj0wYa57hbZCnEGZCvrZAETZA2cCP7Mc2UdbZBW46NQxcoZAmUZCkMsDVriCZCJHXhQL5kZD"

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
            text = message.get("text", {}).get("body", "").strip().lower()

            # Get user's WhatsApp name
            contact_info = data["entry"][0]["changes"][0]["value"].get("contacts", [])
            name = contact_info[0]["profile"]["name"] if contact_info else "there"

            # --- Smart reply section ---
            if text in ["hi", "hello", "hey"]:
                reply = (
                    f"👋 Hello *{name}!* \n\n"
                    "What would you like to do today?\n"
                    "1️⃣ Buy Data\n"
                    "2️⃣ Buy Airtime\n"
                    "3️⃣ Pay Bills\n"
                    "\nPlease reply with the number of your choice."
                )
            else:
                reply = f"You said: {text}"

            # Send message
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
