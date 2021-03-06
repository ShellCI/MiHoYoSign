try:
    # 优先使用httpx，在httpx无法使用的环境下使用requests
    import httpx

    http = httpx.Client(timeout=10, transport=httpx.HTTPTransport(retries=5))
    # 当openssl版本小于1.0.2的时候直接进行一个空请求让httpx报错
    import tools
    if tools.get_openssl_version() <= 102:
        httpx.get()
except:
    import requests
    from requests.adapters import HTTPAdapter
    http = requests.Session()
    http.mount('http://', HTTPAdapter(max_retries=5))
    http.mount('https://', HTTPAdapter(max_retries=5))


# 这里实际上应该加个"-> dict"但是考虑到请求可能失败的关系，所以直接不声明返回变量
def get(url: str, **headers: dict):
    try:
        req = http.get(url, headers=headers)
        return req.json()
    except:
        print("请求失败，网络错误！")
        return ""


def post(url: str, data: dict, **headers: dict):
    try:
        req = http.post(url, data=data, headers=headers)
        return req.json()
    except:
        print("请求失败，网络错误！")
        return ""


def post_json(url: str, json, **headers: dict):
    try:
        req = http.post(url, json=json, headers=headers)
        return req.json()
    except:
        print("请求失败，网络错误！")
        return ""
