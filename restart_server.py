import subprocess

def restart_server():
    try:
        subprocess.run(["sudo", "reboot"], check=True)
        print("🔄 Server is restarting...")
    except Exception as e:
        print(f"❌ Failed to restart server: {e}")

if __name__ == "__main__":
    restart_server()
