"""
로그 분석기 테스트 모듈

TDD 방식으로 작성된 테스트 케이스들입니다.
각 테스트는 AAA(Arrange-Act-Assert) 패턴을 따릅니다.
"""

import pytest
import os
import tempfile
from src.log_analyzer import LogAnalyzer


class TestBasicFunctionality:
    """기본 기능 테스트"""
    
    def test_empty_file(self):
        """빈 로그 파일을 처리할 수 있는지 확인"""
        # Arrange: 빈 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_file = f.name
        
        try:
            # Act: 로그 분석 실행
            analyzer = LogAnalyzer(temp_file)
            result = analyzer.analyze()
            
            # Assert: 모든 카운트가 0인지 확인
            assert result["total_lines"] == 0
            assert result["INFO"] == 0
            assert result["WARNING"] == 0
            assert result["ERROR"] == 0
        finally:
            os.unlink(temp_file)
    
    def test_count_total_lines(self):
        """로그 파일의 전체 줄 수를 정확히 계산하는지 확인"""
        # Arrange: 5줄의 로그가 있는 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2024-11-22 10:00:00 INFO: Line 1\n")
            f.write("2024-11-22 10:00:01 INFO: Line 2\n")
            f.write("2024-11-22 10:00:02 INFO: Line 3\n")
            f.write("2024-11-22 10:00:03 INFO: Line 4\n")
            f.write("2024-11-22 10:00:04 INFO: Line 5\n")
            temp_file = f.name
        
        try:
            # Act: 로그 분석 실행
            analyzer = LogAnalyzer(temp_file)
            result = analyzer.analyze()
            
            # Assert: 전체 줄 수가 5인지 확인
            assert result["total_lines"] == 5
        finally:
            os.unlink(temp_file)
    
    def test_return_dict_structure(self):
        """반환 딕셔너리가 올바른 구조를 가지는지 확인"""
        # Arrange: 임의의 로그 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2024-11-22 10:00:00 INFO: Test log\n")
            temp_file = f.name
        
        try:
            # Act: 로그 분석 실행
            analyzer = LogAnalyzer(temp_file)
            result = analyzer.analyze()
            
            # Assert: 필수 키들이 모두 존재하는지 확인
            assert "total_lines" in result
            assert "INFO" in result
            assert "WARNING" in result
            assert "ERROR" in result
            assert isinstance(result["total_lines"], int)
            assert isinstance(result["INFO"], int)
            assert isinstance(result["WARNING"], int)
            assert isinstance(result["ERROR"], int)
        finally:
            os.unlink(temp_file)


class TestLogLevelDetection:
    """로그 레벨 감지 테스트"""
    
    def test_count_info_logs(self):
        """INFO 레벨 로그를 정확히 카운트하는지 확인"""
        # Arrange: INFO 로그 3개가 있는 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2024-11-22 10:00:00 INFO: Application started\n")
            f.write("2024-11-22 10:00:01 INFO: User logged in\n")
            f.write("2024-11-22 10:00:02 INFO: Data loaded\n")
            temp_file = f.name
        
        try:
            # Act: 로그 분석 실행
            analyzer = LogAnalyzer(temp_file)
            result = analyzer.analyze()
            
            # Assert: INFO 카운트가 3인지 확인
            assert result["INFO"] == 3
        finally:
            os.unlink(temp_file)
    
    def test_count_warning_logs(self):
        """WARNING 레벨 로그를 정확히 카운트하는지 확인"""
        # Arrange: WARNING 로그 2개가 있는 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2024-11-22 10:00:00 WARNING: Low memory\n")
            f.write("2024-11-22 10:00:01 WARNING: Slow response\n")
            temp_file = f.name
        
        try:
            # Act: 로그 분석 실행
            analyzer = LogAnalyzer(temp_file)
            result = analyzer.analyze()
            
            # Assert: WARNING 카운트가 2인지 확인
            assert result["WARNING"] == 2
        finally:
            os.unlink(temp_file)
    
    def test_count_error_logs(self):
        """ERROR 레벨 로그를 정확히 카운트하는지 확인"""
        # Arrange: ERROR 로그 4개가 있는 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2024-11-22 10:00:00 ERROR: Database connection failed\n")
            f.write("2024-11-22 10:00:01 ERROR: File not found\n")
            f.write("2024-11-22 10:00:02 ERROR: Network timeout\n")
            f.write("2024-11-22 10:00:03 ERROR: Invalid input\n")
            temp_file = f.name
        
        try:
            # Act: 로그 분석 실행
            analyzer = LogAnalyzer(temp_file)
            result = analyzer.analyze()
            
            # Assert: ERROR 카운트가 4인지 확인
            assert result["ERROR"] == 4
        finally:
            os.unlink(temp_file)
    
    def test_count_mixed_logs(self):
        """여러 레벨이 섞인 로그를 정확히 구분하여 카운트하는지 확인"""
        # Arrange: 여러 레벨의 로그가 섞인 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2024-11-22 10:00:00 INFO: Application started\n")
            f.write("2024-11-22 10:00:01 WARNING: Low memory\n")
            f.write("2024-11-22 10:00:02 ERROR: Database connection failed\n")
            f.write("2024-11-22 10:00:03 INFO: User logged in\n")
            f.write("2024-11-22 10:00:04 WARNING: Slow response\n")
            temp_file = f.name
        
        try:
            # Act: 로그 분석 실행
            analyzer = LogAnalyzer(temp_file)
            result = analyzer.analyze()
            
            # Assert: 각 레벨별 카운트가 정확한지 확인
            assert result["total_lines"] == 5
            assert result["INFO"] == 2
            assert result["WARNING"] == 2
            assert result["ERROR"] == 1
        finally:
            os.unlink(temp_file)


