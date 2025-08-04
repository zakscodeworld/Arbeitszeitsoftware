import sys
import socket
import time

def wait_for_port(host, port, timeout=30):
    """Wait for a port to be ready."""
    start_time = time.time()
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            if result == 0:
                return True
            if time.time() - start_time >= timeout:
                return False
            time.sleep(1)
        except socket.error:
            if time.time() - start_time >= timeout:
                return False
            time.sleep(1)
        finally:
            sock.close()

def main():
    """Main entry point for the healthcheck script."""
    if len(sys.argv) != 3:
        print("Usage: python healthcheck.py HOST PORT")
        sys.exit(1)

    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except ValueError:
        print(f"Invalid port number: {sys.argv[2]}")
        sys.exit(1)

    if wait_for_port(host, port):
        print(f"Service on {host}:{port} is ready!")
        sys.exit(0)
    else:
        print(f"Service on {host}:{port} did not become ready in time")
        sys.exit(1)

if __name__ == "__main__":
    main()
