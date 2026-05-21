# 코드 리뷰 리포트

## 분석 개요

| 항목 | 내용 |
|---|---|
| 분석 대상 | `user_manager.py` |
| 코드 라인 수 | 304줄 |
| 프로젝트 유형 | Python 기반 사용자 관리 CLI |
| 분석 기준 | PEP8 스타일 규칙, OWASP 보안 기준, Bedrock Knowledge Base RAG 코드 리뷰 흐름 |
| 관련 실습 | Amazon Bedrock 4장 - RAG로 코드 스타일/보안 검사 구현 |
| 생성 파일 | `project_review_report.md` |

본 리포트는 4장 미션의 요구사항인 **Python/JS 프로젝트 코드 200줄 이상 분석**, **스타일 검사**, **보안 검사**, **Markdown 리포트 생성**을 기준으로 작성하였다.

AWS 계정 크레딧 제한으로 Bedrock API를 직접 실행하지는 못했지만, `bedrock_project_review.py`에 RetrieveAndGenerate API 호출 구조를 구현했고, 본 리포트에는 동일한 검사 기준을 적용한 분석 결과를 정리하였다.

---

# 스타일 검사

다음은 `user_manager.py`를 PEP8 및 일반적인 Python 코드 품질 기준으로 점검한 결과이다.

## 네이밍 규칙

- [16] 스타일: `InitDatabase()`는 PascalCase 함수명이다. Python 함수명은 `init_database()`처럼 snake_case로 작성하는 것이 권장된다.
- [24] 스타일: `addUser()`는 `add_user()`로 수정하는 것이 적절하다.
- [34] 스타일: `getUserByName()`는 `get_user_by_name()`으로 변경하는 것이 좋다.
- [63] 스타일: `deleteUser()`는 `delete_user()`로 변경하는 것이 좋다.
- [72] 스타일: `changePassword()`는 `change_password()`로 변경하는 것이 좋다.
- [82] 스타일: `listUsers()`는 `list_users()`로 변경하는 것이 좋다.
- [93] 스타일: `searchUsers()`는 `search_users()`로 변경하는 것이 좋다.
- [104] 스타일: `isAdmin()`은 `is_admin()`으로 변경하는 것이 좋다.

### 수정 예시

```python
def get_user_by_name(username):
    ...
```

---

## import 정리

- [1] 스타일: 여러 모듈을 한 줄에서 import하고 있다.

```python
import os,sys,json,sqlite3,subprocess,pickle,logging
```

- [1] 스타일: `sys`는 현재 코드에서 사용되지 않으므로 제거 가능하다.
- 표준 라이브러리는 한 줄에 하나씩 분리하는 것이 가독성 측면에서 좋다.

### 수정 예시

```python
import json
import logging
import os
import pickle
import sqlite3
import subprocess
from datetime import datetime
```

---

## 공백 및 포맷

- [190] 스타일: `addUser(username,password,role)`에서 쉼표 뒤 공백이 없다.
- [197] 스타일: `login(username,password)`에서 쉼표 뒤 공백이 없다.
- [218] 스타일: `changePassword(username,new_password)`에서 쉼표 뒤 공백이 없다.

### 수정 예시

```python
add_user(username, password, role)
login(username, password)
change_password(username, new_password)
```

---

## 긴 SQL 문자열

- [18], [19], [28], [38] 스타일: SQL 문자열이 한 줄에 길게 작성되어 있다.
- 긴 SQL은 컬럼 추가나 조건 변경 시 실수 가능성이 높아진다.

### 수정 예시

```python
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT,
        created_at TEXT
    )
    """
)
```

---

## 함수 설계 및 복잡도

- [176] 스타일: `runMenu()` 함수가 메뉴 출력, 사용자 입력, 로그인, 관리자 확인, 파일 처리, 네트워크 명령 실행까지 모두 담당한다.
- 하나의 함수가 너무 많은 책임을 가지고 있어 수정 범위가 커지고 테스트가 어려워진다.

### 수정 방향

- `handle_add_user()`
- `handle_login()`
- `handle_admin_list()`
- `handle_backup()`
- `handle_ping()`

