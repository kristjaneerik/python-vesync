import requests
import hashlib
import json

requests.packages.urllib3.disable_warnings()

BASE_URL = "https://smartapi.vesync.com"


class VesyncApi(object):
    def __init__(self, username, password):
        payload = json.dumps({
            "account": username,
            "devToken": "",
            "password": hashlib.md5(password.encode('utf-8')).hexdigest()
        })
        account = requests.post(BASE_URL + "/vold/user/login", verify=False, data=payload).json()
        if "error" in account:
            raise RuntimeError("Invalid username or password")
        else:
            self._account = account
        self._devices = []
        self._name2id = {}
        self._headers = {'tk': self._account["tk"], 'accountid': self._account["accountID"]}

    def get_devices(self, force_update=False):
        if force_update or not self._devices:
            print("# GRABBING DEVICES")
            self._devices = requests.get(BASE_URL + '/vold/user/devices', verify=False,
                                         headers=self._headers).json()
        return self._devices

    def turn_on(self, device_id):
        requests.put(BASE_URL + '/v1/wifi-switch-1.3/' + device_id + '/status/on', verify=False,
                     data={}, headers=self._headers)

    def turn_off(self, device_id):
        requests.put(BASE_URL + '/v1/wifi-switch-1.3/' + device_id + '/status/off', verify=False,
                     data={}, headers=self._headers)

    def turn_on_by_name(self, device_name, force_update=False):
        self.turn_on(self.name2id(device_name))

    def turn_off_by_name(self, device_name, force_update=False):
        self.turn_off(self.name2id(device_name))

    def name2id(self, device_name, force_update=False):
        if force_update or device_name not in self._name2id:
            for device in self.get_devices():
                if device['deviceName'] == device_name:
                    self._name2id[device_name] = device['cid']
                    break
            else:
                raise ValueError('Unknown device name')
        return self._name2id[device_name]
