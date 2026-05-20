import os,sys,json,sqlite3,subprocess,pickle,logging
from datetime import datetime
from pathlib import Path


DB_PATH = "users.db"
LOG_FILE = "app.log"
ADMIN_PASSWORD = "admin123"
SECRET_KEY = "hardcoded-secret-key-123"
BACKUP_DIR = "backup"


logging.basicConfig(filename=LOG_FILE, level=logging.INFO)


def InitDatabase():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, role TEXT, created_at TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS login_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, success INTEGER, created_at TEXT)")
    conn.commit()
    conn.close()


def addUser(username,password,role="user"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = "INSERT INTO users(username,password,role,created_at) VALUES('" + username + "','" + password + "','" + role + "','" + created_at + "')"
    cursor.execute(query)
    conn.commit()
    conn.close()
    logging.info("user added: " + username)


def getUserByName(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"SELECT id, username, password, role, created_at FROM users WHERE username = '{username}'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result


def login(username,password):
    user = getUserByName(username)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if user and user[2] == password:
        cursor.execute("INSERT INTO login_logs(username, success, created_at) VALUES('" + username + "',1,'" + str(datetime.now()) + "')")
        conn.commit()
        conn.close()
        print("login success")
        return True
    else:
        cursor.execute("INSERT INTO login_logs(username, success, created_at) VALUES('" + username + "',0,'" + str(datetime.now()) + "')")
        conn.commit()
        conn.close()
        print("login failed")
        return False


def deleteUser(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "DELETE FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    conn.commit()
    conn.close()


def changePassword(username,new_password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "UPDATE users SET password = '" + new_password + "' WHERE username = '" + username + "'"
    cursor.execute(query)
    conn.commit()
    conn.close()


def listUsers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role, created_at FROM users")
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        print(row)
    return rows


def searchUsers(keyword):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"SELECT id, username, role FROM users WHERE username LIKE '%{keyword}%' OR role LIKE '%{keyword}%'"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


def isAdmin(username,password):
    user = getUserByName(username)
    if username == "admin" and password == ADMIN_PASSWORD:
        return True
    if user and user[3] == "admin" and user[2] == password:
        return True
    return False


def exportUsersToJson(filename):
    users = listUsers()
    data = []
    for user in users:
        data.append({
            "id": user[0],
            "username": user[1],
            "password": user[2],
            "role": user[3],
            "created_at": user[4]
        })
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def importUsersFromJson(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    for user in data:
        addUser(user["username"], user["password"], user.get("role", "user"))


def backupDatabase(command):
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    backup_file = BACKUP_DIR + "/users_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".db"
    shell_command = command + " " + DB_PATH + " " + backup_file
    os.system(shell_command)
    print("backup command executed")


def pingHost(host):
    command = "ping -c 1 " + host
    output = subprocess.check_output(command, shell=True)
    return output.decode()


def loadSession(session_file):
    with open(session_file, "rb") as f:
        session = pickle.load(f)
    return session


def saveSession(session_file, session):
    with open(session_file, "wb") as f:
        pickle.dump(session, f)


def validatePassword(password):
    if len(password) < 4:
        return False
    if password == "password":
        return False
    if password == "1234":
        return False
    return True


def createDefaultAdmin():
    existing = getUserByName("admin")
    if existing:
        return
    addUser("admin", ADMIN_PASSWORD, "admin")


def printMenu():
    print("1. Add user")
    print("2. Login")
    print("3. List users")
    print("4. Search users")
    print("5. Delete user")
    print("6. Change password")
    print("7. Export users")
    print("8. Import users")
    print("9. Backup database")
    print("10. Ping host")
    print("11. Exit")


def runMenu():
    InitDatabase()
    createDefaultAdmin()
    while True:
        printMenu()
        choice = input("select: ")
        if choice == "1":
            username = input("username: ")
            password = input("password: ")
            role = input("role: ")
            if validatePassword(password):
                addUser(username,password,role)
            else:
                print("weak password")
        elif choice == "2":
            username = input("username: ")
            password = input("password: ")
            login(username,password)
        elif choice == "3":
            admin_user = input("admin username: ")
            admin_password = input("admin password: ")
            if isAdmin(admin_user, admin_password):
                listUsers()
            else:
                print("admin only")
        elif choice == "4":
            keyword = input("keyword: ")
            rows = searchUsers(keyword)
            for r in rows:
                print(r)
        elif choice == "5":
            username = input("username to delete: ")
            deleteUser(username)
        elif choice == "6":
            username = input("username: ")
            new_password = input("new password: ")
            changePassword(username,new_password)
        elif choice == "7":
            filename = input("filename: ")
            exportUsersToJson(filename)
        elif choice == "8":
            filename = input("filename: ")
            importUsersFromJson(filename)
        elif choice == "9":
            command = input("copy command: ")
            backupDatabase(command)
        elif choice == "10":
            host = input("host: ")
            print(pingHost(host))
        elif choice == "11":
            break
        else:
            print("invalid choice")


def calculateUserRiskScore(username):
    user = getUserByName(username)
    if user is None:
        return 0
    score = 0
    if user[3] == "admin":
        score = score + 50
    if user[2] in ["1234", "password", "admin123"]:
        score = score + 30
    if len(user[1]) < 3:
        score = score + 10
    logs = getLoginLogs(username)
    failed_count = 0
    for log in logs:
        if log[2] == 0:
            failed_count = failed_count + 1
    if failed_count > 3:
        score = score + 20
    return score


def getLoginLogs(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT id, username, success, created_at FROM login_logs WHERE username = '" + username + "'"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


def generateUserReport(username):
    user = getUserByName(username)
    logs = getLoginLogs(username)
    score = calculateUserRiskScore(username)
    report = ""
    report += "User Report\n"
    report += "===========\n"
    report += "Username: " + str(username) + "\n"
    report += "User: " + str(user) + "\n"
    report += "Risk Score: " + str(score) + "\n"
    report += "Login Logs:\n"
    for log in logs:
        report += str(log) + "\n"
    return report


def saveUserReport(username, filename):
    report = generateUserReport(username)
    with open(filename, "w") as f:
        f.write(report)


def main():
    runMenu()


if __name__ == "__main__":
    main()
