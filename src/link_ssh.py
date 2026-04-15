from PySide6.QtCore import QObject, QThread, Signal, Slot
import paramiko
import logging
import threading
import socket

# 配置日志（可选，用于调试）
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


class SSHWorker(QObject):
    """SSH 后台工作器（处理连接、命令执行，通过信号返回结果）"""
    # 信号定义：连接状态、命令输出、错误信息
    connected = Signal(str)          # 连接成功（参数：服务器地址）
    disconnected = Signal(str)       # 断开连接（参数：服务器地址）
    command_result = Signal(str)     # 命令执行结果（参数：输出内容）
    error_occurred = Signal(str)     # 错误信息（参数：错误描述）

    def __init__(self, host: str = "", port: int = 22, username: str = "", password: str = ""):
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh_client = None
        self._is_connected = False
        self.forward_thread = None
        self.remote_vllm_port = 8000  # 服务器上 vLLM 端口（8000）
        self.local_port = 8000    # 本地映射端口（8000）
        self.listener_socket = None       # 本地监听套接字
        self.remote_vllm_host = "localhost"
        self.is_running = False           # 转发状态标记

    @property
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._is_connected

    def connect(self) -> None:
        """建立 SSH 连接（需在子线程中调用）"""
        try:
            if self._is_connected:
                self.error_occurred.emit(f"已连接到 {self.host}，无需重复连接")
                return

            # 初始化 SSH 客户端
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动接受未知主机密钥

            # 连接服务器
            self.ssh_client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10  # 连接超时时间（秒）
            )

            self._is_connected = True
            self.connected.emit(f"成功连接到 {self.host}:{self.port}")
            logging.info(f"SSH 连接成功：{self.host}:{self.port}")

            # 2. 启动本地端口监听（用于转发）
            self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listener_socket.bind(("localhost", self.local_port))  # 监听本地端口
            self.listener_socket.listen(5)  # 允许最多5个排队连接
            logging.info(
                f"本地端口转发启动：localhost:{self.local_port} -> {self.remote_vllm_host}:{self.remote_vllm_port}")

            # 3. 启动转发线程（循环接受本地连接）
            self.is_running = True
            self.forward_thread = threading.Thread(target=self._forward_loop, daemon=True)
            self.forward_thread.start()
        except Exception as e:
            self._is_connected = False
            error_msg = f"连接失败：{str(e)}"
            self.error_occurred.emit(error_msg)
            logging.error(error_msg)

    def execute_command(self, command: str) -> None:
        """执行 SSH 命令（需先连接）"""
        if not self._is_connected or not self.ssh_client:
            self.error_occurred.emit("未建立 SSH 连接，请先连接服务器")
            return

        try:
            # 执行命令
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=30)
            # 读取输出（stdout 是命令正常输出，stderr 是错误输出）
            output = stdout.read().decode("utf-8", errors="replace")
            error = stderr.read().decode("utf-8", errors="replace")

            # 整合结果
            result = f"命令: {command}\n"
            if output:
                result += f"输出:\n{output}\n"
            if error:
                result += f"错误:\n{error}\n"

            self.command_result.emit(result)
            logging.info(f"命令执行完成：{command}")

        except Exception as e:
            error_msg = f"命令执行失败：{str(e)}"
            self.error_occurred.emit(error_msg)
            logging.error(error_msg)

    def disconnect(self) -> None:
        """断开 SSH 连接"""
        if self._is_connected and self.ssh_client:
            try:
                self.ssh_client.close()
                self._is_connected = False
                self.disconnected.emit(f"已断开与 {self.host} 的连接")
                logging.info(f"SSH 连接已断开：{self.host}:{self.port}")
            except Exception as e:
                self.error_occurred.emit(f"断开连接失败：{str(e)}")

    def _forward_loop(self):
        """循环接受本地连接，并转发到远程vLLM端口"""
        while self.is_running:
            try:
                # 接受本地客户端的连接（如本地代码访问localhost:8000）
                local_socket, local_addr = self.listener_socket.accept()
                logging.info(f"接收到本地连接：{local_addr}")

                # 通过SSH创建到远程vLLM的通道
                remote_channel = self.ssh_client.get_transport().open_channel(
                    "direct-tcpip",
                    (self.remote_vllm_host, self.remote_vllm_port),
                    local_addr
                )

                # 启动双向数据转发线程
                threading.Thread(
                    target=self._forward_data,
                    args=(local_socket, remote_channel),
                    daemon=True
                ).start()
                threading.Thread(
                    target=self._forward_data,
                    args=(remote_channel, local_socket),
                    daemon=True
                ).start()

            except Exception as e:
                if self.is_running:  # 非主动停止时才报错
                    logging.error(f"转发循环错误：{str(e)}")

    def _forward_data(self, source, destination):
        """在两个套接字之间转发数据（双向）"""
        try:
            while self.is_running:
                data = source.recv(4096)  # 一次读取4KB数据
                if not data:
                    break  # 连接关闭
                destination.sendall(data)  # 转发数据
        except Exception as e:
            logging.debug(f"数据转发错误：{str(e)}")  # 调试级日志，避免频繁报错
        finally:
            # 关闭连接
            source.close()
            destination.close()


