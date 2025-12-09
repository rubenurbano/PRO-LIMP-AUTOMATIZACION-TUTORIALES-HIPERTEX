import shotstack_sdk as shotstack
from shotstack_sdk.api import edit_api
from shotstack_sdk.model.title_asset import TitleAsset
from shotstack_sdk.model.clip import Clip
from shotstack_sdk.model.track import Track
from shotstack_sdk.model.timeline import Timeline
from shotstack_sdk.model.output import Output
from shotstack_sdk.model.edit import Edit

# ⚠️ Tu API key de SANDBOX/Stage (la larga)
API_KEY = "7dnVX36CM1I1BwB2nYaQrKoMUc7ezc2HZmuAMWdl"

# ⚠️ Endpoint correcto de sandbox/stage
HOST = "https://api.shotstack.io/edit/stage"

configuration = shotstack.Configuration(host=HOST)
configuration.api_key["DeveloperKey"] = API_KEY

with shotstack.ApiClient(configuration) as api_client:
    api_instance = edit_api.EditApi(api_client)

    title_asset = TitleAsset(
        text="Hola Rubén!",
        style="minimal",
        size="small",
    )

    clip = Clip(
        asset=title_asset,
        start=0.0,
        length=3.0,
    )

    track = Track(clips=[clip])
    timeline = Timeline(background="#000000", tracks=[track])

    output = Output(format="mp4", resolution="sd")

    edit = Edit(timeline=timeline, output=output)

    try:
        api_response = api_instance.post_render(edit)
        render_id = api_response["response"]["id"]
        print("RENDER ID:", render_id)
    except Exception as e:
        print("Error:", e)
