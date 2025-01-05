import re
from typing import List
from fastapi import HTTPException
from schemas.rowDTO import RowDTO
import logging

logger = logging.getLogger(__name__)

def parse_apache_log(contents: str) -> List[RowDTO]:
    rows = []
    
    # Updated regex pattern to capture remote_logname, user, and protocol_version
    log_pattern = (r'(?P<ip>\S+) (?P<remote_logname>\S+) (?P<user>\S+) \[(?P<timestamp>.*?)\] '
                   r'"(?P<method>\S+) (?P<url>\S+) HTTP/(?P<protocol_version>\S+)" (?P<status_code>\d+) '
                   r'(?P<response_size>(\d+|-)) "(?P<referrer>.*?)" "(?P<user_agent>.*?)"')

    for line in contents.splitlines():
        match = re.match(log_pattern, line)
        
        if match:
            log_data = match.groupdict()
            
            # Handle status code properly, defaulting to 0 if not found
            if 'status_code' in log_data and log_data['status_code']:
                logger.debug(f"status_code: {log_data['status_code']}")
                status_code = int(log_data['status_code'])
            else:
                status_code = 0  # Default value if status code is not found
            
            # Handle response size, defaulting to 0 if it is "-"
            response_size = int(log_data['response_size']) if log_data['response_size'] != "-" else 0
            
            try:
                # Creating RowDTO object with all the necessary fields
                row_dto = RowDTO(
                    ip=log_data['ip'],
                    timestamp=log_data['timestamp'],
                    method=log_data['method'],
                    url=log_data['url'],
                    status=status_code,
                    response_size=response_size,
                    referer=log_data['referrer'],
                    user_agent=log_data['user_agent'],
                    remote_logname=log_data['remote_logname'],
                    user=log_data['user'],
                    protocol="HTTP/"+log_data['protocol_version']
                )
                rows.append(row_dto)
            except Exception as e:
                logger.warning(f"Skipping invalid log line: {line} due to error: {e}")
        else:
            logger.warning(f"Skipping unparsable log line: {line}")
    
    if not rows:
        raise HTTPException(status_code=400, detail="No valid log entries found in the file.")
    
    return rows

def parse_apache_error_log(contents: str) -> List[RowDTO]:
    rows = []
    
    # Regex pattern to capture Apache error log fields: timestamp, log level, client IP, and error message
    log_pattern = (r'^\[(?P<timestamp>.*?)\] \[(?P<log_level>\S+)\] '
                   r'\[pid \d+:tid \d+\] \[client (?P<ip>\S+):\d+\] (?P<message>.*?)$')

    for line in contents.splitlines():
        match = re.match(log_pattern, line)
        
        if match:
            log_data = match.groupdict()
            
            # Handle default values for missing fields
            log_level = log_data.get('log_level', 'UNKNOWN')
            message = log_data.get('message', 'No message provided')

            try:
                # Creating RowDTO object with all the necessary fields
                row_dto = RowDTO(
                    ip=log_data['ip'],
                    timestamp=log_data['timestamp'],
                    message=message,
                    level=log_level,
                    component="Apache"  # Assuming the source of the log is Apache
                )
                rows.append(row_dto)
            except Exception as e:
                logger.warning(f"Skipping invalid log line: {line} due to error: {e}")
        else:
            logger.warning(f"Skipping unparsable log line: {line}")
    
    if not rows:
        raise Exception("No valid log entries found in the file.")
    
    return rows

def parse_nginx_log(contents: str) -> List[RowDTO]:
    rows = []
    
    # Regex pattern for the default NGINX combined log format
    log_pattern = (r'(?P<ip>\S+) - (?P<remote_user>\S+) \[(?P<timestamp>.*?)\] '
                   r'"(?P<method>\S+) (?P<url>\S+) (?P<protocol>HTTP/\S+)" (?P<status_code>\d+) '
                   r'(?P<response_size>(\d+|-)) "(?P<referer>.*?)" "(?P<user_agent>.*?)"')

    for line in contents.splitlines():
        match = re.match(log_pattern, line)
        
        if match:
            log_data = match.groupdict()
            
            # Handle status code properly, defaulting to 0 if not found
            if 'status_code' in log_data and log_data['status_code']:
                logger.debug(f"status_code: {log_data['status_code']}")
                status_code = int(log_data['status_code'])
            else:
                status_code = 0  # Default value if status code is not found
            
            # Handle response size, defaulting to 0 if it is "-"
            response_size = int(log_data['response_size']) if log_data['response_size'] != "-" else 0
            
            try:
                # Creating RowDTO object with all the necessary fields
                row_dto = RowDTO(
                    ip=log_data['ip'],
                    timestamp=log_data['timestamp'],
                    method=log_data['method'],
                    url=log_data['url'],
                    status=status_code,
                    response_size=response_size,
                    referer=log_data['referer'],
                    user_agent=log_data['user_agent'],
                    protocol=log_data['protocol'],
                    remote_logname=log_data['remote_user']
                )
                rows.append(row_dto)
            except Exception as e:
                logger.warning(f"Skipping invalid log line: {line} due to error: {e}")
        else:
            logger.warning(f"Skipping unparsable log line: {line}")
    
    if not rows:
        raise HTTPException(status_code=400, detail="No valid log entries found in the file.")
    
    return rows

def parse_nginx_error_log(contents: str) -> List[RowDTO]:
    rows = []
    
    # Regex pattern to capture Nginx error log fields: timestamp, log level, PID/TID, client IP, message, request, host, server
    log_pattern = (r'(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) '
                   r'\[(?P<log_level>\S+)\] (?P<pid_tid>\d+#\d+): '
                   r'\*(?P<client_ip>\d+\.\d+\.\d+\.\d+) (?P<message>.*?), '
                   r'client: (?P<client_ip2>\d+\.\d+\.\d+\.\d+), server: (?P<server>\S+), '
                   r'request: "(?P<request>.*?)", host: "(?P<host>.*?)"')

    for line in contents.splitlines():
        match = re.match(log_pattern, line)
        
        if match:
            log_data = match.groupdict()
            
            # Check that the IPs are the same (from client_ip and client_ip2)
            if log_data['client_ip'] != log_data['client_ip2']:
                logger.warning(f"IP mismatch found: {log_data['client_ip']} != {log_data['client_ip2']}")

            try:
                # Creating RowDTO object with all the necessary fields
                row_dto = RowDTO(
                    timestamp=log_data['timestamp'],
                    level=log_data['log_level'],
                    pid_tid=log_data['pid_tid'],
                    ip=log_data['client_ip'],
                    message=log_data['message'],
                    request=log_data['request'],
                    host=log_data['host'],
                    server=log_data['server']
                )
                rows.append(row_dto)
            except Exception as e:
                logger.warning(f"Skipping invalid log line: {line} due to error: {e}")
        else:
            logger.warning(f"Skipping unparsable log line: {line}")
    
    if not rows:
        raise Exception("No valid log entries found in the file.")
    
    return rows