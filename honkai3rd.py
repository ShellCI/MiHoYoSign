import time
import tools
import config
import random
import setting
from request import http
from loghelper import log
from error import CookieError


class Honkai3rd:
    def __init__(self) -> None:
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'DS': tools.get_ds(web=True, web_old=True),
            'Origin': 'https://webstatic.mihoyo.com',
            'x-rpc-app_version': setting.mihoyobbs_Version_old,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.3.0',
            'x-rpc-client_type': setting.mihoyobbs_Client_type_web,
            'Referer': f'https://webstatic.mihoyo.com/bh3/event/euthenia/index.html?bbs_presentation_style=fullscreen'
                       f'&bbs_game_role_required=bh3_cn&bbs_auth_required=t'
                       f'rue&act_id={setting.honkai3rd_Act_id}&utm_source=bbs&utm_medium=mys&utm_campaign=icon',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.mihoyo.hyperion',
            "Cookie": config.mihoyobbs_Cookies,
            'x-rpc-device_id': tools.get_device_id()
        }
        self.acc_List = self.get_account_list()
        self.sign_day = 0

    # 获取绑定的账号列表
    def get_account_list(self) -> list:
        log.info("正在获取米哈游账号绑定的崩坏3账号列表...")
        temp_list = []
        req = http.get(setting.honkai3rd_Account_info_url, headers=self.headers)
        data = req.json()
        if data["retcode"] != 0:
            log.warning("获取账号列表失败！")
            config.honkai3rd_Auto_sign = False
            config.save_config()
            raise CookieError("BBS Cookie Error")
        for i in data["data"]["list"]:
            temp_list.append([i["nickname"], i["game_uid"], i["region"]])
        log.info(f"已获取到{len(temp_list)}个崩坏3账号信息")
        return temp_list

    # 获取今天已经签到了的dict
    def get_today_item(self, raw_data: list):
        # 用range进行循环，当status等于0的时候上一个就是今天签到的dict
        for i in range(len(raw_data)):
            if raw_data[i]["status"] == 0:
                self.sign_day = i - 1
                return raw_data[i - 1]
            self.sign_day = i
            if raw_data[i]["status"] == 1:
                return raw_data[i]
            if i == int(len(raw_data) - 1) and raw_data[i]["status"] != 0:
                return raw_data[i]

    # 签到
    def sign_account(self):
        return_data = "崩坏3："
        if len(self.acc_List) == 0:
            log.warning("账号没有绑定任何崩坏3账号！")
            return_data += "\n并没有绑定任何崩坏3账号"
        else:
            for i in self.acc_List:
                log.info(f"正在为舰长 {i[0]} 进行签到...")
                req = http.get(setting.honkai3rd_Is_signurl.format(setting.honkai3rd_Act_id, i[2], i[1]), headers=self.headers)
                data = req.json()
                re_message = ""
                if data["retcode"] != 0:
                    re_message = f"舰长 {i[0]} 获取账号签到信息失败！"
                    log.warning(re_message)
                    print(req.text)
                    continue
                today_item = self.get_today_item(data["data"]["sign"]["list"])
                # 判断是否已经签到
                if today_item["status"] == 0:
                    re_message = f"舰长 {i[0]} 今天已经签到过了~\t已连续签到{self.sign_day}天\t今天获得的奖励是{tools.get_item(today_item)}"
                    log.info(re_message)
                else:
                    time.sleep(random.randint(2, 8))
                    req = http.post(url=setting.honkai3rd_SignUrl, headers=self.headers,
                                    json={'act_id': setting.honkai3rd_Act_id, 'region': i[2], 'uid': i[1]})
                    data = req.json()
                    if data["retcode"] == 0:
                        today_item = self.get_today_item(data["data"]["list"])
                        re_message = f"舰长 {i[0]} 签到成功~\t已连续签到{self.sign_day}天\t今天获得的奖励是{tools.get_item(today_item)}"
                        log.info(re_message)
                    elif data["retcode"] == -5003:
                        re_message = f"舰长 {i[0]} 今天已经签到过了~\t已连续签到{self.sign_day}天\t今天获得的奖励是{tools.get_item(today_item)}"
                        log.info(re_message)
                    else:
                        re_message = f"舰长 {i[0]} 本次签到失败！"
                        log.warning(re_message)
                        print(req.text)
                return_data += re_message
        return return_data