처럼 메뉴별 처리 함수를 분리하는 것이 좋다.

---

## 타입 힌트 및 docstring

- [16], [24], [34], [43], [63], [72], [82], [93], [104], [113] 스타일: 주요 함수에 타입 힌트와 docstring이 없다.
- 협업과 유지보수성을 위해 함수의 입력과 반환값을 명확히 표현하는 것이 좋다.

### 수정 예시

```python
def login(username: str, password: str) -> bool:
    """사용자 이름과 비밀번호를 검증해 로그인 성공 여부를 반환한다."""
```

---

# 보안 검사

분석 결과, 해당 코드는 웹 애플리케이션은 아니므로 XSS 위험은 낮다.  
하지만 데이터베이스, OS 명령어, 파일 역직렬화, 비밀번호 저장 로직에서 중요한 보안 취약점이 발견되었다.

---

## 🔴 심각도: 높음

## 1. SQL Injection

- 위치: `addUser()`, `getUserByName()`, `deleteUser()`, `changePassword()`, `searchUsers()`, `getLoginLogs()`
- 유형: SQL Injection
- 설명: 사용자 입력값을 SQL 문자열에 직접 연결하고 있다. 공격자가 특수한 입력값을 전달하면 인증 우회, 데이터 조회, 삭제 등이 가능해질 수 있다.
- 수정 제안: SQLite 파라미터 바인딩을 사용해야 한다.

### 취약 코드 예시

```python
query = f"SELECT id, username, password, role, created_at FROM users WHERE username = '{username}'"
```

```python
query = "DELETE FROM users WHERE username = '" + username + "'"
```

### 수정 예시

```python
cursor.execute(
    "SELECT id, username, password, role, created_at FROM users WHERE username = ?",
    (username,)
)
```

---

## 2. 평문 비밀번호 저장

- 위치: `addUser()`, `login()`, `exportUsersToJson()`
- 유형: 민감정보 보호 미흡
- 설명: 비밀번호가 해싱 없이 DB에 저장되고, JSON export 시에도 그대로 포함된다.
- 영향: DB 파일이나 export 파일이 유출되면 모든 사용자 비밀번호가 노출된다.

### 수정 예시

```python
import bcrypt

password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
```

---

## 3. 하드코딩된 관리자 비밀번호와 Secret

- 위치: 전역 변수 영역
- 유형: Hardcoded Secret
- 설명: 관리자 비밀번호와 Secret Key가 코드에 직접 포함되어 있다.

```python
ADMIN_PASSWORD = "admin123"
SECRET_KEY = "hardcoded-secret-key-123"
```

GitHub에 업로드될 경우 민감 정보가 그대로 노출될 수 있다.

### 수정 예시

```python
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")
```

---

## 4. Command Injection

- 위치: `backupDatabase()`, `pingHost()`
- 유형: OS Command Injection
- 설명: 사용자 입력값이 OS 명령어 문자열에 직접 연결된다.

### 취약 코드 예시

```python
shell_command = command + " " + DB_PATH + " " + backup_file
os.system(shell_command)
```

```python
output = subprocess.check_output(command, shell=True)
```

### 수정 예시

```python
subprocess.check_output(["ping", "-c", "1", host])
```

DB 백업은 OS 명령어 대신 `shutil.copy2()`를 사용하는 것이 안전하다.

---

## 🟠 심각도: 중간

## 5. 안전하지 않은 역직렬화

- 위치: `loadSession()`
- 유형: Insecure Deserialization
- 설명: `pickle.load()`는 신뢰할 수 없는 파일을 읽을 때 임의 코드 실행 위험이 있다.

### 취약 코드

```python
session = pickle.load(f)
```

### 수정 예시

```python
with open(session_file, "r", encoding="utf-8") as f:
    session = json.load(f)
```

---

## 6. 사용자 목록 조회 시 비밀번호 노출

- 위치: `listUsers()`, `exportUsersToJson()`
- 유형: Sensitive Data Exposure
- 설명: 사용자 목록 조회와 JSON export에서 비밀번호 컬럼이 포함된다.

### 취약 코드

