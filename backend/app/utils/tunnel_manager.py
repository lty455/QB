import threading
import select
import socketserver
import paramiko
import time
import socket

# ================= SSH 隧道配置 =================
SSH_HOST = "connect.bjb1.seetacloud.com"  # 你的 AutoDL 地址
SSH_PORT = 10041  # 你的 AutoDL SSH 端口 (整数)
SSH_USER = "root"
SSH_PASS = "S9SQ6dNTiCWH"  # 你的 AutoDL 密码

LOCAL_PORT = 8000  # 本地监听端口
REMOTE_HOST = "127.0.0.1"  # 远端服务器（AutoDL）上 vLLM 监听的地址
REMOTE_PORT = 8000  # 远端服务器（AutoDL）上 vLLM 的端口


# ===============================================

class ForwardServer(socketserver.ThreadingTCPServer):
    """
    一个支持多线程的 TCP 服务器，用于接收本地请求
    """
    daemon_threads = True
    allow_reuse_address = True


class Handler(socketserver.BaseRequestHandler):
    """
    处理本地连接的 Handler，负责将本地 Socket 的数据搬运到 SSH Channel 中
    """

    def handle(self):
        try:
            # 通过全局的 paramiko SSH 客户端，请求建立一条到远端目标端口的直连通道
            channel = ssh_client.get_transport().open_channel(
                "direct-tcpip",
                (REMOTE_HOST, REMOTE_PORT),
                self.request.getpeername()
            )
        except Exception as e:
            print(f"⚠️ [隧道错误] 无法建立到远端的通道: {e}")
            return

        if channel is None:
            print(f"⚠️ [隧道错误] 远端 {REMOTE_HOST}:{REMOTE_PORT} 拒绝了连接请求。")
            return

        # 双向数据搬运 (本地 Socket <--> 远端 SSH Channel)
        while True:
            # 使用 select 监听哪一端有数据可读
            r, w, x = select.select([self.request, channel], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                channel.send(data)
            if channel in r:
                data = channel.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        channel.close()
        self.request.close()


# 全局的 SSH 客户端实例
ssh_client = None
tunnel_thread = None


def check_local_port_in_use(port):
    """检查本地端口是否已被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def _start_tunnel_server():
    """在后台线程中启动本地 TCP 监听服务"""
    try:
        server = ForwardServer(('', LOCAL_PORT), Handler)
        server.serve_forever()
    except OSError as e:
        print(f"❌ [隧道错误] 本地端口 {LOCAL_PORT} 启动失败: {e}")


def start_ssh_tunnel():
    """
    主入口：建立 Paramiko SSH 连接，并在后台启动端口转发服务
    """
    global ssh_client, tunnel_thread

    print(f"🚀 准备建立到 {SSH_HOST}:{SSH_PORT} 的 SSH 隧道...")

    # 1. 检查本地端口是否冲突
    if check_local_port_in_use(LOCAL_PORT):
        print(f"⚠️ 警告：本地端口 {LOCAL_PORT} 已被占用！请先清理占用该端口的进程。")
        print("如果这是你之前启动的旧隧道，请重启 Python 进程。")
        return False

    # 2. 初始化 Paramiko 客户端
    ssh_client = paramiko.SSHClient()
    # 自动接受未知的主机密钥 (等同于 StrictHostKeyChecking=no)
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 3. 建立 SSH 连接
        ssh_client.connect(
            hostname=SSH_HOST,
            port=SSH_PORT,
            username=SSH_USER,
            password=SSH_PASS,
            timeout=10,  # 设置超时防止卡死
            # 下面两个参数有助于保持长连接不掉线
            banner_timeout=30,
            auth_timeout=30
        )

        # 开启 Keepalive 机制，每 30 秒发一次心跳，防止 AutoDL 防火墙掐断空闲连接
        transport = ssh_client.get_transport()
        transport.set_keepalive(30)

        print("✅ SSH 认证成功！")

        # 4. 在后台线程启动端口转发服务
        tunnel_thread = threading.Thread(target=_start_tunnel_server, daemon=True)
        tunnel_thread.start()

        # 给服务一点时间启动
        time.sleep(1)

        print(f"🔗 Paramiko 隧道已就绪: 本地 127.0.0.1:{LOCAL_PORT} ===> 远程 {REMOTE_HOST}:{REMOTE_PORT}")
        return True

    except paramiko.AuthenticationException:
        print("❌ [隧道错误] SSH 密码错误或被拒绝！")
        return False
    except paramiko.SSHException as e:
        print(f"❌ [隧道错误] SSH 连接异常: {e}")
        return False
    except Exception as e:
        print(f"❌ [隧道错误] 发生未知错误: {e}")
        return False


def stop_ssh_tunnel():
    """
    关闭 SSH 连接 (通常在主程序退出时调用)
    """
    global ssh_client
    if ssh_client:
        print("🛑 正在关闭 SSH 隧道...")
        ssh_client.close()
        ssh_client = None