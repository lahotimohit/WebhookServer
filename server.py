import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

WEBHOOK_VERIFY_TOKEN = "dummy_token" 
GRAPH_API_TOKEN = "EAAL7og371v4BOyYzIOptdIiqCdVJU2xd62NaGoWAELDNCqPdoIPmL6kQ225LF7dY8cZBqAS59j4QTqiNMfqHMEOreLr3uGDvKkMr3iLYTQl8Kt8DbeZAjw95McRFmIFVO13J64wRzWZAs8cZBHYJmKxQ85zizmcTW6lza5N67RFaml1XVpPA0qEh5XoUukoePJjJK4a1z8xcrmaeSvgZD"
PORT = 3000

@app.route('/webhook', methods=['POST'])
def webhook():
    body = request.json
    print("Incoming webhook message:", json.dumps(body, indent=2))

    message = body.get('entry', [])[0].get('changes', [])[0].get('value', {}).get('messages', [])[0]

    if message and message.get('type') == 'text':
        business_phone_number_id = body['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']
        
        response_message = {
            "messaging_product": "whatsapp",
            "to": message['from'],
            "text": {"body": "Echo: " + message['text']['body']},
            "context": {"message_id": message['id']}
        }

        headers = {
            "Authorization": f"Bearer {GRAPH_API_TOKEN}",
            "Content-Type": "application/json"
        }

        # Send reply
        requests.post(f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages", 
                      headers=headers, 
                      data=json.dumps(response_message))

        # Mark message as read
        read_receipt = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message['id']
        }
        
        requests.post(f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages",
                      headers=headers, 
                      data=json.dumps(read_receipt))

    return jsonify({'status': 'success'})

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        return challenge
    else:
        return "Forbidden", 403

@app.route('/')
def home():
    return "<pre>Nothing to see here.\nCheckout README.md to start.</pre>"

if __name__ == '__main__':
    app.run(port=PORT)
