# Posting xkcd comics in VK

Don't you know what xkcd is? Calm down, I'll explain. This is a webcomic of romance,
sarcasm, math, and language.

This script publishes a random comic from [xkcd.com](https://xkcd.com/) on the wall in the VK group.

### How to run

To run the script, type:
```
$ python run_me.py
```
After executing the script, you will receive a new post in the group:
![image](https://user-images.githubusercontent.com/22379662/153935424-a6895e6a-cea7-4f1f-ae59-a881f02c3164.png)

### How to install

Python3 should be already installed. 
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```


To use the API VK, you need to [create the application](https://vk.com/editapp?act=create) and get the [access_token](https://vk.com/dev/implicit_flow_user).
You will need the following access rights:  `photos, groups, wall, offline`.

Get your VK group id [here](https://regvk.com/id/)

Create a file `.env` and put your `access_token` and `group_id` in it:
```
VK_ACCESS_TOKEN=<your_access_token>
VK_GROUP_ID=<your_group_id>
```

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
