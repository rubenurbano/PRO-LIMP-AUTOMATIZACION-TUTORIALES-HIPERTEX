import shotstack_sdk as shotstack
from shotstack_sdk.api import edit_api

API_KEY = "7dnVX36CM1I1BwB2nYaQrKoMUc7ezc2HZmuAMWdl"   # misma key
HOST = "https://api.shotstack.io/edit/stage"

RENDER_ID = "15d44e80-532a-49ff-b8f9-fe22a238b2f8"     # el ID de recién

configuration = shotstack.Configuration(host=HOST)
configuration.api_key["DeveloperKey"] = API_KEY

with shotstack.ApiClient(configuration) as api_client:
    api_instance = edit_api.EditApi(api_client)

    try:
        api_response = api_instance.get_render(RENDER_ID, data=False, merged=True)
        resp = api_response["response"]

        print("STATUS:", resp["status"])

        if resp["status"] == "done":
            print("URL:", resp["url"])

    except Exception as e:
        print("Error:", e)

