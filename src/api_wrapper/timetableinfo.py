import json
import requests
from requests.auth import HTTPBasicAuth
from src.api_wrapper.data import u,p, s_key, m_key, t_key
from collections import OrderedDict
import xml.etree.ElementTree as ET
from requests.auth import AuthBase

class TokenAuth(AuthBase):
    """Implements a custom authentication scheme."""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        """Attach an API token to a custom auth header."""
        r.headers['X-TokenAuth'] = f'{self.token}'  # Python 3.6+
        return r



class api_interface():
    adress : str
    endp : str
    conID : str
    data: list

    @staticmethod
    def get_information():
        pass

class timetable_info(api_interface):
    """
    "https://b2p-int.api.sbb.ch/"
    """
    adress = "https://b2p.api.sbb.ch/api/"
    tokenAdress : str = "https://sso-int.sbb.ch/auth/realms/SBB_Public/protocol/openid-connect/token"
    user : str = "af929f08"
    conID: str = 'PLY223P'
    accessToken :str = ""

    @staticmethod
    def get_token():
        """
        ##curl -X POST \
        # 'https://sso.sbb.ch/auth/realms/SBB_Public/protocol/openid-connect/token' \
        # -d 'grant_type=client_credentials&client_id=$clientId&client_secret=$clientSecret'
        :return:
        """
        credential ={
            "grant_type":'client_credentials',
            "client_id": timetable_info.user,
            "client_secret": t_key
        }
        r = requests.post(url=timetable_info.tokenAdress, data=credential)
        print(r.url)
        print(r.status_code)
        print(r.text)
        timetable_info.accessToken = json.loads(r.text)['error']
        print(timetable_info.accessToken)

    @staticmethod
    def get_locationRequest(location="Bern")->dict:
        """
        url -X GET \
         'https://b2p.api.sbb.ch/api/locations?name=Bern' \
         -H 'Authorization: Bearer $accessToken' \
         -H 'Cache-Control: no-cache' \
         -H 'Accept: application/json' \
         -H 'X-Contract-Id: ABC1234' \
         -H 'X-Conversation-Id: e5eeb775-1e0e-4f89-923d-afa780ef844b

        """
        headers ={
            "Authorization:":'Bearer '+timetable_info.accessToken,
            "Cache-Control:": "no-cache",
            "Accept:": "application/json",
            "X-Contract-Id": timetable_info.conID,
            "X-Conversation-ID": "fun"
        }
        r = requests.get(url=timetable_info.adress+'/locations?name='+location, headers=headers)
        print(r.url)
        print(r.status_code)
        print(r.text)
        return json.loads(r.text)

class journey_maps_serivce(api_interface):
    style: str = "base_bright_v2" #"base_dark_v2
    adress: str = "https://journey-maps-tiles.geocdn.sbb.ch/styles/"+style+"/style.json?api_key="


    @staticmethod
    def get_information()->dict:
        r = requests.get(url=journey_maps_serivce.adress + s_key,)
        return json.loads(r.text)


"""
helper functions:
"""
## transfer
def generate_transfer_dict(client:str= "polyhack", clientVersion:str="1.0.0", lang="de", fromStationID:int=8503000,
                           fromTrack:str="L", toStationID:int=8507000, toTrack:int = 10,
                           indoor:bool=True, fromTransportType:str="bus", toTransportType:str="train")-> OrderedDict:
    """
    Helper for inOrder https request.

    :param client:
    :param clientVersion:
    :param lang:
    :param fromStationID:
    :param fromTrack:
    :param toStationID:
    :param toTrack:
    :param indoor:
    :param fromTransportType:
    :param toTransportType:
    :return:
    """
    return OrderedDict({"client": client,
                     "clientVersion": clientVersion,
                     "lang": lang,
                     "fromStationID": fromStationID,
                     "fromTrack": fromTrack,
                     "toStationID": toStationID,
                     "toTrack": toTrack,
                     "indoor": indoor,
                     "fromTransportType": fromTransportType,
                     "toTransportType": toTransportType})

def generate_route_dict(fromStationID:int=8503000, toStationID:int=8507000, mot:str="train")-> OrderedDict:
    """
    Helper for inOrder https request.

    :param fromStationID:
    :param toStationID:
    :param mot:
    :return:
    """
    return OrderedDict({"fromStationID": fromStationID,
                         "toStationhID": toStationID,
                         "mot": mot})

class journey_maps_routing(api_interface):
    header = {"x-api-key": m_key, }
    adress: str = "https://journey-maps.api.sbb.ch:443"

    @staticmethod
    def get_route_information(route:OrderedDict):
        request_url = journey_maps_routing.adress + '/v1/route?' + "&".join(
            [str(k) + "=" + str(v) for k, v in route.items()])
        r = requests.get(request_url, headers=journey_maps_routing.header)

        print(r.url)
        print(r.status_code)
        print(r.text)
        #return json.load(r.text)

    @staticmethod
    def get_transfer_information(transfer:OrderedDict):
        request_url = journey_maps_routing.adress + '/v1/transfer?' + "&".join(
            [str(k) + "=" + str(v) for k, v in transfer.items()])
        r = requests.get(request_url, headers=journey_maps_routing.header)

        print(r.url)
        print(r.status_code)
        print(r.text)
        #return json.load(r.text)

class swiss_topo_maps(api_interface):
    adress: str


class weather_forcast(api_interface):
    adress: str = "https://weather.api.sbb.ch/"


class outdoor_active(api_interface):
    adress: str = "http://developers.outdooractive.com/Overview/"


class UMTS_3G_coverage(api_interface):
    adress: str

class Journey_service(api_interface):
    adress: str

class POI_service(api_interface):
    adress: str



if __name__ == "__main__":
    #SBB Timetables:
    #Todo: does not work! - Need Client registration! https://b2p-int.app.sbb.ch/docs/index.html
    #timetable_info.get_token()
    #json_dict = timetable_info.get_locationRequest()
    #print(json_dict)

    #journey_maps
    # Works
    #json_dict = journey_maps_serivce.get_information()
    #print(json_dict)

    #journey_route
    ## route
    # Todo: does not work! - A bug on the server side?
    #https: // journey - maps.api.sbb.ch: 443 / v1 / route?fromStationID = 8503000 & toStationhID = 8507000 & mot = train
    #500
    #{"status": 500, "message": "[2006288006] Unexpected error occurred."}
    journey_maps_routing.get_route_information(generate_route_dict())

    ##transfer:
    #visualize -> https://geojson.io/#map=10/47.1941/7.9879
    # Works!
    #geoJson_dict = journey_maps_routing.get_route_information(generate_transfer_dict())

    # Map Swisstopo

    #weather api

    #Outdoor activity


    #3G-UMTS Coverage
    #root_node = ET.

    #Points of Interests – POI-Service.
