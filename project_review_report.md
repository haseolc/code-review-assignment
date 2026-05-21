# 코드 리뷰 리포트

## 검사 대상

- 파일명: `user_manager.py`
- 총 라인 수: 304줄

---

# 스타일 검사 결과

## 1. 함수명 네이밍 규칙

**문제점:**  
`InitDatabase`, `addUser`, `getUserByName`, `deleteUser`, `changePassword`, `listUsers` 등 일부 함수명이 Python에서 권장하는 `snake_case` 형식을 따르지 않습니다.

**이유:**  
PEP8에서는 함수명과 변수명을 소문자 기반의 `snake_case`로 작성하는 것을 권장합니다. 현재 코드처럼 CamelCase와 snake_case가 섞이면 코드 스타일의 일관성이 떨어집니다.

**개선 방법:**

```python
def init_database():
    ...

def add_user(username, password, role="user"):
    ...

def get_user_by_name(username):
    ...
```

---

## 2. Import 정리 문제

**문제점:**  
파일 첫 줄에서 여러 모듈을 한 줄에 import하고 있습니다.

```python
import os,sys,json,sqlite3,subprocess,pickle,logging
```

**이유:**  
여러 모듈을 한 줄에 작성하면 사용 여부를 파악하기 어렵고, 가독성이 떨어집니다. 또한 `sys`는 현재 코드에서 사용되지 않습니다.

**개선 방법:**

```python
import json
import logging
import os
import pickle
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
```

---

## 3. 공백 및 포맷 문제

**문제점:**  
일부 함수 호출에서 쉼표 뒤 공백이 빠져 있습니다.

```python
addUser(username,password,role)
login(username,password)
changePassword(username,new_password)
```

**이유:**  
PEP8에서는 함수 인자 사이의 쉼표 뒤에 공백을 넣어 가독성을 높이는 것을 권장합니다.

**개선 방법:**

```python
add_user(username, password, role)
login(username, password)
change_password(username, new_password)
```

---

## 4. 긴 SQL 문자열

**문제점:**  
테이블 생성 및 SQL 실행문이 한 줄에 길게 작성되어 있습니다.

```python
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, role TEXT, created_at TEXT)")
```

**이유:**  
SQL문이 길어질수록 컬럼 구조를 확인하기 어렵고, 수정 시 실수가 발생하기 쉽습니다.

**개선 방법:**

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

## 5. 함수 책임 과다

**문제점:**  
`runMenu()` 함수가 메뉴 출력, 사용자 입력 처리, 로그인, 관리자 검증, 파일 처리, 백업, 네트워크 명령 실행까지 모두 담당하고 있습니다.

**이유:**  
하나의 함수가 너무 많은 역할을 가지면 유지보수가 어려워지고, 특정 기능만 테스트하기도 어려워집니다.

**개선 방법:**  
메뉴별 처리 함수를 분리합니다.

```python
def handle_add_user():
    ...

def handle_login():
    ...

def handle_backup():
    ...
```

---

## 6. 타입 힌트 및 docstring 부족

**문제점:**  
대부분의 함수에 타입 힌트와 docstring이 없습니다.

**이유:**  
타입 힌트와 docstring이 없으면 함수의 입력값과 반환값을 빠르게 이해하기 어렵습니다. 특히 여러 명이 함께 코드를 볼 때 유지보수성이 떨어집니다.

**개선 방법:**

```python
def login(username: str, password: str) -> bool:
    """사용자 이름과 비밀번호를 검증하여 로그인 성공 여부를 반환한다."""
    ...
```

---

# 보안 검사 결과

## 🔴 [위험도: 높음] SQL Injection 취약점

**문제점:**  
사용자 입력값이 SQL 쿼리 문자열에 직접 삽입되고 있습니다.

```python
query = f"SELECT id, username, password, role, created_at FROM users WHERE username = '{username}'"
```

```python
query = "DELETE FROM users WHERE username = '" + username + "'"
```

**원인:**  
외부 입력값을 검증하거나 분리하지 않고 SQL 문자열에 직접 연결하면, 공격자가 특수한 문자열을 입력하여 의도하지 않은 쿼리를 실행할 수 있습니다.

**개선 방법:**  
SQLite의 파라미터 바인딩을 사용합니다.

```python
cursor.execute(
    "SELECT id, username, password, role, created_at FROM users WHERE username = ?",
    (username,)
)
```

```python
cursor.execute(
    "DELETE FROM users WHERE username = ?",
    (username,)
)
```

---

## 🔴 [위험도: 높음] 평문 비밀번호 저장

**문제점:**  
사용자 비밀번호가 해싱 없이 그대로 저장됩니다.

```python
query = "INSERT INTO users(username,password,role,created_at) VALUES(...)"
```

또한 사용자 목록 조회와 JSON export 과정에서도 비밀번호가 노출될 수 있습니다.

**원인:**  
비밀번호를 암호학적으로 보호하지 않고 문자열 그대로 저장하면 DB 파일이 유출되었을 때 모든 계정 정보가 노출됩니다.

**개선 방법:**  
`bcrypt`와 같은 해시 알고리즘을 사용합니다.

```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())
```

---

