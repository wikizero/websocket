import os
import json

from datetime import datetime
from flask import Flask, make_response, send_from_directory
from flask import request
# from flask_session import Session
from flask import render_template
from flask_socketio import SocketIO
from db import DBHelper

port = 8001
secret_key = os.urandom(24)  # 生成密钥，为session服务。
print(f'secret_key: {secret_key}')
app = Flask(__name__)
# app.config['SECRET_KEY'] = secret_key  # 配置会话密钥
# app.config['SESSION_TYPE'] = "redis"  # session类型为redis
# app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
# app.config.from_object(__name__)
# Session(app)
socket_io = SocketIO(app)


@app.route("/listen", methods=['post', 'get'])
def listen():
    """"监听发送来的消息,并使用socketio向所有客户端发送消息"""
    mes = {"status": "unknown error"}
    text = request.form.get('data')
    alias = request.form.get('alias')
    file_obj = request.files.get('files')

    if file_obj:
        filename = file_obj.filename
        file_obj.save('static/files/' + filename)
        text = filename

    if text:
        _db = DBHelper()
        _from = request.headers.get('X-Real-Ip') or request.remote_addr
        _type = 'file' if file_obj else 'text'
        _id = _db.insert([alias, _from, _type, text])
        data = _db.select_by_id(_id)
        data['alias'] = data['alias'] or data['id']
        text = data['content']
        data['content'] = text[:40].strip() + '...' if len(text) >= 40 else text
        socket_io.emit(data=json.dumps(data), event="mes")
        mes['status'] = "success"

    print(mes)
    return json.dumps(mes)


@socket_io.on("login")
def login(mes):
    """客户端连接"""
    print(mes)
    sid = request.sid  # io客户端的sid, socketio用此唯一标识客户端.
    can = False
    host = request.host
    print(sid, host)

    host_list = ['127.0.0.1']
    """
    根据页面的访问地址决定是否允许连接, 你可以自己实现自己对访问的控制逻辑.
    最后决定是允许连接还是使用socket_io.server.disconnect(sid)断开链接.
    """
    if host in host_list:
        can = True
    elif host.startswith("192.168") or host.startswith("local"):
        can = True
    else:
        pass
    if can:
        socket_io.emit(event="login", data=json.dumps({"message": "connect refuse!"}))
        socket_io.server.disconnect(sid)
    else:
        socket_io.emit(event="login", data=json.dumps({"message": "connect success!"}))


@app.route("/")
def index():
    """主页面"""
    # TODO 获取前10条
    _db = DBHelper()
    data = _db.select()
    for row in data:
        row['alias'] = row['alias'] or row['id']
        text = row['content']
        row['content'] = text[:40].strip() + '...' if len(text) >= 40 else text
    return render_template("index.html", data=data)


@app.route("/operation", methods=['get', 'POST'])
def operation():
    """operation"""
    if request.method == 'GET':
        _id = request.args.get('id')
        if not _id:
            return {'msg': 'error'}
        _db = DBHelper()
        data = _db.select_by_id(_id)
        filename = data['content']
        response = make_response(send_from_directory('static/files', filename, as_attachment=True))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
        return response

    elif request.method == 'POST':
        _id = request.form.get('id')
        if not _id:
            return {'msg': 'error'}
        _db = DBHelper()
        data = _db.select_by_id(_id)
        return json.dumps({'text': data['content']})


if __name__ == '__main__':
    # TODO 数据库
    # TODO 断开socket 不接受数据   打开再次接收
    socket_io.run(app=app, host="0.0.0.0", port=port, debug=True)
