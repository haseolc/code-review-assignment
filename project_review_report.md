# 코드 리뷰 리포트

## 1. 프로젝트 개요

본 리포트는 Amazon Bedrock Generative AI 실무 4장 미션인 **“자신의 프로젝트 코드 200줄 검사”**를 기준으로 작성한 코드 리뷰 결과이다.

분석 대상 프로젝트는 Python 기반의 간단한 사용자 관리 CLI 프로그램이다. 주요 기능은 사용자 등록, 로그인, 사용자 목록 조회, 사용자 검색, 비밀번호 변경, 데이터 백업, 세션 저장, 사용자 리포트 생성이다.

| 항목 | 내용 |
|---|---|
| 프로젝트명 | User Manager CLI |
| 분석 대상 파일 | `user_manager.py` |
| 언어 | Python |
| 코드 라인 수 | 약 260줄 |
| 검사 항목 | 스타일 검사, 보안 취약점 검사 |
| 리포트 파일 | `project_review_report.md` |

---

## 2. 분석 기준

수업 자료의 4장 미션 기준에 따라 다음 항목을 중심으로 분석했다.

1. **스타일 검사**
   - PEP8 네이밍 규칙
   - import 정리
   - 공백 및 줄 길이
   - 함수 분리 여부
   - 코드 가독성

2. **보안 검사**
   - SQL Injection
   - 하드코딩된 비밀번호 및 Secret Key
   - Command Injection
   - 안전하지 않은 역직렬화
   - 민감정보 노출
   - 예외 처리 부족

3. **개선 방향**
   - 파라미터 바인딩 적용
   - 비밀번호 해싱
   - 환경 변수 사용
   - subprocess 안전 호출
   - pickle 사용 제거
   - 함수명 및 구조 개선

---

## 3. 분석 대상 코드 요약

분석 대상 파일은 `user_manager.py`이다. SQLite를 사용하여 사용자 정보를 저장하고, CLI 메뉴를 통해 사용자를 관리한다.

주요 함수는 다음과 같다.

| 함수명 | 역할 |
|---|---|
| `InitDatabase()` | SQLite 테이블 생성 |
| `addUser()` | 사용자 등록 |
| `getUserByName()` | 사용자 조회 |
| `login()` | 로그인 처리 |
| `deleteUser()` | 사용자 삭제 |
| `changePassword()` | 비밀번호 변경 |
| `listUsers()` | 사용자 목록 조회 |
| `searchUsers()` | 사용자 검색 |
| `backupDatabase()` | DB 백업 |
| `pingHost()` | 호스트 ping 실행 |
| `loadSession()` | 세션 파일 로드 |
| `generateUserReport()` | 사용자 리포트 생성 |

---

## 4. 스타일 검사 결과

### 4.1 함수명 네이밍 규칙 위반

PEP8에서는 함수명에 `snake_case` 사용을 권장한다. 그러나 분석 대상 코드에는 `InitDatabase`, `addUser`, `getUserByName`, `deleteUser`, `changePassword`, `listUsers` 등 CamelCase 또는 혼합 형태의 함수명이 사용되었다.

| 위치 | 문제 유형 | 설명 | 개선 방향 |
|---|---|---|---|
| 12행 | 함수명 스타일 | `InitDatabase()`는 PEP8 함수명 규칙에 맞지 않음 | `init_database()` |
| 21행 | 함수명 스타일 | `addUser()`는 snake_case가 아님 | `add_user()` |
| 31행 | 함수명 스타일 | `getUserByName()`는 snake_case가 아님 | `get_user_by_name()` |
| 59행 | 함수명 스타일 | `deleteUser()`는 snake_case가 아님 | `delete_user()` |
| 68행 | 함수명 스타일 | `changePassword()`는 snake_case가 아님 | `change_password()` |
| 78행 | 함수명 스타일 | `listUsers()`는 snake_case가 아님 | `list_users()` |

