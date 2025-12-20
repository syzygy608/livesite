import requests
import yaml
import sys
# contest ID
CID = "dj-5"

# API URL
BASE_URL = "https://ccupc-contest.csie.io/api/v4/contests"
TEAMS_URL = f"{BASE_URL}/{CID}/teams?strict=false"
GROUPS_URL = f"{BASE_URL}/{CID}/groups?strict=false"

DEFAULT_PHOTO = "/images/default-photo-regional.png"

def fetch_data():
    try:
        print(f"Fetching groups from: {GROUPS_URL}")
        groups_resp = requests.get(GROUPS_URL)
        groups_resp.raise_for_status()
        groups_data = groups_resp.json()
        
        groups_map = {g['id']: g['name'] for g in groups_data}

        print(f"Fetching teams from: {TEAMS_URL}")
        teams_resp = requests.get(TEAMS_URL)
        teams_resp.raise_for_status()
        teams_data = teams_resp.json()

        formatted_output = {}

        for team in teams_data:
            if team.get('hidden'):
                continue
            
            raw_name = team.get('name')
            
            # 處理 DOMjudge 格式 "team_id: team_name"
            if ':' in raw_name:
                team_id = raw_name.split(':')[0].strip()
                final_name = raw_name.split(':', 1)[-1].strip()
            else:
                team_id = team.get('id')
                final_name = raw_name

            photo_url = DEFAULT_PHOTO
            if team.get('photo') and len(team['photo']) > 0:
                photo_url = team['photo'][0].get('href', DEFAULT_PHOTO)

            university_name = team.get('affiliation', '')
            # 如果沒有機構名稱，嘗試從 Group ID 找
            if not university_name and team.get('group_ids'):
                first_group_id = team['group_ids'][0]
                university_name = groups_map.get(first_group_id, '')

            # 構建符合 YAML 範例的物件
            team_obj = {
                "name": final_name,
                "university": university_name,
                "universityEn": university_name, # 範例中的 universityEn
                "members": [], # API 通常沒有成員細節，保持空陣列
                "photo": photo_url,
                # "country": team.get('nationality', 'Unknown') # 如果需要國家可取消註解
            }

            # YAML 的 key 是 team_id
            formatted_output[team_id] = team_obj

        print("Writing to teams.yaml...")
        with open('teams.yaml', 'w', encoding='utf-8') as f:
            # allow_unicode=True 確保中文不會變成 \uXXXX
            # sort_keys=False 保持插入順序 (或者依 ID 排序)
            yaml.dump(formatted_output, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

        print("Done!")

    except requests.exceptions.RequestException as e:
        print(f"API requests error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_data()