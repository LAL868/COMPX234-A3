import socket
import threading
import time

#定义一个字典来表示元组空间，以及一些统计变量
tuple_space = {}
total_clients = 0
total_operations = 0
total_reads = 0
total_gets = 0
total_puts = 0
total_errors = 0

#处理客户端请求的函数，使得函数会在每个线程中运行，处理单个客户端的请求
def handle_client(client_socket, client_address):
    global total_clients, total_operations, total_reads, total_gets, total_puts, total_errors
    total_clients += 1
    try:
        while True:
            request = client_socket.recv(1024).decode('utf - 8')
            if not request:
                break
            # 解析请求消息
            message_length = int(request[:3])
            operation = request[3]
            key = request[4:message_length].split(' ')[0]
            value = request[4:message_length].split(' ')[1] if operation == 'P' else ''

            response = ''
            if operation == 'R':
                total_operations += 1
                total_reads += 1
                if key in tuple_space:
                    response = f"0{len(f'OK ({key}, {tuple_space[key]}) read')} OK ({key}, {tuple_space[key]}) read"
                else:
                    response = f"0{len('ERR k does not exist')} ERR k does not exist"
                    total_errors += 1
            elif operation == 'G':
                total_operations += 1
                total_gets += 1
                if key in tuple_space:
                    value = tuple_space.pop(key)
                    response = f"0{len(f'OK ({key}, {value}) removed')} OK ({key}, {value}) removed"
                else:
                    response = f"0{len('ERR k does not exist')} ERR k does not exist"
                    total_errors += 1
            elif operation == 'P':
                total_operations += 1
                total_puts += 1
                if key in tuple_space:
                    response = f"0{len('ERR k already exists')} ERR k already exists"
                    total_errors += 1
                else:
                    tuple_space[key] = value
                    response = f"0{len(f'OK ({key}, {value}) added')} OK ({key}, {value}) added"

            client_socket.send(response.encode('utf - 8'))
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        client_socket.close()

#用于启动服务器并监听客户端连接。
def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Server is listening on port {port}...")

    def print_stats():
        global total_clients, total_operations, total_reads, total_gets, total_puts, total_errors
        while True:
            time.sleep(10)
            num_tuples = len(tuple_space)
            if num_tuples > 0:
                total_tuple_size = sum(len(key) + len(value) for key, value in tuple_space.items())
                avg_tuple_size = total_tuple_size / num_tuples
                avg_key_size = sum(len(key) for key in tuple_space.keys()) / num_tuples
                avg_value_size = sum(len(value) for value in tuple_space.values()) / num_tuples
            else:
                avg_tuple_size = 0
                avg_key_size = 0
                avg_value_size = 0
            print(f"Tuple Space Stats:")
            print(f"Number of tuples: {num_tuples}")
            print(f"Average tuple size: {avg_tuple_size}")
            print(f"Average key size: {avg_key_size}")
            print(f"Average value size: {avg_value_size}")
            print(f"Total clients: {total_clients}")
            print(f"Total operations: {total_operations}")
            print(f"Total READs: {total_reads}")
            print(f"Total GETs: {total_gets}")
            print(f"Total PUTs: {total_puts}")
            print(f"Total errors: {total_errors}")

    stats_thread = threading.Thread(target = print_stats)
    stats_thread.daemon = True
    stats_thread.start()

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target = handle_client, args = (client_socket, client_address))
        client_thread.start()

#程序的入口，用于获取命令行参数并启动服务器
if __name__ == "__main__":
    import sys
    if len(sys.argv)!= 2:
        print("Usage: python server.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])
    start_server(port)