i have a python script which i want to automate to be run every 12 hours automatically. I want to achieve this free of charge , the python script is as follows:  import requests

# -------------------- Configuration --------------------
import os
ASANA_PAT               = os.environ['ASANA_PAT']
PORTFOLIO_GID           = os.environ['PORTFOLIO_GID']
SHOP_URL_FIELD_GID      = os.environ['SHOP_URL_FIELD_GID']
JOURNEY_REV_FIELD_GID   = os.environ['JOURNEY_REV_FIELD_GID']
BROADCAST_REV_FIELD_GID = os.environ['BROADCAST_REV_FIELD_GID']
ANALYTICS_API           = os.environ.get(
    'ANALYTICS_API',
    'https://43r09s4nl9.execute-api…/attribution'
)
HEADERS = {'Authorization': f'Bearer {ASANA_PAT}'}

# -------------------- API Endpoints --------------------
ANALYTICS_API = 'https://43r09s4nl9.execute-api.us-east-1.amazonaws.com/internal/shop/analytics/attribution'

# -------------------- Asana Functions ------------------

def get_projects_in_portfolio(portfolio_gid):
    url = f'https://app.asana.com/api/1.0/portfolios/{portfolio_gid}/items'
    projects = []
    offset = None
    while True:
        params = {'limit': 100}
        if offset:
            params['offset'] = offset
        res = requests.get(url, headers=HEADERS, params=params)
        if res.status_code != 200:
            return []
        data = res.json()
        projects.extend(data.get('data', []))
        next_page = data.get('next_page')
        offset = next_page['offset'] if next_page and 'offset' in next_page else None
        if not offset:
            break
    return projects

def get_shop_url(project_gid):
    url = f'https://app.asana.com/api/1.0/projects/{project_gid}?opt_fields=custom_fields'
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return None
    fields = res.json()['data']['custom_fields']
    for field in fields:
        if field['gid'] == SHOP_URL_FIELD_GID:
            return field.get('text_value') or field.get('display_value')
    return None

def update_asana_field(project_gid, custom_field_gid, value):
    url = f'https://app.asana.com/api/1.0/projects/{project_gid}'
    data = {
        'data': {
            'custom_fields': {
                custom_field_gid: round(value, 2)
            }
        }
    }
    res = requests.put(url, headers=HEADERS, json=data)
    return res.status_code == 200

# -------------------- Analytics Integration ------------

def get_analytics(shop_url):
    payload = {'shopUrl': shop_url}
    res = requests.post(ANALYTICS_API, json=payload)
    if res.status_code != 200:
        return None
    return res.json().get('data', {})

# -------------------- Main Flow ------------------------

def main():
    projects = get_projects_in_portfolio(PORTFOLIO_GID)
    for project in projects:
        project_gid = project['gid']
        project_name = project['name']
        shop_url = get_shop_url(project_gid)

        if not shop_url:
            print(f"[{project_name}] No Shop URL found. Skipping.")
            continue

        analytics = get_analytics(shop_url)
        if not analytics:
            print(f"[{project_name}] Failed to get analytics for {shop_url}")
            continue

        journey_rev = analytics.get('journeyRevenue14Day')
        broadcast_rev = analytics.get('broadcastRevenue14Day')

        updated_fields = []
        if journey_rev is not None:
            success = update_asana_field(project_gid, JOURNEY_REV_FIELD_GID, journey_rev)
            if success:
                updated_fields.append("Journey Revenue")
        if broadcast_rev is not None:
            success = update_asana_field(project_gid, BROADCAST_REV_FIELD_GID, broadcast_rev)
            if success:
                updated_fields.append("Broadcast Revenue")

        print(f"[{project_name}] Updated: {', '.join(updated_fields)}")

if __name__ == '__main__':
    main() ; can you help me to do the same
