import os
from random import randint

import requests
from dotenv import load_dotenv


def get_xkcd_last_num() -> int:
    xkcd_url = "https://xkcd.com/info.0.json"
    response = requests.get(xkcd_url)
    response.raise_for_status()
    return int(response.json()["num"])


def get_xkcd_comic_description(comic_id: int) -> tuple[str, str]:
    xkcd_url = f"https://xkcd.com/{comic_id}/info.0.json"
    response = requests.get(xkcd_url)
    response.raise_for_status()
    response_payload = response.json()

    comic_comment = response_payload["alt"]
    comic_url = response_payload["img"]
    return (comic_comment, comic_url)


def fetch_xkcd_comic(comic_url: str, filename: str) -> None:
    response = requests.get(comic_url)
    response.raise_for_status()
    with open(filename, "wb") as file:
        file.write(response.content)


class VK_error(Exception):
    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"VK error: {self.code}: {self.message}"


def handle_vk_error(content: dict) -> None:
    vk_error = content.get("error")
    if vk_error:
        raise VK_error(vk_error["error_code"], vk_error["error_msg"])


def call_vk_api_method(
    access_token: str,
    method: str,
    method_params: dict = {}
) -> dict:
    api_params = {
        "access_token": access_token,
        "v": "5.131",
    }
    method_url = f"https://api.vk.com/method/{method}"

    response = requests.get(method_url, params=api_params | method_params)
    response.raise_for_status()
    content = response.json()
    handle_vk_error(content)
    return content


def post_vk_wall_photo(
    token: str,
    group_id: str,
    title: str,
    photo_filename: str
) -> None:
    method_params = {
        "group_id": group_id,
    }
    answer = call_vk_api_method(
        access_token=token,
        method="photos.getWallUploadServer",
        method_params=method_params
    )
    upload_url = answer["response"]["upload_url"]

    with open(photo_filename, "rb") as file:
        files = {
            "photo": file,
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()

    method_params.update(response.json())
    answer = call_vk_api_method(
        access_token=token,
        method="photos.saveWallPhoto",
        method_params=method_params
    )

    save_photo_response = answer["response"][0]
    owner_id = save_photo_response["owner_id"]
    photo_id = save_photo_response["id"]

    method_params = {
        "owner_id": f"-{group_id}",
        "from_group": 1,
        "message": title,
        "attachments": f"photo{owner_id}_{photo_id}",
    }
    answer = call_vk_api_method(
        access_token=token,
        method="wall.post",
        method_params=method_params
    )


if __name__ == "__main__":
    load_dotenv()
    vk_token = os.getenv("VK_ACCESS_TOKEN")
    group_id = os.getenv("VK_GROUP_ID")
    temp_filename = "tmp_img.png"

    try:
        comic_id = randint(1, get_xkcd_last_num())
        comic_comment, comic_url = get_xkcd_comic_description(
            comic_id=comic_id)
        fetch_xkcd_comic(comic_url=comic_url, filename=temp_filename)
    except requests.exceptions.HTTPError as error:
        print(f"An error occurred while fetching the comic: \
                    {error.response.status_code} {error.response.reason}")
    except requests.exceptions.Timeout:
        print("An error occurred while fetching the comic: Timeout expired")

    try:
        post_vk_wall_photo(
            token=vk_token,
            group_id=group_id,
            title=comic_comment,
            photo_filename=temp_filename
        )
    except VK_error as error:
        print(f"An error occurred while posting the comic: {error}")
    except requests.exceptions.HTTPError as error:
        print(f"An error occurred while posting the comic: \
                    {error.response.status_code} {error.response.reason}")
    except requests.exceptions.Timeout:
        print("An error occurred while posting the comic: Timeout expired")
    finally:
        os.remove(temp_filename)