```python
cursor.execute("SELECT id, username, password, role, created_at FROM users")
```

### 수정 예시

```python
cursor.execute("SELECT id, username, role, created_at FROM users")
```

---

## 7. 입력값 검증 부족

- 위치: `importUsersFromJson()`, `backupDatabase()`, `pingHost()`
- 유형: Insufficient Input Validation
- 설명: 파일명, 명령어, host 입력값에 대한 검증이 부족하다.
- 영향: 잘못된 파일 접근, 명령어 삽입, 예외 발생 가능성이 있다.

### 수정 예시

```python
import re

def is_safe_hostname(host: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9.-]+$", host))
```

---

## 🟡 심각도: 낮음

## 8. 예외 처리 부족

- 위치: DB 연결, 파일 처리, JSON 파싱, subprocess 실행 구간
- 유형: Error Handling
- 설명: DB 오류, 파일 없음, JSON 파싱 실패, 명령 실행 실패 시 프로그램이 중단될 수 있다.
- 수정 제안: `try-except`와 로깅을 추가해 장애 원인을 확인할 수 있게 해야 한다.

---

# 요청 항목 결론

| 취약점 유형 | 존재 여부 | 심각도 | 비고 |
|---|---:|---|---|
| SQL Injection | ✅ 있음 | 높음 | SQL 문자열 직접 조립 |
| XSS | ❌ 없음 | - | 웹 화면 미사용 |
| 하드코딩된 비밀번호/Secret | ✅ 있음 | 높음 | 전역 상수 사용 |
| 평문 비밀번호 저장 | ✅ 있음 | 높음 | 해싱 미적용 |
| Command Injection | ✅ 있음 | 높음 | `os.system`, `shell=True` |
| 안전하지 않은 역직렬화 | ✅ 있음 | 중간 | `pickle.load()` |
| 입력값 검증 부족 | ✅ 있음 | 중간 | 파일명/host 검증 부족 |
| 민감정보 노출 | ✅ 있음 | 중간 | 비밀번호 조회/export |
| 예외 처리 부족 | ✅ 있음 | 낮음 | 장애 추적 어려움 |

---

# 최우선 개선 코드 예시

아래는 SQL Injection과 평문 비밀번호 저장 문제를 함께 줄이는 개선 예시이다.

```python
import sqlite3
import bcrypt
from datetime import datetime

DB_PATH = "users.db"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def add_user(username: str, password: str, role: str = "user") -> None:
    password_hash = hash_password(password)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users(username, password, role, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (username, password_hash, role, created_at),
        )
        conn.commit()
```

---

# 개선 우선순위

1. 모든 SQL 쿼리를 파라미터 바인딩으로 변경
2. 비밀번호 해싱 적용
3. 하드코딩된 관리자 비밀번호와 Secret 제거
4. `os.system()` 및 `shell=True` 제거
5. `pickle` 기반 세션 로드 제거
6. 사용자 조회/export에서 비밀번호 제외
7. 함수명 snake_case로 정리
8. `runMenu()` 함수 분리
9. 입력값 검증 추가
10. 예외 처리 및 로깅 보강

---

# 최종 평가

`user_manager.py`는 300줄 이상의 Python 코드로, 사용자 관리 기능을 구현하고 있어 4장 미션의 분석 대상 조건을 충족한다.

다만 데이터베이스 쿼리와 사용자 입력 처리 방식에서 보안 취약점이 많이 발견되었다. 가장 우선적으로 해결해야 할 문제는 SQL Injection, 평문 비밀번호 저장, 하드코딩된 Secret, Command Injection이다.

스타일 측면에서는 함수명 규칙, import 정리, 함수 책임 분리, 타입 힌트 추가가 필요하다.

Bedrock Knowledge Base 기반 RAG 코드 리뷰 구조를 실제 프로젝트에 적용하면, PEP8과 OWASP 같은 외부 규칙 문서를 기반으로 코드 리뷰 품질을 일관되게 유지할 수 있다. 또한 GitHub PR과 연동하면 코드가 병합되기 전에 스타일과 보안 문제를 자동으로 점검할 수 있을 것이다.
