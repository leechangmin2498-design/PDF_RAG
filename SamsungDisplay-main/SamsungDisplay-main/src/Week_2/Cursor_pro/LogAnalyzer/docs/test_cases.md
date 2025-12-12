# 테스트 케이스 명세

## 1. 기본 기능 테스트

### test_empty_file
- **목적**: 빈 로그 파일을 처리할 수 있는지 확인
- **입력**: 빈 파일
- **예상 결과**: 
  ```python
  {
      "total_lines": 0,
      "INFO": 0,
      "WARNING": 0,
      "ERROR": 0
  }
  ```

### test_count_total_lines
- **목적**: 로그 파일의 전체 줄 수를 정확히 계산하는지 확인
- **입력**: 5줄의 로그가 있는 파일
- **예상 결과**: `total_lines` 키의 값이 5

### test_return_dict_structure
- **목적**: 반환 딕셔너리가 올바른 구조를 가지는지 확인
- **입력**: 임의의 로그 파일
- **예상 결과**: 딕셔너리에 `total_lines`, `INFO`, `WARNING`, `ERROR` 키가 모두 존재

## 2. 로그 레벨 감지 테스트

### test_count_info_logs
- **목적**: INFO 레벨 로그를 정확히 카운트하는지 확인
- **입력**:
  ```
  2024-11-22 10:00:00 INFO: Application started
  2024-11-22 10:00:01 INFO: User logged in
  2024-11-22 10:00:02 INFO: Data loaded
  ```
- **예상 결과**: `INFO` 키의 값이 3

### test_count_warning_logs
- **목적**: WARNING 레벨 로그를 정확히 카운트하는지 확인
- **입력**:
  ```
  2024-11-22 10:00:00 WARNING: Low memory
  2024-11-22 10:00:01 WARNING: Slow response
  ```
- **예상 결과**: `WARNING` 키의 값이 2

### test_count_error_logs
- **목적**: ERROR 레벨 로그를 정확히 카운트하는지 확인
- **입력**:
  ```
  2024-11-22 10:00:00 ERROR: Database connection failed
  2024-11-22 10:00:01 ERROR: File not found
  2024-11-22 10:00:02 ERROR: Network timeout
  2024-11-22 10:00:03 ERROR: Invalid input
  ```
- **예상 결과**: `ERROR` 키의 값이 4

### test_count_mixed_logs
- **목적**: 여러 레벨이 섞인 로그를 정확히 구분하여 카운트하는지 확인
- **입력**:
  ```
  2024-11-22 10:00:00 INFO: Application started
  2024-11-22 10:00:01 WARNING: Low memory
  2024-11-22 10:00:02 ERROR: Database connection failed
  2024-11-22 10:00:03 INFO: User logged in
  2024-11-22 10:00:04 WARNING: Slow response
  ```
- **예상 결과**: 
  ```python
  {
      "total_lines": 5,
      "INFO": 2,
      "WARNING": 2,
      "ERROR": 1
  }
  ```

## 3. 로그 포맷 검증 테스트

### test_valid_log_format
- **목적**: 올바른 포맷("YYYY-MM-DD HH:MM:SS LEVEL: Message")을 정확히 파싱하는지 확인
- **입력**:
  ```
  2024-11-22 10:00:00 INFO: Valid log message
  2024-11-22 14:30:45 WARNING: Another valid message
  ```
- **예상 결과**: 모든 로그가 정확히 파싱되고 카운트됨

### test_invalid_log_format
- **목적**: 잘못된 포맷의 로그를 적절히 처리하는지 확인
- **입력**:
  ```
  Invalid log line without proper format
  2024-11-22 10:00:00 INFO: Valid log
  This is also invalid
  ```
- **예상 결과**: 
  - 유효한 로그만 카운트
  - `total_lines`는 3 (모든 줄 포함)
  - `INFO`는 1 (유효한 로그만)

### test_missing_level
- **목적**: 레벨이 없는 로그를 적절히 처리하는지 확인
- **입력**:
  ```
  2024-11-22 10:00:00 Some message without level
  2024-11-22 10:00:01 INFO: Valid message
  ```
- **예상 결과**: 레벨이 없는 로그는 INFO, WARNING, ERROR 카운트에 포함되지 않음

## 4. 예외 처리 테스트

### test_file_not_found
- **목적**: 존재하지 않는 파일을 처리할 때 적절한 예외를 발생시키는지 확인
- **입력**: 존재하지 않는 파일 경로
- **예상 결과**: `FileNotFoundError` 예외 발생

### test_permission_denied
- **목적**: 읽기 권한이 없는 파일을 처리할 때 적절한 예외를 발생시키는지 확인
- **입력**: 읽기 권한이 없는 파일 경로
- **예상 결과**: `PermissionError` 예외 발생

## 테스트 우선순위

1. **Phase 1** (핵심 기능):
   - test_count_total_lines
   - test_count_info_logs
   - test_count_warning_logs
   - test_count_error_logs
   - test_return_dict_structure

2. **Phase 2** (통합 테스트):
   - test_count_mixed_logs
   - test_valid_log_format

3. **Phase 3** (엣지 케이스):
   - test_empty_file
   - test_invalid_log_format
   - test_missing_level

4. **Phase 4** (예외 처리):
   - test_file_not_found
   - test_permission_denied