class SSHManager(QObject):
    """SSH 管理器（负责线程管理，对外提供接口）"""
    def __init__(self):
        super().__init__()
        self.worker:SSHWorker = SSHWorker()
        self.thread:QThread = QThread()

    def start_ssh(self, host: str, port: int = 22, username: str = "", password: str = "") -> None:
        """启动 SSH 后台连接（创建线程和工作器）"""
        # 停止已有连接
        if self.thread and self.thread.isRunning():
            self.stop_ssh()

        # 创建子线程和工作器
        if self.thread is None:
            self.thread = QThread()
        if self.thread is None:
            self.worker = SSHWorker(host, port, username, password)
        else:
            self.worker.host = host
            self.worker.port = port
            self.worker.username = username
            self.worker.password = password
        self.worker.moveToThread(self.thread)

        # 连接线程信号（线程启动时执行连接）
        self.thread.started.connect(self.worker.connect)
        # 线程结束时清理资源
        self.worker.disconnected.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # 启动线程
        self.thread.start()

    def execute(self, command: str) -> None:
        """执行命令（通过工作器）"""
        if self.worker and self.worker.is_connected:
            self.worker.execute_command(command)
        else:
            logging.error("无法执行命令：未建立 SSH 连接")

    def stop_ssh(self) -> None:
        """停止 SSH 连接并清理线程"""
        if self.worker and self.worker.is_connected:
            self.worker.disconnect()
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()  # 等待线程结束
        self.worker = None
        self.thread = None


# ------------------------------
# 使用示例（可集成到你的 PySide6 项目中）
# ------------------------------
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    # 初始化应用（PySide6 必须有 QApplication 实例）
    app = QApplication(sys.argv)

    # 创建 SSH 管理器
    ssh_manager = SSHManager()

    # 绑定信号处理函数（根据需要自定义）
    def on_connected(msg: str):
        # print(f"[连接成功] {msg}")
        # 连接成功后执行命令示例
        ssh_manager.execute("ls -la")  # 查看目录
        ssh_manager.execute("echo 'Hello from SSH'")  # 打印文本

    def on_disconnected(msg: str):
        # print(f"[断开连接] {msg}")
        pass
    def on_result(msg: str):
        # print(f"[命令结果]\n{msg}")
        pass
    def on_error(msg: str):
        # print(f"[错误] {msg}")
        pass
    # 连接信号（根据需要选择绑定）
    ssh_manager.worker.connected.connect(on_connected)
    ssh_manager.worker.disconnected.connect(on_disconnected)
    ssh_manager.worker.command_result.connect(on_result)
    ssh_manager.worker.error_occurred.connect(on_error)

    # 启动 SSH 连接（替换为你的服务器信息）
    ssh_manager.start_ssh(
        host="proxy.cn-south-1.gpu-instance.ppinfra.com",  # 服务器 IP
        port=59759,               # SSH 端口
        username="root",  # 用户名
        password="L3xdxliJKnoTcVfTeUHd"   # 密码
    )

    # 运行应用（阻塞等待，实际项目中可集成到现有事件循环）
    sys.exit(app.exec())