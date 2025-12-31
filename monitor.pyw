import psutil
import requests
import time
import socket

# 設定
WEBHOOK_URL = "あなたのWebhook URL"
ALERT_THRESHOLD = 80.0  # CPU使用率がこれを超えたら警告色にする

def send_discord_webhook():
    # システム情報の取得
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    hostname = socket.gethostname()

    # メモリ計算 (GB単位)
    mem_total = round(memory.total / (1024**3), 2)
    mem_used = round(memory.used / (1024**3), 2)
    mem_percent = memory.percent

    # ディスク計算 (GB単位)
    disk_total = round(disk.total / (1024**3), 2)
    disk_free = round(disk.free / (1024**3), 2)

    # 色の決定 (CPU負荷が高いと赤、通常は緑)
    color = 0xFF0000 if cpu_percent > ALERT_THRESHOLD else 0x00FF00
    status_msg = "⚠️ 高負荷警告" if cpu_percent > ALERT_THRESHOLD else "✅ 正常稼働中"

    payload = {
        "username": "PC Monitor",
        "embeds": [
            {
                "title": f"{status_msg}: {hostname}",
                "color": color,
                "fields": [
                    {
                        "name": "CPU使用率",
                        "value": f"{cpu_percent}%",
                        "inline": True
                    },
                    {
                        "name": "メモリ使用量",
                        "value": f"{mem_used}GB / {mem_total}GB ({mem_percent}%)",
                        "inline": True
                    },
                    {
                        "name": "ディスク空き容量",
                        "value": f"{disk_free}GB / {disk_total}GB",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Resource Monitor"
                }
            }
        ]
    }

    try:
        requests.post(WEBHOOK_URL, json=payload)
        print("送信完了")
    except Exception as e:
        print(f"送信エラー: {e}")

if __name__ == "__main__":
    print("監視を開始しました...")
    
    while True: # 無限に繰り返す
        try:
            send_discord_webhook()
        except Exception as e:
            print(f"エラー発生: {e}")
            
        # 600秒（10分）待機してから次へ
        # ここを短くしすぎるとDiscordに「送りすぎ！」と怒られるので注意
        time.sleep(600)