class TestLogFormatValidation:
    """로그 포맷 검증 테스트"""
    
    def test_valid_log_format(self):
        """올바른 포맷을 정확히 파싱하는지 확인"""
        # Arrange: 올바른 포맷의 로그 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2024-11-22 10:00:00 INFO: Valid log message\n")
            f.write("2024-11-22 14:30:45 WARNING: Another valid message\n")
            temp_file = f.name
        
        try:
            # Act: 로그 분석 실행
            analyzer = LogAnalyzer(temp_file)
            result = analyzer.analyze()
            
            # Assert: 모든 로그가 정확히 카운트되었는지 확인
            assert result["INFO"] == 1
            assert result["WARNING"] == 1
            assert result["total_lines"] == 2
        finally:
            os.unlink(temp_file)
    
    def test_invalid_log_format(self):
        """잘못된 포맷의 로그를 적절히 처리하는지 확인"""
        # Arrange: 유효한 로그와 잘못된 포맷의 로그가 섞인 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("Invalid log line without proper format\n")
            f.write("2024-11-22 10:00:00 INFO: Valid log\n")
            f.write("This is also invalid\n")
            temp_file = f.name
        
        try:
            # Act: 로그 분석 실행
            analyzer = LogAnalyzer(temp_file)
            result = analyzer.analyze()
            
            # Assert: 전체 줄 수는 3이지만 유효한 로그만 카운트
            assert result["total_lines"] == 3
            assert result["INFO"] == 1
            assert result["WARNING"] == 0
            assert result["ERROR"] == 0
        finally:
            os.unlink(temp_file)
    
    def test_missing_level(self):
        """레벨이 없는 로그를 적절히 처리하는지 확인"""
        # Arrange: 레벨이 없는 로그가 포함된 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2024-11-22 10:00:00 Some message without level\n")
            f.write("2024-11-22 10:00:01 INFO: Valid message\n")
            temp_file = f.name
        
        try:
            # Act: 로그 분석 실행
            analyzer = LogAnalyzer(temp_file)
            result = analyzer.analyze()
            
            # Assert: 레벨이 없는 로그는 레벨 카운트에 포함되지 않음
            assert result["total_lines"] == 2
            assert result["INFO"] == 1
            assert result["WARNING"] == 0
            assert result["ERROR"] == 0
        finally:
            os.unlink(temp_file)


class TestExceptionHandling:
    """예외 처리 테스트"""
    
    def test_file_not_found(self):
        """존재하지 않는 파일을 처리할 때 적절한 예외를 발생시키는지 확인"""
        # Arrange: 존재하지 않는 파일 경로
        non_existent_file = "non_existent_file.log"
        
        # Act & Assert: FileNotFoundError 예외가 발생하는지 확인
        with pytest.raises(FileNotFoundError):
            analyzer = LogAnalyzer(non_existent_file)
            analyzer.analyze()
    
    def test_permission_denied(self):
        """읽기 권한이 없는 파일을 처리할 때 적절한 예외를 발생시키는지 확인"""
        # Arrange: 읽기 권한이 없는 임시 파일 생성 (Windows에서는 스킵)
        if os.name == 'nt':
            pytest.skip("Permission test not applicable on Windows")
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2024-11-22 10:00:00 INFO: Test\n")
            temp_file = f.name
        
        try:
            # 파일 권한을 000으로 변경 (읽기 불가)
            os.chmod(temp_file, 0o000)
            
            # Act & Assert: PermissionError 예외가 발생하는지 확인
            with pytest.raises(PermissionError):
                analyzer = LogAnalyzer(temp_file)
                analyzer.analyze()
        finally:
            # 권한을 복구하고 파일 삭제
            os.chmod(temp_file, 0o644)
            os.unlink(temp_file)

