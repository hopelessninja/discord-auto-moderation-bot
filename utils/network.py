from requests import get
from config.settings import BASE_URL, API_KEY

def fetch(*, url, headers):
    """
    Send a GET request and return response as python object
    """

    response = get(url, headers=headers)
    return response.json()


def make_api_url(module, action, address, **kwargs):
    url = BASE_URL+f"?module={module}&action={action}&address={address}&apikey={API_KEY}"
    for key, value in kwargs.items():
        url += f"&{key}={value}"

        return url