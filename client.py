import socket
import sys

#用于向服务器发送请求并接收响应
def send_request(server_host, server_port, request):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))
    client_socket.send(request.encode('utf - 8'))
    response = client_socket.recv(1024).decode('utf - 8')
    client_socket.close()
    return response

#客户端程序的入口，用于读取请求文件并依次发送请求
if __name__ == "__main__":
    if len(sys.argv)!= 4:
        print("Usage: python client.py <server_host> <server_port> <request_file>")
        sys.exit(1)
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    request_file = sys.argv[3]

    with open(request_file, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            operation = line.split(' ')[0]
            key = line.split(' ')[1]
            value = line.split(' ')[2] if operation == 'PUT' else ''
            message_length = len(line) + 3
            request = f"{message_length:03d}{operation}{key} {value}" if operation == 'PUT' else f"{message_length:03d}{operation}{key}"
            response = send_request(server_host, server_port, request)
            print(f"{line}: {response}")

