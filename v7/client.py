import socket
import json
import sys

# Establish a connection
def send_msg(msg):
    HOST = "127.0.0.1"
    PORT = 9999
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            client_socket.sendall(json.dumps(message).encode('utf-8'))  # Send the message
            print(f"Sent: {message}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    user_input = sys.argv
    exam = user_input[1]
    simulation = user_input[2]

    message = {"exam": exam, "simulation": simulation}
    send_msg(message)