## 🔴 [위험도: 높음] 하드코딩된 관리자 비밀번호와 Secret

**문제점:**  
관리자 비밀번호와 Secret Key가 코드에 직접 작성되어 있습니다.

```python
ADMIN_PASSWORD = "admin123"
SECRET_KEY = "hardcoded-secret-key-123"
```

**원인:**  
민감정보를 코드에 직접 작성하면 GitHub 업로드 시 그대로 노출됩니다.

**개선 방법:**  
환경 변수 또는 Secret Manager를 사용합니다.

```python
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")
```

---

## 🔴 [위험도: 높음] Command Injection 취약점

**문제점:**  
사용자 입력값이 OS 명령어에 직접 연결되어 실행됩니다.

```python
shell_command = command + " " + DB_PATH + " " + backup_file
os.system(shell_command)
```

```python
command = "ping -c 1 " + host
output = subprocess.check_output(command, shell=True)
```

**원인:**  
`os.system()`이나 `shell=True`는 외부 입력이 포함될 경우 의도하지 않은 명령어 실행으로 이어질 수 있습니다.

**개선 방법:**  
`shell=True`를 제거하고, 명령어 인자를 리스트로 전달합니다.

```python
subprocess.check_output(["ping", "-c", "1", host])
```

DB 백업은 OS 명령어보다 Python 표준 라이브러리 사용이 안전합니다.

```python
import shutil

shutil.copy2(DB_PATH, backup_file)
```

---

## 🟠 [위험도: 중간] 안전하지 않은 역직렬화

**문제점:**  
세션 파일을 `pickle.load()`로 불러오고 있습니다.

```python
session = pickle.load(f)
```

**원인:**  
pickle은 신뢰할 수 없는 파일을 로드할 경우 임의 코드 실행 위험이 있습니다.

**개선 방법:**  
세션 저장에는 JSON처럼 안전한 포맷을 사용합니다.

```python
with open(session_file, "r", encoding="utf-8") as f:
    session = json.load(f)
```

---

## 🟠 [위험도: 중간] 민감정보 출력 가능성

**문제점:**  
사용자 목록 조회 시 비밀번호 컬럼까지 함께 조회합니다.

```python
cursor.execute("SELECT id, username, password, role, created_at FROM users")
```

**원인:**  
관리자 기능이라 하더라도 비밀번호를 화면이나 파일에 직접 노출하는 것은 안전하지 않습니다.

**개선 방법:**  
조회 대상에서 비밀번호 컬럼을 제외합니다.

```python
cursor.execute("SELECT id, username, role, created_at FROM users")
```

---

## 🟠 [위험도: 중간] 입력값 검증 부족

**문제점:**  
파일명, host, command 입력값에 대한 검증이 부족합니다.

**원인:**  
사용자 입력값이 파일 처리나 명령어 실행에 바로 사용되면 비정상 입력으로 인해 오류나 보안 문제가 발생할 수 있습니다.

**개선 방법:**  
허용 가능한 입력 패턴만 통과시키는 검증 로직을 추가합니다.

```python
import re

def is_safe_hostname(host: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9.-]+$", host))
```

---

## 🟡 [위험도: 낮음] 예외 처리 부족

**문제점:**  
DB 연결, 파일 처리, JSON 파싱, subprocess 실행 구간에 예외 처리가 부족합니다.

**원인:**  
파일이 없거나 DB 오류가 발생하면 프로그램이 갑자기 중단될 수 있습니다.

**개선 방법:**

```python
try:
    ...
except sqlite3.Error as e:
    logging.error("database error: %s", e)
except FileNotFoundError:
    logging.error("file not found")
```

---

# 검사 항목 결론

| 취약점 유형 | 존재 여부 | 비고 |
|---|---:|---|
| SQL Injection | ✅ 있음 | SQL 문자열 직접 조립 |
| XSS | ❌ 없음 | 웹 화면 미사용 |
| 하드코딩된 비밀번호/Secret | ✅ 있음 | 전역 상수 사용 |
| 평문 비밀번호 저장 | ✅ 있음 | 해싱 미적용 |
| Command Injection | ✅ 있음 | `os.system`, `shell=True` |
| 안전하지 않은 역직렬화 | ✅ 있음 | `pickle.load()` |
| 입력값 검증 부족 | ✅ 있음 | 파일명/host 검증 부족 |
| 민감정보 노출 | ✅ 있음 | 비밀번호 조회/export |
| 예외 처리 부족 | ✅ 있음 | 장애 추적 어려움 |

---

# 종합 평가

`user_manager.py`는 사용자 등록, 로그인, 조회, 백업 기능을 포함한 Python CLI 프로그램이며, 총 304줄로 과제의 200줄 이상 분석 조건을 충족합니다.

스타일 측면에서는 함수명 규칙, import 정리, 공백 사용, 함수 책임 분리, 타입 힌트 보강이 필요합니다.

보안 측면에서는 SQL Injection, 평문 비밀번호 저장, 하드코딩된 Secret, Command Injection이 가장 우선적으로 개선되어야 합니다. 이후 pickle 사용 제거, 비밀번호 출력 제한, 입력값 검증, 예외 처리 보강을 적용하면 코드의 안정성과 유지보수성을 높일 수 있습니다.
