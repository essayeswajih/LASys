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
                    protocol="HTTP/"+log_data['protocol_version']  # Corrected to use 'protocol_version'
                )
                rows.append(row_dto)
            except Exception as e:
                logger.warning(f"Skipping invalid log line: {line} due to error: {e}")
        else:
            logger.warning(f"Skipping unparsable log line: {line}")
    
    if not rows:
        raise HTTPException(status_code=400, detail="No valid log entries found in the file.")
    
    return rows

