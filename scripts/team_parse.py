import requests
import json

# contest ID
CID = "dj-6"

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

            
            final_name = team.get('display_name')
            if not final_name:
                final_name = team.get('name')

            team_id = final_name.split(':')[0].strip()
            final_name = final_name.split(':', 1)[-1].strip()

            photo_url = DEFAULT_PHOTO
            if team.get('photo') and len(team['photo']) > 0:
                photo_url = team['photo'][0].get('href', DEFAULT_PHOTO)

            university_name = team.get('affiliation', '')
            if not university_name and team.get('group_ids'):
                first_group_id = team['group_ids'][0]
                university_name = groups_map.get(first_group_id, '')

            team_obj = {
                "country": team.get('nationality', 'Unknown'),
                "id": team_id,
                "members": [], 
                "name": final_name,
                "photo": photo_url,
                "university": university_name,
                "universityShort": university_name
            }

            formatted_output[team_id] = team_obj

        json_result = json.dumps(formatted_output, indent=4, ensure_ascii=False)

        with open('teams.json', 'w', encoding='utf-8') as f:
            f.write(json_result)

    except requests.exceptions.RequestException as e:
        print(f"API requests error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_data()
