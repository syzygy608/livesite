import sys
import json
import yaml
from datetime import datetime

# 用來讓 YAML 輸出 HTML 時使用 Block Style (|)
class LiteralStr(str): pass

def change_style(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(LiteralStr, change_style)

def parse_domjudge_time(time_str):
    if not time_str:
        return None
    time_str = time_str.replace('Z', '+00:00')
    try:
        dt = datetime.fromisoformat(time_str)
        if dt.tzinfo is None:
            return None
        return int(dt.timestamp())
    except Exception as e:
        print(f"時間解析失敗: {time_str} -> {e}")
        return None

def parse_duration(duration_str):
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
        # 從 stdin 讀取 JSON (例如: curl ... | python script.py)
        input_data = sys.stdin.read()
        if not input_data:
            print("No input provided via stdin.")
            return
            
        data = json.loads(input_data)

        start_str = data.get("start_time")
        end_str = data.get("end_time")
        freeze_duration_str = data.get("scoreboard_freeze_duration")

        start_ts = parse_domjudge_time(start_str)
        end_ts = parse_domjudge_time(end_str)

        if start_ts is None or end_ts is None:
            print("無法取得比賽開始或結束時間")
            return

        if freeze_duration_str and freeze_duration_str.strip():
            freeze_seconds = parse_duration(freeze_duration_str)
            freeze_ts = end_ts - freeze_seconds
        else:
            freeze_ts = end_ts

        contest_name = data.get("name", "LiveSite")

        # 構建 HTML (使用 LiteralStr 讓它在 YAML 中變漂亮)
        html_content = (
            f"<h1 class=\"page-header\">{contest_name}</h1>\n"
            "<p>Powered by <a href=\"https://www.domjudge.org/\">DOMjudge</a> and <a href=\"https://github.com/icpcsec/livesite\">Livesite</a></p>\n"
            "<dl class=\"dl-horizontal\">\n"
            f"  <dt>Contest Start</dt><dd>{start_str}</dd>\n"
            f"  <dt>Contest End</dt><dd>{end_str}</dd>\n"
            "</dl>\n"
        )

        output_data = {
            "title": contest_name,
            "frontPageHtml": LiteralStr(html_content),
            "times": {
                # YAML 支援 Unix Timestamp，也支援 ISO 字串
                # 這裡使用 Timestamp 確保跨時區計算準確
                "start": start_ts,
                "freeze": freeze_ts,
                "end": end_ts,
                "scale": 1
            },
            "problemLink": None 
        }

        print("Writing to contest.yaml...")
        with open('contest.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(output_data, f, allow_unicode=True, sort_keys=False)
        
        print("Success! contest.yaml generated.")
        
        # 顯示預覽
        print("\n--- YAML Preview ---\n")
        print(yaml.dump(output_data, allow_unicode=True, sort_keys=False))

    except json.JSONDecodeError as e:
        print(f"JSON 解析失敗: {e}")
    except Exception as e:
        print(f"發生未知錯誤: {e}")

if __name__ == "__main__":
    fetch_contest_config()