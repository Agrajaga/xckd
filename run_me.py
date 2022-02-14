import os
from random import randint

import requests
from dotenv import load_dotenv


def get_xkcd_last_num() -> int:
    xkcd_url = f"https://xkcd.com/info.0.json"
    response = requests.get(xkcd_url)
    response.raise_for_status()
    return int(response.json()["num"])


def get_xkcd_comic(comic_id: int) -> tuple[str, str]:
    xkcd_url = f"https://xkcd.com/{comic_id}/info.0.json"
    response = requests.get(xkcd_url)
    response.raise_for_status()
    comic_description = response.json()

    comic_comment = comic_description["alt"]
    comic_url = comic_description["img"]

    response = requests.get(comic_url)
    response.raise_for_status()

    filename = "tmp_img.png"
    with open(filename, "wb") as file:
        file.write(response.content)

    return (comic_comment, filename)


def call_vk_api_method(
    access_token: str,
    method: str,
    method_params: dict = {}
) -> requests.Response:
    api_params = {
        "access_token": access_token,
        "v": "5.131",
    }
    method_url = f"https://api.vk.com/method/{method}"

    response = requests.get(method_url, params=api_params | method_params)
    response.raise_for_status()
    return response


def post_vk_wall_photo(
    token: str,
    group_id: str,
    title: str,
    photo_filename: str
) -> None:
    method_params = {
        "group_id": group_id,
    }
    response = call_vk_api_method(
        access_token=token,
        method="photos.getWallUploadServer",
        method_params=method_params
    )
    upload_url = response.json()["response"]["upload_url"]

    with open(photo_filename, "rb") as file:
        files = {
            "photo": file,
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()

    method_params.update(response.json())
    response = call_vk_api_method(
        access_token=token,
        method="photos.saveWallPhoto",
        method_params=method_params
    )

    save_photo_response = response.json()["response"][0]
    owner_id = save_photo_response["owner_id"]
    photo_id = save_photo_response["id"]

    method_params = {
        "owner_id": f"-{group_id}",
        "from_group": 1,
        "message": title,
        "attachments": f"photo{owner_id}_{photo_id}",
    }
    response = call_vk_api_method(
        access_token=token,
        method="wall.post",
        method_params=method_params
    )


if __name__ == "__main__":
    load_dotenv()
    vk_token = os.getenv("VK_ACCESS_TOKEN")
    group_id = os.getenv("VK_GROUP_ID")

    comic_id = randint(1, get_xkcd_last_num())
    comic_comment, comic_filename = get_xkcd_comic(comic_id=comic_id)

    post_vk_wall_photo(
        token=vk_token,
        group_id=group_id,
        title=comic_comment,
        photo_filename=comic_filename
    )

    os.remove(comic_filename)