### 4.2 import 정리 문제

1행에서 여러 라이브러리를 한 줄에 import하고 있다.

```python
import os,sys,json,sqlite3,subprocess,pickle,logging
```

PEP8에서는 일반적으로 import를 한 줄에 하나씩 작성하는 것이 좋다.

개선 예시는 다음과 같다.

```python
import json
import logging
import os
import pickle
import sqlite3
import subprocess
import sys
```

또한 `sys`는 실제 코드에서 사용되지 않으므로 제거하는 것이 적절하다.

### 4.3 공백 스타일 문제

일부 함수 호출에서 쉼표 뒤 공백이 없다.

```python
addUser(username,password,role)
login(username,password)
changePassword(username,new_password)
```

개선 예시는 다음과 같다.

```python
add_user(username, password, role)
login(username, password)
change_password(username, new_password)
```

### 4.4 긴 SQL 문자열

13행과 14행의 테이블 생성 SQL은 한 줄이 지나치게 길다. 긴 문자열은 가독성을 떨어뜨리고 유지보수를 어렵게 만든다.

개선 예시는 다음과 같다.

```python
cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT,
        created_at TEXT
    )
    '''
)
```

### 4.5 함수 책임 과다

`runMenu()` 함수는 메뉴 출력, 입력 처리, 인증, 사용자 관리, 백업, 네트워크 명령 실행까지 모두 처리한다. 하나의 함수가 너무 많은 책임을 가지므로 유지보수가 어렵다.

개선 방향은 다음과 같다.

- 메뉴 출력 함수 분리
- 사용자 등록 처리 함수 분리
- 로그인 처리 함수 분리
- 관리자 기능 처리 함수 분리
- 백업 및 ping 기능 분리

---

## 5. 보안 취약점 검사 결과

## 5.1 SQL Injection 취약점

가장 심각한 문제는 사용자 입력값을 SQL 문자열에 직접 연결하는 방식이다.

### 발견 위치

```python
query = f"SELECT id, username, password, role, created_at FROM users WHERE username = '{username}'"
```

```python
query = "DELETE FROM users WHERE username = '" + username + "'"
```

```python
query = "UPDATE users SET password = '" + new_password + "' WHERE username = '" + username + "'"
```

### 위험도

| 항목 | 내용 |
|---|---|
| 취약점 유형 | SQL Injection |
| 심각도 | CRITICAL |
| 영향 | 인증 우회, 사용자 정보 유출, 데이터 삭제 가능 |
| 원인 | 사용자 입력값을 SQL 쿼리에 직접 삽입 |

### 공격 예시

사용자가 다음 값을 입력할 경우 의도하지 않은 SQL이 실행될 수 있다.

```text
' OR '1'='1
```

### 개선 코드

```python
cursor.execute(
    "SELECT id, username, password, role, created_at FROM users WHERE username = ?",
    (username,)
)
```

삭제와 수정도 동일하게 파라미터 바인딩을 사용해야 한다.

```python
cursor.execute(
    "DELETE FROM users WHERE username = ?",
    (username,)
)
```

```python
cursor.execute(
    "UPDATE users SET password = ? WHERE username = ?",
    (new_password, username)
)
```

---

## 5.2 평문 비밀번호 저장

사용자 비밀번호가 해싱 없이 그대로 DB에 저장된다.

### 발견 위치

```python
query = "INSERT INTO users(username,password,role,created_at) VALUES(...)"
```

```python
if user and user[2] == password:
```

### 위험도

| 항목 | 내용 |
|---|---|
| 취약점 유형 | Plaintext Password Storage |
| 심각도 | CRITICAL |
| 영향 | DB 유출 시 모든 사용자 비밀번호 노출 |
| 개선 방향 | bcrypt 또는 hashlib 기반 해시 적용 |

### 개선 코드 예시

```python
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode(), password_hash.encode())
```

---

## 5.3 하드코딩된 관리자 비밀번호 및 Secret Key

