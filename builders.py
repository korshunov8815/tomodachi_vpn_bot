import json
import logging
import tomodachi_outline
import tomodachi_db

logging.basicConfig(level=logging.INFO)


def build_user_string(message):
    user_info = [
        str(message.from_user.id),
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
    ]
    return '\n'.join(filter(None, user_info))


def build_provider_data():
    data = {
        "receipt": {
            "items": [{
                "description": "Tomodachi VPN 1 month 30GB",
                "quantity": "1.00",
                "amount": {"value": "169.00", "currency": "RUB"},
                "vat_code": 1
            }]
        }
    }
    return json.dumps(data)


def build_download_string():
    return (
        "- <a href='https://itunes.apple.com/ru/app/outline-app/id1356177741'>iOS</a>\n"
        "- <a href='https://play.google.com/store/apps/details?id=org.outline.android.client'>Android</a>\n"
        "- <a href='https://itunes.apple.com/ru/app/outline-app/id1356178125'>MacOS</a>\n"
        "- <a href='https://raw.githubusercontent.com/Jigsaw-Code/outline-releases/master/client/stable/Outline-Client.exe'>Windows</a>\n"
        "- <a href='https://raw.githubusercontent.com/Jigsaw-Code/outline-releases/master/client/stable/Outline-Client.AppImage'>Linux (AppImage)</a>\n"
    )


def build_key_description(key, location):
    try:
        usage_gb = round(tomodachi_outline.get_key_traffic(
            tomodachi_db.get_single_server(location), key[3]) / 1000000000, 2)
        limit_gb = round(key[7] / 1000000000, 2)
        return (
            f"{key[1]}\n"
            f"{key[4]}\n"
            f"Expires {key[6]}\n"
            f"Spent {usage_gb} GB out of {limit_gb} GB"
        )
    except Exception as e:
        logging.error(f"Error getting key data: {e}")
        return "Error getting key data"
