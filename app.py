import os
from datetime import datetime
from flask import Flask
from flask import request
# from flask_session import Session
from flask import render_template
from flask_socketio import SocketIO
import json

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
    data = request.form.get('data')
    print(data)
    if data:
        res = {
            'ip': request.headers.get('X-Real-Ip') or request.remote_addr,
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'text',
            'content': data
        }
        print(res)
        socket_io.emit(data=json.dumps(res), event="mes")
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
    return render_template("index.html")


if __name__ == '__main__':
    # TODO 数据库
    # TODO 断开socket 不接受数据   打开再次接收
    socket_io.run(app=app, host="0.0.0.0", port=port, debug=True)
