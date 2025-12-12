"""
로그 분석기 모듈

로그 파일을 분석하여 통계 정보를 제공합니다.
"""

import re
from typing import Dict, List


class LogAnalyzer:
    """로그 파일을 분석하는 클래스"""
    
    # 지원하는 로그 레벨
    LOG_LEVELS = ('INFO', 'WARNING', 'ERROR')
    
    # 로그 포맷 정규식 패턴: YYYY-MM-DD HH:MM:SS LEVEL: Message
    LOG_PATTERN = re.compile(
        r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} (INFO|WARNING|ERROR):'
    )
    
    # 파일 인코딩
    FILE_ENCODING = 'utf-8'
    
    def __init__(self, log_file_path: str):
        """
        LogAnalyzer 초기화
        
        Args:
            log_file_path: 분석할 로그 파일 경로
        """
        self.log_file_path = log_file_path
    
    def analyze(self) -> Dict[str, int]:
        """
        로그 파일을 분석하여 통계를 반환
        
        Returns:
            dict: 로그 분석 결과
                - total_lines: 전체 줄 수
                - INFO: INFO 레벨 로그 개수
                - WARNING: WARNING 레벨 로그 개수
                - ERROR: ERROR 레벨 로그 개수
        
        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            PermissionError: 파일 읽기 권한이 없을 때
        """
        lines = self._read_log_file()
        level_counts = self._count_log_levels(lines)
        
        return self._build_result(len(lines), level_counts)
    
    def _read_log_file(self) -> List[str]:
        """
        로그 파일을 읽어서 줄 단위 리스트로 반환
        
        Returns:
            List[str]: 로그 파일의 각 줄
            
        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            PermissionError: 파일 읽기 권한이 없을 때
        """
        try:
            with open(self.log_file_path, 'r', encoding=self.FILE_ENCODING) as f:
                return f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {self.log_file_path}")
        except PermissionError:
            raise PermissionError(f"파일을 읽을 권한이 없습니다: {self.log_file_path}")
    
    def _count_log_levels(self, lines: List[str]) -> Dict[str, int]:
        """
        로그 라인들에서 각 레벨별 개수를 카운트
        
        Args:
            lines: 로그 파일의 각 줄
            
        Returns:
            Dict[str, int]: 각 로그 레벨별 개수
        """
        level_counts = {level: 0 for level in self.LOG_LEVELS}
        
        for line in lines:
            level = self._extract_log_level(line)
            if level:
                level_counts[level] += 1
        
        return level_counts
    
    def _extract_log_level(self, line: str) -> str:
        """
        로그 라인에서 레벨을 추출
        
        Args:
            line: 로그 라인
            
        Returns:
            str: 로그 레벨 (INFO, WARNING, ERROR) 또는 None
        """
        match = self.LOG_PATTERN.match(line)
        return match.group(1) if match else None
    
    def _build_result(self, total_lines: int, level_counts: Dict[str, int]) -> Dict[str, int]:
        """
        분석 결과 딕셔너리 생성
        
        Args:
            total_lines: 전체 줄 수
            level_counts: 각 로그 레벨별 개수
            
        Returns:
            Dict[str, int]: 분석 결과
        """
        return {
            "total_lines": total_lines,
            **level_counts
        }

