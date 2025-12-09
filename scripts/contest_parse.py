import sys
import json
from datetime import datetime, timedelta, timezone

# No longer need BASE_URL since we're reading from stdin

def parse_domjudge_time(time_str):
    """
    DOMjudge 的時間格式可能是：
    - "2025-12-05T13:30:00+08:00"（帶時區）
    - "2025-12-05T05:30:00Z"（UTC）
    - null
    """
    if not time_str:
        return None
    
    # 統一處理 Z 結尾 → 換成 +00:00
    time_str = time_str.replace('Z', '+00:00')
    
    try:
        # fromisoformat 支援 +08:00 這種格式
        dt = datetime.fromisoformat(time_str)
        # 確保是 aware datetime（有時區資訊）
        if dt.tzinfo is None:
            return None
        return int(dt.timestamp())
    except Exception as e:
        print(f"時間解析失敗: {time_str} -> {e}")
        return None

def parse_duration(duration_str):
    """
    解析 DOMjudge 的 duration 字串，例如：
    - "5:00:00" → 5 小時
    - "8760:00:00.000" → 很多小時（你這場是測試用超長比賽）
    - null
    """
    if not duration_str:
        return 0
    
    try:
        parts = duration_str.split(':')
        if '.' in parts[-1]:
            parts[-1] = parts[-1].split('.')[0]
        
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
        seconds = int(parts[2]) if len(parts) > 2 else 0
        return hours * 3600 + minutes * 60 + seconds
    except:
        return 0

def fetch_contest_config():
    try:
        print("Reading contest info from stdin...")
        # 从 stdin 读取 JSON 数据
        input_data = sys.stdin.read()
        data = json.loads(input_data)

        print("Input JSON:", json.dumps(data, indent=2, ensure_ascii=False))

        start_str = data.get("start_time")
        end_str = data.get("end_time")
        freeze_duration_str = data.get("scoreboard_freeze_duration")  # 可能是 "1:00:00" 或 null

        start_ts = parse_domjudge_time(start_str)
        end_ts = parse_domjudge_time(end_str)

        if start_ts is None or end_ts is None:
            print("無法取得比賽開始或結束時間")
            return

        # 計算 freeze 時間
        if freeze_duration_str and freeze_duration_str.strip():
            freeze_seconds = parse_duration(freeze_duration_str)
            freeze_ts = end_ts - freeze_seconds
            print(f"凍榜時間：結束前 {freeze_seconds} 秒 → {datetime.fromtimestamp(freeze_ts)}")
        else:
            # 沒有凍榜 → freeze 時間 = 結束時間（榜單到最後一刻都更新）
            freeze_ts = end_ts
            print("無凍榜設定，freeze 時間設為結束時間")

        output_data = {
            "frontPageHtml": "<h1 class=\"page-header\">LiveSite</h1>\n\n<p>CCUPC week8 即時榜單</p>\n",
            "problemLink": None,
            "times": {
                "start": start_ts,
                "end": end_ts,
                "freeze": freeze_ts,        # 正確的凍榜開始時間（UNIX timestamp）
                "scale": 1
            },
            "title": data.get("name", "LiveSite")
        }

        json_result = json.dumps(output_data, indent=4, ensure_ascii=False)
        print("\nGenerated contest.json content:")
        print(json_result)

        with open('contest.json', 'w', encoding='utf-8') as f:
            f.write(json_result)

        print("\ncontest.json 已成功寫入！")

    except json.JSONDecodeError as e:
        print(f"JSON 解析失敗: {e}")
    except Exception as e:
        print(f"發生未知錯誤: {e}")

if __name__ == "__main__":
    fetch_contest_config()