코드 상단에 관리자 비밀번호와 Secret Key가 하드코딩되어 있다.

```python
ADMIN_PASSWORD = "admin123"
SECRET_KEY = "hardcoded-secret-key-123"
```

### 위험도

| 항목 | 내용 |
|---|---|
| 취약점 유형 | Hardcoded Secret |
| 심각도 | HIGH |
| 영향 | GitHub 업로드 시 비밀정보 노출 |
| 개선 방향 | `.env` 또는 AWS Secrets Manager 사용 |

### 개선 코드 예시

```python
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")
```

---

## 5.4 Command Injection 취약점

`backupDatabase()` 함수와 `pingHost()` 함수에서 사용자 입력을 OS 명령어로 직접 실행한다.

### 발견 위치

```python
shell_command = command + " " + DB_PATH + " " + backup_file
os.system(shell_command)
```

```python
command = "ping -c 1 " + host
output = subprocess.check_output(command, shell=True)
```

### 위험도

| 항목 | 내용 |
|---|---|
| 취약점 유형 | Command Injection |
| 심각도 | HIGH |
| 영향 | 임의 명령 실행 가능 |
| 원인 | 사용자 입력을 shell 명령에 직접 연결 |
| 개선 방향 | shell=True 제거, 리스트 인자 사용 |

### 개선 코드 예시

```python
import shutil

def backup_database():
    backup_file = Path(BACKUP_DIR) / f"users_{datetime.now():%Y%m%d%H%M%S}.db"
    shutil.copy2(DB_PATH, backup_file)
```

`ping` 기능은 다음처럼 작성할 수 있다.

```python
def ping_host(host):
    output = subprocess.check_output(["ping", "-c", "1", host])
    return output.decode()
```

---

## 5.5 안전하지 않은 역직렬화

`pickle.load()`는 신뢰할 수 없는 파일에 대해 사용할 경우 원격 코드 실행 위험이 있다.

### 발견 위치

```python
session = pickle.load(f)
```

### 위험도

| 항목 | 내용 |
|---|---|
| 취약점 유형 | Insecure Deserialization |
| 심각도 | HIGH |
| 영향 | 악성 pickle 파일 로드 시 임의 코드 실행 가능 |
| 개선 방향 | JSON 등 안전한 포맷 사용 |

### 개선 코드 예시

```python
def load_session(session_file):
    with open(session_file, "r", encoding="utf-8") as f:
        return json.load(f)
```

---

## 5.6 사용자 목록 조회 시 비밀번호 출력

`listUsers()` 함수는 사용자 목록을 출력할 때 비밀번호까지 출력한다.

```python
cursor.execute("SELECT id, username, password, role, created_at FROM users")
```

### 위험도

| 항목 | 내용 |
|---|---|
| 취약점 유형 | Sensitive Data Exposure |
| 심각도 | MEDIUM |
| 영향 | 관리자 화면 또는 로그에서 비밀번호 노출 |
| 개선 방향 | 비밀번호 컬럼 제외 |

### 개선 코드 예시

```python
cursor.execute("SELECT id, username, role, created_at FROM users")
```

---

## 5.7 예외 처리 부족

DB 연결, 파일 입출력, JSON 파싱, 명령 실행 과정에서 예외 처리가 부족하다. 파일이 없거나 DB가 잠겨 있거나 외부 명령이 실패하면 프로그램이 중단될 수 있다.

개선 방향은 다음과 같다.

```python
try:
    ...
except sqlite3.Error as e:
    logging.error("database error: %s", e)
except FileNotFoundError:
    logging.error("file not found")
```

---

## 6. 종합 취약점 요약

