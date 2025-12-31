import keyboard
import pyautogui
import requests
import datetime
import os
import io

# --- 設定エリア ---
WEBHOOK_URL = "あなたのWebhook URL"
HOTKEY = "ctrl+alt+s"  # このキー同時押しで発動
# ------------------

def take_screenshot_and_send():
    print("📸 撮影中...")
    
    # 1. スクショを撮る
    screenshot = pyautogui.screenshot()
    
    # 2. メモリ上に画像を保存（ファイルとして保存しないのでゴミがたまらない）
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    # 3. Discordに送信
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 画像ファイルとして送信するためのデータ作成
    files = {
        'file': ('screenshot.png', img_byte_arr, 'image/png')
    }
    data = {
        "content": f"📸 Screenshot captured at {timestamp}"
    }

    try:
        requests.post(WEBHOOK_URL, data=data, files=files)
        print("送信完了！")
    except Exception as e:
        print(f"送信失敗: {e}")

if __name__ == "__main__":
    print(f"待機中... ({HOTKEY} を押すと送信)")
    
    # ホットキーを登録
    keyboard.add_hotkey(HOTKEY, take_screenshot_and_send)
    
    # プログラムが終了しないように待機
    keyboard.wait()
