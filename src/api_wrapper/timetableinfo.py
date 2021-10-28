import request
from src.api_wrapper.data import u,p

class api_interface():
    adress : str
    endp : str
    conID : str
    data: list

    def get_information(self):
        pass

class timetable_info(api_interface):
    adress : str = "https://developer.sbb.ch/apis/b2p/information"
    endp : str = "https://sso-int.sbb.ch/auth/realms/SBB_Public/protocol/openid-connect/token"
    conID : str = "PLY223P"


class journey_maps_serivce(api_interface):
    adress: str
    endp: str
    conID: str


class journey_maps_routing(api_interface):
    adress: str
    endp: str
    conID: str


class swiss_topo_maps(api_interface):
    adress: str
    endp: str
    conID: str


class weather_forcast(api_interface):
    adress: str
    endp: str
    conID: str

class outdoor_active(api_interface):
    adress: str
    endp: str
    conID: str

class UMTS_3G_coverage(api_interface):
    adress: str
    endp: str
    conID: str


r = request.get(timetable_info.adress, auth=(u, p))

print(r.status_code)
print(r.text)