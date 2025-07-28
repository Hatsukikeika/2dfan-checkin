import json
from requests_html import AsyncHTMLSession
from recaptcha import CaptchaInterface
from bs4 import BeautifulSoup

def _recap(captcha_interface: CaptchaInterface):
    return captcha_interface.cap(
        websiteURL='https://2dfan.com/',
        websiteKey='6LdUG0AgAAAAAAfSmLDXGMM7XKYMTItv87seZUan',
        pageAction="checkin",
        isInvisible=True,
    )

class User: 
    id: str
    host: str
    session: AsyncHTMLSession
    captcha_interface: CaptchaInterface

    def __init__(self, id: str, session: str, captcha_interface: CaptchaInterface, host="2dfan.com") -> None:
        self.id = id
        self.host = host
        self.session = AsyncHTMLSession()
        self.session.headers.update({
            'accept': '*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript',
            'accept-language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': f'https://{host}',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': f'https://{host}/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        })
        self.session.cookies.update({
            '_project_hgc_session': session, 
            'pop-blocked': 'true',
            '_ga_RF77TZ6QMN': 'GS1.1.1737081048.3.1.1737081780.0.0.0',
            '_ga': 'GA1.1.1480083206.1736996753',
        })
        self.captcha_interface = captcha_interface

    async def get_authenticity_token(self):
        try:
            resp = await self.session.get(url=f"https://2dfan.com/users/{self.id}/recheckin")
            await resp.html.arender(wait=30)

            new_cookie = resp.cookies.get_dict('2dfan.com')
            for key in new_cookie.keys():
                self.session.cookies.set(key, new_cookie[key])
            h5 = BeautifulSoup(resp.text, 'html.parser')
            token: str = h5.find('input', attrs={'name': 'authenticity_token'}).attrs['value']
            return token
        finally:
            await self.session.close()

    class CheckinResult:
        checkins_count: int 
        serial_checkins: int 
        def __init__(self, checkins_count: int, serial_checkins: int) -> None:
            self.checkins_count = checkins_count 
            self.serial_checkins = serial_checkins 
        def from_json(json_str: str): 
            data = json.loads(json_str)
            return User.CheckinResult(**data)
        
    def create_cf_token(self, rqData: dict= {}) -> str:
        return self.captcha_interface.tft(
            websiteURL=f"https://{self.host}/users/{self.id}/recheckin",
            websiteKey="0x4AAAAAAAju-ZORvFgbC-Cd",
            rqData = {
                'mode':'',
                'metadataAction': 'checkin',
                'metadataCdata': '',
            },
        )

    async def checkin(self) -> CheckinResult: 
        auth_token = await self.get_authenticity_token()
        cf_token = self.create_cf_token()
        response = await self.session.post(url= f'https://{self.host}/checkins', headers={
            'referer': f"https://{self.host}/users/{self.id}/recheckin",
            'x-csrf-token': auth_token,
        }, data={
            'cf-turnstile-response': cf_token,
            'authenticity_token': auth_token,
            'format': 'json',
        }) 
        if response.status_code != 200:
            raise ValueError(response.text)
        return User.CheckinResult.from_json(response.text) 
