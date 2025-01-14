import socket
import json
import time

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
    while True:
        print("Enter slicing parameters for exam and simulation")
        exam = input("Exam (true/false): ").lower()
        simulation = input("Simulation (true/false): ").lower()
        
        if exam not in ["true", "false"] or simulation not in ["true", "false"]:
            print("Invalid input")
            print("-------------")
            continue
        
        message = {"exam": exam, "simulation": simulation}
        send_msg(message)
        print("-"* (len(str(message)) + 8))

        time.sleep(1)

