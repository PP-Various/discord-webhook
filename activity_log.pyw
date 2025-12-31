import time
import datetime
import requests
import ctypes
import psutil
from collections import Counter

# --- 設定エリア ---
WEBHOOK_URL = "あなたのWebhook URL"
REPORT_TIME = "23:55"  # 毎日この時間になったら通知を送る (24時間表記)
# ------------------

# 記録用データ（辞書型で保存）
activity_stats = Counter()
last_report_date = None

def get_active_window_process_name():
    """
    現在アクティブなウィンドウのプロセス名（.exe名）を取得する
    """
    try:
        # 1. アクティブなウィンドウのハンドルを取得
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        # 2. そのウィンドウのプロセスID(PID)を取得
        pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        # 3. PIDからプロセス名を取得 (例: chrome.exe)
        process = psutil.Process(pid.value)
        return process.name()
    except:
        return "Unknown"

def send_daily_report():
    """
    Discordに集計結果を送信する
    """
    if not activity_stats:
        return # データがなければ送らない

    # 上位10個を取得
    top_activities = activity_stats.most_common(10)
    
    # 合計時間（分）
    total_minutes = sum(activity_stats.values())
    hours = total_minutes // 60
    minutes = total_minutes % 60

    # メッセージ作成
    fields = []
    rank_emoji = ["🥇", "🥈", "🥉"]
    
    for i, (name, count) in enumerate(top_activities):
        # 時間計算
        h = count // 60
        m = count % 60
        time_str = f"{h}時間{m}分" if h > 0 else f"{m}分"
        
        # アイコン決定
        prefix = rank_emoji[i] if i < 3 else f"**{i+1}.**"
        
        fields.append({
            "name": f"{prefix} {name}",
            "value": time_str,
            "inline": False
        })

    today_str = datetime.date.today().strftime('%Y/%m/%d')
    
    payload = {
        "username": "Life Logger",
        "embeds": [{
            "title": f"📊 本日のPC使用レポート ({today_str})",
            "description": f"**合計稼働時間:** {hours}時間 {minutes}分\n\n起動していたアプリの内訳:",
            "color": 0x5865F2, # Discord Blue
            "fields": fields,
            "footer": {
                "text": "1分ごとにアクティブウィンドウを集計"
            }
        }]
    }

    try:
        requests.post(WEBHOOK_URL, json=payload)
        print("レポート送信完了")
    except Exception as e:
        print(f"送信エラー: {e}")

if __name__ == "__main__":
    print(f"監視開始... 毎日 {REPORT_TIME} に通知します。")
    
    while True:
        # 現在時刻チェック
        now = datetime.datetime.now()
        current_time_str = now.strftime("%H:%M")
        current_date = now.date()

        # 指定時間になったらレポート送信 (1日1回だけ)
        if current_time_str == REPORT_TIME and last_report_date != current_date:
            send_daily_report()
            activity_stats.clear() # 集計リセット
            last_report_date = current_date
            time.sleep(60) # 連続送信防止のため1分待つ

        # アクティブウィンドウを取得してカウント (+1分)
        app_name = get_active_window_process_name()
        
        # スリープ中やロック画面を除外したい場合の簡易フィルタ
        if app_name not in ["LockApp.exe", "Unknown"]:
            activity_stats[app_name] += 1
            # print(f"Recording: {app_name}") # テスト時はコメントアウト外すと確認しやすい

        # 1分待機
        time.sleep(60)
