# LogAnalyzer

로그 파일을 분석하여 통계를 제공하는 프로젝트입니다.

## 프로젝트 구조

```
LogAnalyzer/
├─ src/              # 소스 코드
├─ tests/            # 테스트 코드
├─ docs/             # 문서
├─ .cursor/
│   └─ rules/
│       └─ tdd_vibe_coding.json
├─ .cursorignore
└─ README.md
```

## 요구사항

1. 로그 파일의 전체 줄 수를 계산
2. 각 로그의 레벨(INFO, WARNING, ERROR)을 감지하여 카운트
3. 로그 포맷: `YYYY-MM-DD HH:MM:SS LEVEL: Message`
4. 분석 결과는 딕셔너리 형태로 반환

## 테스트 단위

### 1. 기본 기능 테스트
- `test_empty_file`: 빈 로그 파일 처리
- `test_count_total_lines`: 전체 줄 수 계산
- `test_return_dict_structure`: 반환 딕셔너리 구조 검증

### 2. 로그 레벨 감지 테스트
- `test_count_info_logs`: INFO 레벨 로그 카운트
- `test_count_warning_logs`: WARNING 레벨 로그 카운트
- `test_count_error_logs`: ERROR 레벨 로그 카운트
- `test_count_mixed_logs`: 여러 레벨이 섞인 로그 카운트

### 3. 로그 포맷 검증 테스트
- `test_valid_log_format`: 올바른 포맷 파싱
- `test_invalid_log_format`: 잘못된 포맷 로그 처리
- `test_missing_level`: 레벨이 없는 로그 처리

### 4. 예외 처리 테스트
- `test_file_not_found`: 파일이 존재하지 않을 때 처리
- `test_permission_denied`: 파일 읽기 권한이 없을 때 처리

## 설치 및 실행

```bash
# 테스트 실행
pytest tests/

# 특정 테스트 실행
pytest tests/test_log_analyzer.py::test_count_info_logs
```

## 예상 결과 형식

```python
{
    "total_lines": 100,
    "INFO": 60,
    "WARNING": 30,
    "ERROR": 10
}
```

