import requests
import logging

logging.basicConfig(level=logging.INFO)

def get_access_keys(api_url):
    try:
        response = requests.get(api_url + "/access-keys", verify=False)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to get access keys: {e}")
        return None

def check_if_free(uid, api_url):
    keys = get_access_keys(api_url).get('accessKeys', [])
    for key in keys:
        if key['name'] == f"tg{uid}":
            return False
    return True

def create_key(api_url, uid, bytes_limit, is_free):
    try:
        key_name = f"free{uid}" if is_free else f"paid{uid}"

        # Key creation
        response = requests.post(f"{api_url}/access-keys", verify=False)
        response.raise_for_status()
        key_data = response.json()
        access_url = key_data.get('accessUrl')
        key_id = key_data.get('id')

        if not access_url or not key_id:
            logging.error("Invalid response: missing 'accessUrl' or 'id'")
            return None, None

        # Updating key name
        files = {'name': (None, key_name)}
        response = requests.put(
            f"{api_url}/access-keys/{key_id}/name", files=files, verify=False)
        response.raise_for_status()

        # Setting data limit
        json_data = {'limit': {'bytes': bytes_limit}}
        response = requests.put(
            f"{api_url}/access-keys/{key_id}/data-limit", json=json_data, verify=False)
        response.raise_for_status()

        return access_url, key_id

    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None, None


def delete_key(api_url, key_id):
    try:
        response = requests.delete(
            f"{api_url}/access-keys/{key_id}", verify=False)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")


def get_key_traffic(api_url, key_id):
    try:
        response = requests.get(f"{api_url}/metrics/transfer", verify=False)
        response.raise_for_status()
        metrics = response.json()
        traffic = metrics.get('bytesTransferredByUserId',
                              {}).get(str(key_id), 0)
        return traffic
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return 0
    except ValueError as e:
        logging.error(f"Failed to parse JSON response: {e}")
        return 0
