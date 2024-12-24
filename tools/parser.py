import re
from typing import List
from fastapi import HTTPException
from schemas.rowDTO import RowDTO
import logging
logger = logging.getLogger(__name__)

def parse_apache_log(contents: str) -> List[RowDTO]:
    rows = []
    log_pattern = r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>.*?)\] "(?P<method>\S+) (?P<url>\S+) HTTP/\S+" (?P<status_code>\d+) (?P<response_size>(\d+|-)) "(?P<referrer>.*?)" "(?P<user_agent>.*?)"'
    
    for line in contents.splitlines():
        match = re.match(log_pattern, line)
        if match:
            log_data = match.groupdict()
            try:
                row_dto = RowDTO(
                    ip=log_data['ip'],
                    timestamp=log_data['timestamp'],
                    method=log_data['method'],
                    url=log_data['url'],
                    status_code=int(log_data['status_code']),
                    response_size=int(log_data['response_size']) if log_data['response_size'] != "-" else 0,
                    referrer=log_data['referrer'],
                    user_agent=log_data['user_agent']
                )
                rows.append(row_dto)
            except Exception as e:
                logger.warning(f"Skipping invalid log line: {line} due to error: {e}")
        else:
            logger.warning(f"Skipping unparsable log line: {line}")
    
    if not rows:
        raise HTTPException(status_code=400, detail="No valid log entries found in the file.")
    
    return rows