"""
1-Click GitHub Repository Creator & Auto-Pusher (V8.1)
Supports both 1-Click Browser OAuth Login (via Git Credential Manager)
and Personal Access Token (PAT) input directly from the Web UI or CLI.
"""
import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GitHubAutoPusher:
    def __init__(self, repo_dir: str = PROJECT_ROOT):
        self.repo_dir = repo_dir

    def _get_stored_credential(self) -> tuple[str, str]:
        """ดึงโทเคน GitHub จาก Git Credential Manager"""
        try:
            p = subprocess.run(
                ["git", "credential", "fill"],
                input="protocol=https\nhost=github.com\n\n",
                text=True,
                capture_output=True,
                timeout=8,
                cwd=self.repo_dir
            )
            creds = dict(line.split("=", 1) for line in p.stdout.splitlines() if "=" in line)
            return creds.get("password", "").strip(), creds.get("username", "Salmonnnnnn").strip()
        except Exception:
            return "", "Salmonnnnnn"

    def _verify_token_and_get_user(self, token: str) -> str | None:
        """ตรวจสอบว่าโทเคนใช้งานได้จริงและดึงชื่อบัญชี GitHub"""
        if not token:
            return None
        req = urllib.request.Request(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "AI-Holding-Company-V8"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data.get("login", "Salmonnnnnn")
        except Exception:
            return None
        return None

    def _clear_stale_credentials(self):
        """ล้างโทเคนเก่าที่หมดอายุออกจาก Windows Credential Manager"""
        try:
            subprocess.run(
                ["git", "credential", "reject"],
                input="protocol=https\nhost=github.com\n\n",
                text=True,
                capture_output=True,
                timeout=5
            )
            subprocess.run(
                ["cmdkey", "/delete:LegacyGeneric:target=git:https://github.com"],
                capture_output=True,
                timeout=5
            )
        except Exception:
            pass

    def _save_valid_credential(self, username: str, token: str):
        """บันทึกโทเคนที่ใช้ได้ลงใน Git Credential Manager"""
        try:
            subprocess.run(
                ["git", "credential", "approve"],
                input=f"protocol=https\nhost=github.com\nusername={username}\npassword={token}\n\n",
                text=True,
                capture_output=True,
                timeout=5
            )
        except Exception:
            pass

    def push_project_to_github(
        self,
        repo_name: str = "AI-Holding-Company-V8-Portable",
        private: bool = False,
        custom_token: str = "",
        interactive_browser_login: bool = True
    ) -> dict:
        steps_log = []
        clean_repo_name = (repo_name or "AI-Holding-Company-V8-Portable").strip().replace(" ", "-")

        # 1. ตรวจสอบโทเคน
        token = custom_token.strip()
        username = "Salmonnnnnn"

        if token:
            verified_user = self._verify_token_and_get_user(token)
            if verified_user:
                username = verified_user
                self._clear_stale_credentials()
                self._save_valid_credential(username, token)
                steps_log.append(f"✅ ยืนยันตัวตนด้วย GitHub Token สำเร็จ (บัญชี: {username})")
            else:
                return {
                    "status": "AUTH_ERROR",
                    "message": "❌ GitHub Token ที่กรอกไม่ถูกต้องหรือหมดอายุ กรุณาตรวจสอบหรือกดปุ่ม '🌐 ล็อกอินผ่านเว็บเบราว์เซอร์'",
                    "steps_log": steps_log
                }
        else:
            stored_tok, stored_usr = self._get_stored_credential()
            verified_user = self._verify_token_and_get_user(stored_tok)
            if verified_user:
                token = stored_tok
                username = verified_user
                steps_log.append(f"✅ พบสิทธิ์ GitHub ที่ใช้งานได้ของบัญชี '{username}'")
            else:
                steps_log.append("🔄 โทเคนเก่าหมดอายุ กำลังล้างค่าเดิมและเปิดหน้าต่างล็อกอิน GitHub ผ่านเว็บเบราว์เซอร์...")
                self._clear_stale_credentials()
                if interactive_browser_login:
                    try:
                        subprocess.run(
                            ["git", "credential-manager", "github", "login"],
                            timeout=120,
                            cwd=self.repo_dir
                        )
                    except Exception as e:
                        steps_log.append(f"⚠️ การเรียกหน้าต่างล็อกอิน: {e}")

                    stored_tok, stored_usr = self._get_stored_credential()
                    verified_user = self._verify_token_and_get_user(stored_tok)
                    if verified_user:
                        token = stored_tok
                        username = verified_user
                        steps_log.append(f"✅ ล็อกอินผ่านเบราว์เซอร์สำเร็จ! (บัญชี: {username})")
                    else:
                        return {
                            "status": "NEED_LOGIN",
                            "message": "⚠️ ยังไม่ได้กดยืนยันล็อกอินในหน้าเว็บเบราว์เซอร์ หรือสามารถวาง GitHub Token (PAT) ในช่องด้านล่างแล้วกดอัปโหลดได้ทันทีครับ",
                            "steps_log": steps_log
                        }
                else:
                    return {
                        "status": "NEED_LOGIN",
                        "message": "⚠️ กรุณากดปุ่มล็อกอินผ่านเบราว์เซอร์ หรือใส่ GitHub Token",
                        "steps_log": steps_log
                    }

        # 2. สร้าง Repository บน GitHub ผ่าน REST API (หากยังไม่มี)
        repo_url = f"https://github.com/{username}/{clean_repo_name}"
        create_payload = json.dumps({
            "name": clean_repo_name,
            "description": "Autonomous AI Holding Company V8: Cozy Isometric Cutaway Office, 12+ Frontier LLMs, Obsidian Knowledge Graph Token-Saver (86% Savings), MT5 Bot & 24/7 Cloud Runner",
            "private": bool(private)
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.github.com/user/repos",
            data=create_payload,
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "AI-Holding-Company-V8"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                repo_url = data.get("html_url", repo_url)
                steps_log.append(f"✅ สร้าง Repository ใหม่บน GitHub สำเร็จ: {repo_url}")
        except urllib.error.HTTPError as e:
            if e.code == 422:
                steps_log.append(f"ℹ️ มี Repository '{clean_repo_name}' อยู่บนบัญชี {username} แล้ว พร้อมอัปเดตโค้ดล่าสุด")
            else:
                steps_log.append(f"⚠️ สถานะการสร้าง Repo ({e.code}): ใช้ URL {repo_url}")

        # 3. รัน Git Init, Add, Commit และ Push
        subprocess.run(["git", "init", "-b", "main"], cwd=self.repo_dir, capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=self.repo_dir, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=self.repo_dir, capture_output=True)
        commit_msg = f"Release AI Holding Company V8 Portable ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.repo_dir, capture_output=True)
        steps_log.append(f"✅ บันทึกไฟล์ทั้งหมดลง Git Commit ('{commit_msg}')")

        # ใช้ Authenticated HTTPS URL สำหรับจังหวะ Push แล้วค่อยสลับเป็น Clean URL
        auth_remote = f"https://{username}:{token}@github.com/{username}/{clean_repo_name}.git"
        clean_remote = f"https://github.com/{username}/{clean_repo_name}.git"

        subprocess.run(["git", "remote", "remove", "origin"], cwd=self.repo_dir, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", auth_remote], cwd=self.repo_dir, capture_output=True)

        push_proc = subprocess.run(
            ["git", "push", "-u", "origin", "main", "--force"],
            cwd=self.repo_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        # เปลี่ยน remote กลับเป็น clean URL เพื่อไม่ให้เก็บ token ไว้ใน .git/config
        subprocess.run(["git", "remote", "set-url", "origin", clean_remote], cwd=self.repo_dir, capture_output=True)

        if push_proc.returncode == 0:
            steps_log.append(f"🚀 อัปโหลดโค้ด + รายงาน + กราฟ Obsidian ขึ้น {repo_url} สำเร็จ 100%!")
            return {
                "status": "SUCCESS",
                "username": username,
                "repo_name": clean_repo_name,
                "repo_url": repo_url,
                "message": f"🎉 อัปโหลดโปรเจกต์ทั้งหมดขึ้น GitHub สำเร็จแล้วที่ {repo_url}",
                "steps_log": steps_log
            }
        else:
            err_txt = (push_proc.stderr or push_proc.stdout or "").strip()
            if "without 'workflow' scope" in err_txt or "workflow" in err_txt.lower() and "scope" in err_txt.lower():
                friendly_msg = (
                    "⚠️ GitHub Token ขาดสิทธิ์ 'workflow' (จำเป็นสำหรับระบบรันบนคลาวด์ 24 ชม. แม้ปิดคอม)\n\n"
                    "👉 วิธีแก้ใน 3 ขั้นตอน (ใช้เวลา 30 วินาที):\n"
                    "1. เปิดลิงก์: https://github.com/settings/tokens\n"
                    "2. คลิกที่ชื่อ Token ที่สร้างไว้\n"
                    "3. ติ๊กเครื่องหมายถูกหน้าช่อง [✔] workflow แล้วเลื่อนลงล่างสุดกด 'Update token'\n"
                    "4. นำโทเคนมาวางหรือกดปุ่ม 'เชื่อมต่อ GitHub & อัปโหลดทั้งหมดทันที' อีกครั้งได้เลยครับ!"
                )
                steps_log.append("❌ GitHub ปฏิเสธ: Token ขาดสิทธิ์ 'workflow' สำหรับโฟลเดอร์ .github/workflows/")
                steps_log.append("💡 วิธีแก้: ติ๊กถูกที่ช่อง [✔] workflow บน GitHub Settings -> แล้วกดอัปโหลดอีกครั้ง")
                return {
                    "status": "WORKFLOW_SCOPE_REQUIRED",
                    "username": username,
                    "repo_name": clean_repo_name,
                    "repo_url": repo_url,
                    "message": friendly_msg,
                    "steps_log": steps_log
                }

            steps_log.append(f"❌ Push Error: {err_txt[:240]}")
            return {
                "status": "PUSH_ERROR",
                "username": username,
                "repo_name": clean_repo_name,
                "repo_url": repo_url,
                "message": f"⚠️ เกิดข้อผิดพลาดตอน git push: {err_txt[:180]}",
                "steps_log": steps_log
            }


if __name__ == "__main__":
    print("=" * 76)
    print("🚀 AI HOLDING COMPANY V8 — 1-CLICK GITHUB REPO CREATOR & PUSHER")
    print("=" * 76)
    pusher = GitHubAutoPusher()
    res = pusher.push_project_to_github(interactive_browser_login=True)
    for line in res.get("steps_log", []):
        print("  ", line)
    print("-" * 76)
    print(res.get("message", ""))
    if res.get("status") == "SUCCESS":
        try:
            os.startfile(res["repo_url"])
        except Exception:
            pass
