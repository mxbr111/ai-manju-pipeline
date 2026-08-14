#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
comfy_ssh_client.py — AutoDL 云端 ComfyUI 统一 SSH 客户端（脱敏版）

凭据从环境变量读取（绝不硬编码）:
  AUTODL_HOST   e.g. connect.<region>.seetacloud.com（在 AutoDL 实例页获取）
  AUTODL_PORT   e.g. 17699（实例页获取，每次开机可能轮换）
  AUTODL_USER   default: root
  AUTODL_PASS   SSH 密码

用法:
  export AUTODL_HOST=connect.<region>.seetacloud.com
  export AUTODL_PORT=17699
  export AUTODL_PASS=xxxxx
  python comfy_ssh_client.py --exec "curl -s http://127.0.0.1:6006/system_stats"

也提供 Python API: ComfyClient 封装了 提交工作流 / 轮询历史 / 下载文件。
"""
import os, sys, json, time, argparse

HOST = os.environ.get("AUTODL_HOST", "")
PORT = int(os.environ.get("AUTODL_PORT", "0"))
USER = os.environ.get("AUTODL_USER", "root")
PASS = os.environ.get("AUTODL_PASS", "")
COMFY_PORT = int(os.environ.get("COMFY_PORT", "6006"))


class ComfyClient:
    """AutoDL 实例上 ComfyUI 的 SSH 封装: 提交 prompt -> 轮询 /history -> SFTP 下载"""

    def __init__(self, host=HOST, port=PORT, user=USER, password=PASS):
        if not host or not port:
            raise RuntimeError("需要设置环境变量 AUTODL_HOST / AUTODL_PORT / AUTODL_PASS")
        import paramiko
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(host, port=port, username=user, password=password, timeout=30)
        self.ssh.get_transport().set_keepalive(30)

    def run(self, cmd, timeout=60):
        """在实例上执行命令，返回 stdout"""
        s, o, e = self.ssh.exec_command(cmd, timeout=timeout)
        return o.read().decode("utf-8", "ignore")

    def get_workflow(self, remote_path):
        """读取云端工作流 JSON"""
        return json.loads(self.run(f"cat {remote_path}"))

    def submit(self, workflow, client_id="hermes_batch"):
        """提交工作流到 ComfyUI API，返回 prompt_id"""
        payload = json.dumps({"prompt": workflow, "client_id": client_id}, ensure_ascii=False)
        out = self.run(
            f"curl -s -X POST http://127.0.0.1:{COMFY_PORT}/prompt "
            f"-H 'Content-Type: application/json' -d '{payload}'"
        )
        try:
            return json.loads(out).get("prompt_id"), out
        except Exception:
            return None, out

    def wait_done(self, prompt_id, timeout=1200, poll=15):
        """轮询 /history/{id} 直到 completed 或 error"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(poll)
            hist = self.run(f"curl -s http://127.0.0.1:{COMFY_PORT}/history/{prompt_id}")
            try:
                d = json.loads(hist)
                if prompt_id in d:
                    st = d[prompt_id].get("status", {})
                    if st.get("completed"):
                        return d[prompt_id]
                    if st.get("status_str") == "error":
                        return {"error": json.dumps(st, ensure_ascii=False)[:800]}
            except Exception:
                pass
        return {"error": f"timeout after {timeout}s"}

    def download(self, remote_path, local_path):
        """SFTP 下载文件"""
        sftp = self.ssh.open_sftp()
        try:
            sftp.get(remote_path, local_path)
        finally:
            sftp.close()

    def list_output(self, prefix):
        """列出云端输出目录匹配文件"""
        return self.run(f"ls /root/ComfyUI/output/{prefix}* 2>/dev/null | tail -5").strip()

    def close(self):
        self.ssh.close()


def main():
    ap = argparse.ArgumentParser(description="AutoDL ComfyUI SSH 客户端")
    ap.add_argument("--exec", help="在实例上执行任意命令")
    args = ap.parse_args()
    if not args.exec:
        ap.print_help()
        sys.exit(1)
    c = ComfyClient()
    print(c.run(args.exec))
    c.close()


if __name__ == "__main__":
    main()
