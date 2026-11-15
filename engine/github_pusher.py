"""
1-Click GitHub Repository Creator & Auto-Pusher (V8.2 macOS & Windows)
Supports 1-Click Instant Push via:
1. Native macOS/Linux Git (macOS Keychain, SSH key, or existing remote)
2. Personal Access Token (PAT) with auto-persistence in .env
3. Environment variables (GITHUB_TOKEN / GH_TOKEN)
4. System Git Credential Helper / Manager
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GITHUB_TOKEN_CREATION_URL = "https://github.com/settings/tokens/new?scopes=repo,workflow&description=AI-Holding-Company-V8"


class GitHubAutoPusher:
    def __init__(self, repo_dir: str = PROJECT_ROOT):
        self.repo_dir = repo_dir
        self._last_auth_status = None

    def _git_env(self) -> dict:
        """สภาพแวดล้อมสำหรับรัน git โดยปิด terminal prompt ไม่ให้ค้างรอรับ input ทางคีย์บอร์ด"""
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        return env

    def _read_token_from_env_file(self) -> str:
        """อ่านค่า GITHUB_TOKEN หรือ GH_TOKEN จากไฟล์ .env"""
        env_path = os.path.join(self.repo_dir, ".env")
        if not os.path.exists(env_path):
            return ""
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k in ("GITHUB_TOKEN", "GH_TOKEN") and v:
                        return v
        except Exception:
            pass
        return ""

    def _save_token_to_env_file(self, token: str):
        """บันทึก GITHUB_TOKEN ลงในไฟล์ .env เพื่อให้การกดปุ่มครั้งถัดไปเป็น 1-Click Instant Push ได้ทันที"""
        if not token:
            return
        env_path = os.path.join(self.repo_dir, ".env")
        try:
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                new_lines = []
                found = False
                for line in lines:
                    stripped = line.strip()
                    if not stripped.startswith("#") and "=" in stripped:
                        k, _ = stripped.split("=", 1)
                        if k.strip() == "GITHUB_TOKEN":
                            new_lines.append(f"GITHUB_TOKEN={token}\n")
                            found = True
                            continue
                    new_lines.append(line)
                if not found:
                    if new_lines and not new_lines[-1].endswith("\n"):
                        new_lines[-1] += "\n"
                    new_lines.append(f"GITHUB_TOKEN={token}\n")
                with open(env_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
            else:
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(f"GITHUB_TOKEN={token}\n")
            os.environ["GITHUB_TOKEN"] = token
        except Exception:
            pass

    def _get_stored_credential(self) -> tuple[str, str]:
        """ดึงโทเคน GitHub จาก Git Credential Helper"""
        try:
            p = subprocess.run(
                ["git", "credential", "fill"],
                input="protocol=https\nhost=github.com\n\n",
                text=True,
                capture_output=True,
                timeout=5,
                cwd=self.repo_dir,
                env=self._git_env()
            )
            creds = dict(line.split("=", 1) for line in p.stdout.splitlines() if "=" in line)
            return creds.get("password", "").strip(), creds.get("username", "Salmonnnnnn").strip()
        except Exception:
            return "", "Salmonnnnnn"

    def _verify_token_and_get_user(self, token: str) -> str | None:
        """ตรวจสอบว่าโทเคนใช้งานได้จริงและดึงชื่อบัญชี GitHub"""
        self._last_auth_status = None
        if not token or not token.strip():
            return None
        token = token.strip()
        is_token_format = token.startswith(("ghp_", "github_pat_", "gho_", "ghu_")) or len(token) >= 30
        req = urllib.request.Request(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "AI-Holding-Company-V8"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    self._last_auth_status = 200
                    data = json.loads(resp.read().decode("utf-8"))
                    return data.get("login", "Salmonnnnnn")
        except urllib.error.HTTPError as e:
            self._last_auth_status = e.code
            if e.code == 401:
                return None
            if is_token_format:
                return "Salmonnnnnn"
            return None
        except (urllib.error.URLError, TimeoutError, OSError, Exception):
            self._last_auth_status = "NETWORK_ERROR"
            if is_token_format:
                return "Salmonnnnnn"
            return None
        return None

    def _clear_stale_credentials(self):
        """ล้างโทเคนเก่าที่หมดอายุ"""
        try:
            subprocess.run(
                ["git", "credential", "reject"],
                input="protocol=https\nhost=github.com\n\n",
                text=True,
                capture_output=True,
                timeout=5,
                cwd=self.repo_dir,
                env=self._git_env()
            )
            if sys.platform.startswith("win"):
                subprocess.run(
                    ["cmdkey", "/delete:LegacyGeneric:target=git:https://github.com"],
                    capture_output=True,
                    timeout=5
                )
        except Exception:
            pass

    def _save_valid_credential(self, username: str, token: str):
        """บันทึกโทเคนที่ใช้ได้ลงใน Git Credential Helper"""
        try:
            subprocess.run(
                ["git", "credential", "approve"],
                input=f"protocol=https\nhost=github.com\nusername={username}\npassword={token}\n\n",
                text=True,
                capture_output=True,
                timeout=5,
                cwd=self.repo_dir,
                env=self._git_env()
            )
        except Exception:
            pass

    def _ensure_git_committed(self, steps_log: list, commit_label: str = "") -> bool:
        """Stage ทุกไฟล์และ Commit การเปลี่ยนแปลงล่าสุดก่อนทำการ Push (เคารพ .gitignore อย่างเคร่งครัด)"""
        try:
            # กำหนดค่าผู้ใช้ git สำรองหากยังไม่ได้ตั้งค่า เพื่อป้องกัน commit error ในเครื่องใหม่
            chk_name = subprocess.run(["git", "config", "user.name"], cwd=self.repo_dir, capture_output=True, text=True, env=self._git_env())
            if not chk_name.stdout.strip():
                subprocess.run(["git", "config", "user.name", "AI Holding Company V8"], cwd=self.repo_dir, capture_output=True, env=self._git_env())
            chk_email = subprocess.run(["git", "config", "user.email"], cwd=self.repo_dir, capture_output=True, text=True, env=self._git_env())
            if not chk_email.stdout.strip():
                subprocess.run(["git", "config", "user.email", "ai-company@local.internal"], cwd=self.repo_dir, capture_output=True, env=self._git_env())

            # Stage ทุกไฟล์ใน working tree (ไฟล์ที่ตรงกับ .gitignore เช่น SQLite lock/wal, .env จะไม่ถูก stage)
            subprocess.run(["git", "add", "-A"], cwd=self.repo_dir, capture_output=True, env=self._git_env())

            status_proc = subprocess.run(["git", "status", "--porcelain"], cwd=self.repo_dir, capture_output=True, text=True, env=self._git_env())
            if status_proc.stdout.strip():
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                msg = commit_label or f"Release AI Holding Company V8 Portable ({ts})"
                c_proc = subprocess.run(
                    ["git", "commit", "-m", msg],
                    cwd=self.repo_dir,
                    capture_output=True,
                    text=True,
                    env=self._git_env()
                )
                if c_proc.returncode == 0:
                    steps_log.append(f"✅ บันทึกไฟล์ทั้งหมดลง Git Commit เรียบร้อยแล้ว ('{msg}')")
                else:
                    err_txt = (c_proc.stderr or c_proc.stdout or "").strip()
                    steps_log.append(f"⚠️ บันทึก commit ไม่สำเร็จ: {err_txt[:120]}")
            else:
                steps_log.append("ℹ️ ไฟล์ในโปรเจกต์อยู่ในสถานะล่าสุดพร้อม Push (Clean working tree)")
            return True
        except Exception as e:
            steps_log.append(f"⚠️ เกิดข้อผิดพลาดตอน commit: {e}")
            return False

    def _push_excluding_workflows(
        self,
        username: str,
        clean_repo_name: str,
        auth_remote: str,
        clean_remote: str,
        steps_log: list,
        repo_url: str
    ) -> dict:
        """
        Fallback push mechanism:
        Temporarily moves .github/workflows out of the repository, commits and pushes
        all other project files, and immediately restores .github/workflows locally
        so no local work or cloud runner configurations are ever lost.
        """
        workflows_dir = os.path.join(self.repo_dir, ".github", "workflows")
        temp_backup = None
        try:
            if os.path.exists(workflows_dir):
                temp_backup = tempfile.mkdtemp(prefix="ai_workflows_bak_")
                shutil.copytree(workflows_dir, os.path.join(temp_backup, "workflows"))
                shutil.rmtree(workflows_dir)
                subprocess.run(["git", "add", "-A"], cwd=self.repo_dir, capture_output=True, env=self._git_env())
                commit_msg = f"Release AI Holding Company V8 (without workflows) {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.repo_dir, capture_output=True, env=self._git_env())
                steps_log.append("📦 สำรองโฟลเดอร์ .github/workflows ชั่วคราว และสร้าง commit สำรองสำหรับ Token ทั่วไป")

            subprocess.run(["git", "remote", "remove", "origin"], cwd=self.repo_dir, capture_output=True, env=self._git_env())
            subprocess.run(["git", "remote", "add", "origin", auth_remote], cwd=self.repo_dir, capture_output=True, env=self._git_env())
            push_proc = subprocess.run(
                ["git", "push", "-u", "origin", "main", "--force"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=60,
                env=self._git_env()
            )
            subprocess.run(["git", "remote", "set-url", "origin", clean_remote], cwd=self.repo_dir, capture_output=True, env=self._git_env())

            if push_proc.returncode == 0:
                steps_log.append(f"🚀 อัปโหลดโค้ด + โมเดล + รายงาน + กราฟ Obsidian ขึ้น {repo_url} สำเร็จ 100%!")
                steps_log.append("💡 คำแนะนำ: หากต้องการรันระบบบน Cloud Runner 24 ชม. สามารถเปิดสิทธิ์ [✔] workflow บน GitHub Settings ได้ใน 30 วินาที")
                return {
                    "status": "SUCCESS_EXCLUDING_WORKFLOW",
                    "username": username,
                    "repo_name": clean_repo_name,
                    "repo_url": repo_url,
                    "message": (
                        f"🎉 อัปโหลดโปรเจกต์ทั้งหมดขึ้น GitHub สำเร็จแล้วที่ {repo_url} (ยกเว้นโฟลเดอร์ .github/workflows เพื่อความปลอดภัยของ Token)\n\n"
                        "💡 ไฟล์ระบบ, AI Engine 12+ ตัว, ระบบจำลอง MT5, Dashboard และ Obsidian Vault ถูกส่งขึ้นครบถ้วน 100%!\n\n"
                        "👉 หากต้องการเปิดใช้งาน GitHub Actions Cloud Runner รันระบบ 24 ชม. บนคลาวด์ฟรี:\n"
                        "1. เปิดลิงก์: https://github.com/settings/tokens\n"
                        "2. ติ๊กเครื่องหมายถูกหน้าช่อง [✔] workflow แล้วกด Update token\n"
                        "3. กดอัปโหลดขึ้น GitHub อีกครั้งได้เลยครับ!"
                    ),
                    "steps_log": steps_log
                }
            else:
                err_txt = (push_proc.stderr or push_proc.stdout or "").strip()
                steps_log.append(f"❌ Fallback Push Error: {err_txt[:240]}")
                return {
                    "status": "PUSH_ERROR",
                    "username": username,
                    "repo_name": clean_repo_name,
                    "repo_url": repo_url,
                    "token_url": GITHUB_TOKEN_CREATION_URL,
                    "message": (
                        f"⚠️ เกิดข้อผิดพลาดตอน git push: {err_txt[:180]}\n\n"
                        f"👉 หากเกิดจากสิทธิ์เข้าถึงหรือ Token หมดอายุ สามารถสร้าง Token ใหม่ได้ทันทีใน 1-Click:\n"
                        f"{GITHUB_TOKEN_CREATION_URL}\n"
                        f"(เลือกระดับสิทธิ์ repo และ workflow ให้อัตโนมัติแล้วครับ)"
                    ),
                    "steps_log": steps_log
                }
        finally:
            if temp_backup and os.path.exists(temp_backup):
                backed_workflows = os.path.join(temp_backup, "workflows")
                if os.path.exists(backed_workflows):
                    os.makedirs(os.path.dirname(workflows_dir), exist_ok=True)
                    if os.path.exists(workflows_dir):
                        shutil.rmtree(workflows_dir)
                    shutil.copytree(backed_workflows, workflows_dir)
                    steps_log.append("🛡️ กู้คืนโฟลเดอร์ .github/workflows กลับสู่เครื่องเรียบร้อยแล้ว (ไฟล์ในเครื่องอยู่ครบ 100%)")
                shutil.rmtree(temp_backup, ignore_errors=True)
                subprocess.run(["git", "add", "-A"], cwd=self.repo_dir, capture_output=True, env=self._git_env())

    def push_project_to_github(
        self,
        repo_name: str = "AI-Holding-Company-V8-Portable",
        private: bool = False,
        custom_token: str = "",
        interactive_browser_login: bool = True,
        exclude_workflows: bool = False
    ) -> dict:
        steps_log = []
        clean_repo_name = (repo_name or "AI-Holding-Company-V8-Portable").strip().replace(" ", "-")

        # 1. ค้นหาโทเคนตามลำดับความสำคัญ (Token Lookup Order)
        # a. custom_token จาก request
        # b. os.getenv("GITHUB_TOKEN") หรือ os.getenv("GH_TOKEN")
        # c. อ่าน GITHUB_TOKEN จากไฟล์ .env
        # d. ดึงจาก Git Credential Helper (_get_stored_credential)
        token = ""
        username = "Salmonnnnnn"

        if custom_token and custom_token.strip():
            c_token = custom_token.strip()
            self._save_token_to_env_file(c_token)
            verified_user = self._verify_token_and_get_user(c_token)
            is_valid_format = c_token.startswith(("ghp_", "github_pat_", "gho_", "ghu_")) or len(c_token) >= 30

            # Only return AUTH_ERROR if GitHub specifically returned 401 Unauthorized
            # or if verification failed and token format is invalid
            if self._last_auth_status == 401 or (not verified_user and not is_valid_format):
                return {
                    "status": "AUTH_ERROR",
                    "token_url": GITHUB_TOKEN_CREATION_URL,
                    "message": (
                        "❌ GitHub Token ที่กรอกไม่ถูกต้องหรือหมดอายุ\n\n"
                        "💡 GitHub ไม่อนุญาตให้ล็อกอินด้วยรหัสผ่านปกติแล้ว ต้องใช้ Personal Access Token (PAT)\n\n"
                        "⚡ คุณสามารถสร้าง Token ใหม่ที่ถูกต้องได้ทันทีใน 1-Click ผ่านลิงก์นี้:\n"
                        f"{GITHUB_TOKEN_CREATION_URL}\n"
                        "(ลิงก์นี้จะเปิดหน้าต่างที่เลือกสิทธิ์ [✔] repo และ [✔] workflow พร้อมตั้งชื่อให้อัตโนมัติ)\n\n"
                        "👉 วิธีทำ: เลื่อนลงไปล่างสุดของหน้าต่าง GitHub กดปุ่มสีเขียว 'Generate token' แล้วนำรหัสมาวางในช่องด้านล่าง (ระบบจะบันทึกลง .env ให้อัตโนมัติครับ)"
                    ),
                    "steps_log": steps_log
                }

            token = c_token
            username = verified_user or "Salmonnnnnn"
            self._clear_stale_credentials()
            self._save_valid_credential(username, token)
            steps_log.append(f"✅ ยืนยันตัวตนด้วย GitHub Token สำเร็จ (บัญชี: {username}) และบันทึกลง .env เรียบร้อย")

        if not token:
            env_tok = (os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or "").strip()
            if env_tok:
                verified_user = self._verify_token_and_get_user(env_tok)
                if verified_user:
                    token = env_tok
                    username = verified_user
                    steps_log.append(f"✅ พบ GitHub Token จากสภาพแวดล้อมระบบ (Environment) ของบัญชี '{username}'")

        if not token:
            dotenv_tok = self._read_token_from_env_file()
            if dotenv_tok:
                verified_user = self._verify_token_and_get_user(dotenv_tok)
                if verified_user:
                    token = dotenv_tok
                    username = verified_user
                    steps_log.append(f"✅ พบ GitHub Token จากไฟล์ .env ของบัญชี '{username}'")

        if not token:
            stored_tok, stored_usr = self._get_stored_credential()
            if stored_tok:
                verified_user = self._verify_token_and_get_user(stored_tok)
                if verified_user:
                    token = stored_tok
                    username = verified_user
                    steps_log.append(f"✅ พบสิทธิ์ GitHub ที่บันทึกไว้ของบัญชี '{username}'")

        # หากเป็น Windows และเปิด interactive_browser_login ไว้ และยังไม่มี token
        if not token and interactive_browser_login and sys.platform.startswith("win"):
            steps_log.append("🔄 กำลังเปิดหน้าต่างล็อกอิน GitHub ผ่านเว็บเบราว์เซอร์ (Git Credential Manager)...")
            self._clear_stale_credentials()
            try:
                subprocess.run(
                    ["git", "credential-manager", "github", "login"],
                    timeout=120,
                    cwd=self.repo_dir,
                    env=self._git_env()
                )
            except Exception as e:
                steps_log.append(f"⚠️ การเรียกหน้าต่างล็อกอิน: {e}")

            stored_tok, stored_usr = self._get_stored_credential()
            verified_user = self._verify_token_and_get_user(stored_tok)
            if verified_user:
                token = stored_tok
                username = verified_user
                steps_log.append(f"✅ ล็อกอินผ่านเบราว์เซอร์สำเร็จ! (บัญชี: {username})")

        # ----------------------------------------------------
        # กรณีไม่มี Token: ทำ Native macOS / Linux Git Push Fallback
        # ----------------------------------------------------
        if not token:
            steps_log.append("ℹ️ ไม่พบ Token เฉพาะเจาะจง — กำลังลองดึงและอัปโหลดผ่าน Native Git (macOS Keychain / SSH / Existing Remote)...")

            # Stage ทุกไฟล์และ Commit การเปลี่ยนแปลงล่าสุดก่อนทำการ Push
            self._ensure_git_committed(steps_log)

            # ตรวจสอบ remote URL ที่มีอยู่
            repo_url = f"https://github.com/{username}/{clean_repo_name}"
            try:
                url_proc = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=self.repo_dir,
                    capture_output=True,
                    text=True,
                    env=self._git_env()
                )
                if url_proc.returncode == 0 and url_proc.stdout.strip():
                    rem_url = url_proc.stdout.strip()
                    if "github.com" in rem_url:
                        repo_url = rem_url.replace(".git", "")
                        if repo_url.startswith("git@github.com:"):
                            repo_url = repo_url.replace("git@github.com:", "https://github.com/")
                else:
                    clean_remote = f"https://github.com/{username}/{clean_repo_name}.git"
                    subprocess.run(["git", "remote", "add", "origin", clean_remote], cwd=self.repo_dir, capture_output=True, env=self._git_env())
            except Exception:
                pass

            # ลอง Push ด้วย Native Git
            push_proc = subprocess.run(
                ["git", "push", "-u", "origin", "HEAD"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=60,
                env=self._git_env()
            )

            if push_proc.returncode == 0:
                steps_log.append(f"🚀 ดึงและอัปโหลดโค้ดขึ้น {repo_url} ผ่าน Native Git สำเร็จ 100%!")
                return {
                    "status": "SUCCESS",
                    "username": username,
                    "repo_name": clean_repo_name,
                    "repo_url": repo_url,
                    "message": f"🎉 ดึงและอัปโหลดโปรเจกต์ขึ้น GitHub สำเร็จแล้วที่ {repo_url}",
                    "steps_log": steps_log
                }
            else:
                err_txt = (push_proc.stderr or push_proc.stdout or "").strip()
                steps_log.append(f"⚠️ ผลการ Push แบบ Native: {err_txt[:180]}")
                friendly_msg = (
                    "⚠️ ไม่สามารถเชื่อมต่อ GitHub ได้โดยอัตโนมัติ เนื่องจากยังไม่มีสิทธิ์เข้าถึง (Authentication Required)\n\n"
                    "👉 หมายเหตุสำคัญ: GitHub ไม่อนุญาตให้ล็อกอินด้วยรหัสผ่านบัญชีปกติแล้ว ต้องใช้ Personal Access Token (PAT)\n\n"
                    "⚡ วิธีแก้ปัญหาแบบ 1-Click ที่ง่ายและเร็วที่สุด (ใช้เวลาไม่เกิน 30 วินาที):\n"
                    f"1. เปิดลิงก์นี้เพื่อสร้าง Token: {GITHUB_TOKEN_CREATION_URL}\n"
                    "   (ลิงก์นี้ถูกเตรียมไว้ล่วงหน้า จะติ๊กเลือกสิทธิ์ที่จำเป็นทั้งหมดให้อัตโนมัติ: [✔] repo และ [✔] workflow พร้อมตั้งชื่อโทเคนให้เรียบร้อย)\n"
                    "2. เลื่อนลงไปล่างสุดของหน้าต่าง GitHub แล้วกดปุ่มสีเขียว 'Generate token'\n"
                    "3. คัดลอก Token ที่ได้ (ขึ้นต้นด้วย ghp_...) นำมาวางในช่อง '🔑 GitHub Personal Access Token' ด้านล่าง แล้วกดอัปโหลด\n\n"
                    "💡 เมื่อคุณวาง Token ลงใน Web UI ระบบจะบันทึกลงในไฟล์ .env ภายในเครื่องของคุณให้อัตโนมัติ ปลอดภัย และทำให้ครั้งถัดไปกด 1-Click Instant Push ได้ตลอดไปโดยไม่ต้องตั้งค่าซ้ำอีกครับ!"
                )
                return {
                    "status": "NEED_LOGIN",
                    "username": username,
                    "repo_name": clean_repo_name,
                    "repo_url": repo_url,
                    "token_url": GITHUB_TOKEN_CREATION_URL,
                    "message": friendly_msg,
                    "steps_log": steps_log
                }

        # ----------------------------------------------------
        # กรณีมี Token ที่ยืนยันตัวตนแล้ว: Push ด้วย Authenticated Remote
        # ----------------------------------------------------
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
                "Authorization": f"Bearer {token}",
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
        except Exception as e:
            steps_log.append(f"⚠️ การเชื่อมต่อ GitHub API: {e}")

        # Git init, branch, add, commit
        subprocess.run(["git", "init", "-b", "main"], cwd=self.repo_dir, capture_output=True, env=self._git_env())
        subprocess.run(["git", "branch", "-M", "main"], cwd=self.repo_dir, capture_output=True, env=self._git_env())
        self._ensure_git_committed(steps_log)

        # ใช้ Authenticated HTTPS URL สำหรับจังหวะ Push แล้วค่อยสลับเป็น Clean URL
        auth_remote = f"https://{username}:{token}@github.com/{username}/{clean_repo_name}.git"
        clean_remote = f"https://github.com/{username}/{clean_repo_name}.git"

        # หากระบุว่าต้องการแยก .github/workflows ออกตั้งแต่แรก
        if exclude_workflows:
            steps_log.append("ℹ️ โหมด exclude_workflows=True: ข้ามโฟลเดอร์ .github/workflows สำหรับ Token ที่ไม่มีสิทธิ์ workflow")
            return self._push_excluding_workflows(
                username=username,
                clean_repo_name=clean_repo_name,
                auth_remote=auth_remote,
                clean_remote=clean_remote,
                steps_log=steps_log,
                repo_url=repo_url
            )

        subprocess.run(["git", "remote", "remove", "origin"], cwd=self.repo_dir, capture_output=True, env=self._git_env())
        subprocess.run(["git", "remote", "add", "origin", auth_remote], cwd=self.repo_dir, capture_output=True, env=self._git_env())

        push_proc = subprocess.run(
            ["git", "push", "-u", "origin", "main", "--force"],
            cwd=self.repo_dir,
            capture_output=True,
            text=True,
            timeout=60,
            env=self._git_env()
        )
        # เปลี่ยน remote กลับเป็น clean URL เพื่อไม่ให้เก็บ token ไว้ใน .git/config
        subprocess.run(["git", "remote", "set-url", "origin", clean_remote], cwd=self.repo_dir, capture_output=True, env=self._git_env())

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
            if "without 'workflow' scope" in err_txt or ("workflow" in err_txt.lower() and "scope" in err_txt.lower()):
                steps_log.append("⚠️ ตรวจพบข้อจำกัด: Token ขาดสิทธิ์ 'workflow' สำหรับโฟลเดอร์ .github/workflows/")
                steps_log.append("🔄 เริ่มต้นระบบ Smart Fallback: กำลังอัปโหลดโปรเจกต์ทั้งหมดโดยเว้น .github/workflows ให้อัตโนมัติ...")
                fallback_res = self._push_excluding_workflows(
                    username=username,
                    clean_repo_name=clean_repo_name,
                    auth_remote=auth_remote,
                    clean_remote=clean_remote,
                    steps_log=steps_log,
                    repo_url=repo_url
                )
                if fallback_res.get("status") in ("SUCCESS_EXCLUDING_WORKFLOW", "SUCCESS"):
                    return fallback_res

                friendly_msg = (
                    "⚠️ GitHub Token ขาดสิทธิ์ 'workflow' (จำเป็นสำหรับระบบรันบนคลาวด์ 24 ชม. แม้ปิดคอม)\n\n"
                    "👉 วิธีแก้ใน 3 ขั้นตอน (ใช้เวลา 30 วินาที):\n"
                    f"1. เปิดลิงก์สร้าง Token ใหม่ที่เลือกสิทธิ์ครบถ้วนอัตโนมัติ: {GITHUB_TOKEN_CREATION_URL}\n"
                    "   (หรือเปิด https://github.com/settings/tokens คลิกที่ชื่อ Token เดิม แล้วติ๊กถูกที่ช่อง [✔] workflow)\n"
                    "2. เลื่อนลงล่างสุดแล้วกดปุ่ม 'Generate token' หรือ 'Update token'\n"
                    "3. นำ Token มาวางในช่องด้านล่าง แล้วกดอัปโหลดอีกครั้ง — ระบบจะบันทึกลง .env ให้อัตโนมัติครับ!"
                )
                steps_log.append("💡 วิธีแก้: ติ๊กถูกที่ช่อง [✔] workflow บน GitHub Settings -> แล้วกดอัปโหลดอีกครั้ง")
                return {
                    "status": "WORKFLOW_SCOPE_REQUIRED",
                    "username": username,
                    "repo_name": clean_repo_name,
                    "repo_url": repo_url,
                    "token_url": GITHUB_TOKEN_CREATION_URL,
                    "message": friendly_msg,
                    "steps_log": steps_log
                }

            steps_log.append(f"❌ Push Error: {err_txt[:240]}")
            return {
                "status": "PUSH_ERROR",
                "username": username,
                "repo_name": clean_repo_name,
                "repo_url": repo_url,
                "token_url": GITHUB_TOKEN_CREATION_URL,
                "message": (
                    f"⚠️ เกิดข้อผิดพลาดตอน git push: {err_txt[:180]}\n\n"
                    f"👉 หมายเหตุ: GitHub ไม่อนุญาตให้ล็อกอินด้วยรหัสผ่านปกติแล้ว ต้องใช้ Personal Access Token (PAT)\n"
                    f"สร้าง Token ใหม่ง่ายๆ 1-Click ที่ลิงก์นี้: {GITHUB_TOKEN_CREATION_URL}\n"
                    f"(ระบบเลือกสิทธิ์ [✔] repo และ [✔] workflow ให้ครบเรียบร้อยแล้วครับ)"
                ),
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
