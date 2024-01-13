from flask import Flask, request, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Report IP</title>
    <script>
        function convertToLocalTime(utcTime) {
            const utcDate = new Date(utcTime + 'Z');
            return utcDate.toLocaleString();
        }
        function deleteRecord(hostname) {
            if (confirm('Are you sure you want to delete the record for ' + hostname + '?')) {
                window.location.href = '/delete?hostname=' + encodeURIComponent(hostname);
            }
        }
    </script>
</head>
<body>
    <h1>Report IP</h1>
    <table border="1">
        <tr>
            <th>Hostname</th>
            <th>External IP</th>
            <th>Internal IP</th>
            <th>Last Report Time</th>
            <th>Actions</th>
        </tr>
        {% for info in client_info %}
        <tr>
            <td>{{ info[0] }}</td>
            <td>{{ info[1] }}</td>
            <td>{{ info[2] }}</td>
            <td><script>document.write(convertToLocalTime('{{ info[3] }}'));</script></td>
            <td><button onclick="deleteRecord('{{ info[0] }}')">Delete</button></td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# 初始化数据库连接和表
def init_db():
    conn = sqlite3.connect('ip_database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS client_info (
            id INTEGER PRIMARY KEY, 
            hostname TEXT UNIQUE,
            external_ip TEXT, 
            internal_ip TEXT, 
            last_report_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 插入或更新客户端信息到数据库
def upsert_client_info(hostname, external_ip, internal_ip, last_report_time):
    conn = sqlite3.connect('ip_database.db')
    c = conn.cursor()
    # 使用UPSERT语法（SQLite 3.24.0及以上版本）
    c.execute('''
        INSERT INTO client_info (hostname, external_ip, internal_ip, last_report_time) 
        VALUES (?, ?, ?, ?)
        ON CONFLICT(hostname) DO UPDATE SET
        external_ip=excluded.external_ip,
        internal_ip=excluded.internal_ip,
        last_report_time=excluded.last_report_time
    ''', (hostname, external_ip, internal_ip, last_report_time))
    conn.commit()
    conn.close()

# 获取客户端的信息并保存到数据库
@app.route('/report', methods=['GET'])
def report():
    hostname = request.args.get('hostname', '')
    # 尝试获取X-Forwarded-For，如果没有则使用request.remote_addr
    external_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    internal_ip = request.args.get('internal_ip', '')
    last_report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    upsert_client_info(hostname, external_ip, internal_ip, last_report_time)
    return f'Information for {hostname} saved successfully!', 200

# 从数据库中获取并用HTML显示所有客户端信息
@app.route('/', methods=['GET'])
def show():
    conn = sqlite3.connect('ip_database.db')
    c = conn.cursor()
    c.execute('SELECT hostname, external_ip, internal_ip, last_report_time FROM client_info')
    client_info = c.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, client_info=client_info)

@app.route('/delete', methods=['GET'])
def delete():
    hostname = request.args.get('hostname', '')
    if hostname:
        conn = sqlite3.connect('ip_database.db')
        c = conn.cursor()
        c.execute('DELETE FROM client_info WHERE hostname = ?', (hostname,))
        conn.commit()
        conn.close()
        return f'Record for {hostname} deleted successfully!', 200
    else:
        return 'No hostname provided for deletion.', 400


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=6222)