| 번호 | 취약점 | 위치 | 심각도 | 개선 우선순위 |
|---|---|---|---|---|
| 1 | SQL Injection | `addUser`, `getUserByName`, `deleteUser`, `changePassword`, `searchUsers` | CRITICAL | 1순위 |
| 2 | 평문 비밀번호 저장 | `addUser`, `login` | CRITICAL | 1순위 |
| 3 | 하드코딩된 Secret | 전역 변수 | HIGH | 2순위 |
| 4 | Command Injection | `backupDatabase`, `pingHost` | HIGH | 2순위 |
| 5 | Insecure Deserialization | `loadSession` | HIGH | 2순위 |
| 6 | 비밀번호 출력 | `listUsers`, `exportUsersToJson` | MEDIUM | 3순위 |
| 7 | 예외 처리 부족 | 전체 코드 | MEDIUM | 3순위 |

---

## 7. 개선 코드 예시

아래는 핵심 취약점인 SQL Injection과 평문 비밀번호 저장 문제를 개선한 예시이다.

```python
import os
import sqlite3
import bcrypt
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "users.db")


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def add_user(username, password, role="user"):
    password_hash = hash_password(password)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO users(username, password, role, created_at)
            VALUES (?, ?, ?, ?)
            ''',
            (username, password_hash, role, created_at)
        )
        conn.commit()


def get_user_by_name(username):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT id, username, password, role, created_at
            FROM users
            WHERE username = ?
            ''',
            (username,)
        )
        return cursor.fetchone()
```

---

## 8. 최종 평가

분석 대상 코드는 사용자 관리 기능을 구현하고 있지만, 보안 측면에서는 개선이 매우 필요하다. 특히 사용자 입력을 SQL 쿼리에 직접 삽입하는 방식은 SQL Injection으로 이어질 수 있으며, 비밀번호를 평문으로 저장하는 구조는 실제 서비스 환경에서 매우 위험하다.

스타일 측면에서는 함수명 네이밍 규칙, import 정리, 공백 사용, 긴 함수 분리 등이 필요하다. 특히 `runMenu()` 함수는 하나의 함수가 너무 많은 책임을 가지고 있어 기능별 함수로 분리해야 한다.

---

## 9. 개선 우선순위

1. SQL 쿼리 전부 파라미터 바인딩으로 변경
2. 비밀번호 해싱 적용
3. 하드코딩된 비밀번호와 Secret Key 제거
4. `os.system`, `shell=True` 제거
5. `pickle` 대신 JSON 사용
6. 비밀번호 컬럼 출력 제거
7. 함수명 PEP8 기준으로 수정
8. `runMenu()` 함수 분리
9. 예외 처리 및 로깅 보강
10. 테스트 코드 추가

---

## 10. 느낀 점

이번 미션을 통해 단순히 코드가 실행되는 것과 안전하고 유지보수 가능한 코드를 작성하는 것은 다르다는 점을 확인했다. 특히 사용자 입력을 처리하는 부분에서는 SQL Injection, Command Injection과 같은 취약점이 쉽게 발생할 수 있기 때문에 입력값 검증과 안전한 API 사용이 중요하다.

또한 RAG 기반 코드 리뷰 방식은 일반적인 LLM 코드 분석보다 더 실무적인 장점이 있다. PEP8, OWASP Top 10, 회사 내부 스타일 가이드처럼 외부 문서를 Knowledge Base에 저장하고 검색 결과를 바탕으로 리뷰하면, 최신 규칙과 조직별 기준을 반영한 코드 검사가 가능하다.

따라서 실제 프로젝트에 적용한다면 GitHub PR이 생성될 때 자동으로 코드 스타일과 보안 취약점을 검사하고, Markdown 리포트를 생성하거나 PR 코멘트로 남기는 방식으로 확장할 수 있을 것이다.

---

## 11. 제출 정보

| 항목 | 내용 |
|---|---|
| 제출 파일 | `project_review_report.md` |
| 분석 코드 | `user_manager.py` |
| 제출 방식 | GitHub Repository 업로드 후 링크 공유 |
| 과제 기준 | Python/JS 프로젝트 코드 200줄 이상 검사 |
