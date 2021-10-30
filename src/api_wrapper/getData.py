import json, os
import requests
import uuid
from datetime import timezone, date, datetime, time
from requests.auth import HTTPBasicAuth
from src.api_wrapper.data import s_key, m_key, t_key, w_key
from collections import OrderedDict
import xml.etree.ElementTree as ET
from requests.auth import AuthBase
from src.api_wrapper import UGM_3G_data

class api_interface():
    adress : str
    def __init__(self):
        pass

def generate_trip_dict(date:date=date.fromisoformat('2021-10-29'),
                       time:time=time.fromisoformat("19:44"),
                       originId:int=8591122, destinationId:int=8591123)-> OrderedDict:
    """
    Helper for inOrder https request.

    :param fromStationID:
    :param toStationID:
    :param mot:
    :return:
    """
    return OrderedDict({"date": str(date),
                         "time": str(time.hour)+":"+str(time.minute),
                         "originId": str(originId),
                         "destinationId":str(destinationId)})

class timetable_info(api_interface):
    """
    "https://b2p-int.api.sbb.ch/"
    """
    adress = "https://b2p-int.api.sbb.ch/api"
    tokenAdress : str = "https://sso-int.sbb.ch/auth/realms/SBB_Public/protocol/openid-connect/token"
    user : str = "af929f08"
    conID: str = 'PLY223P'
    accessToken :str = ""
    token_timestamp = None

    def __init__(self):
        self.get_token()

    def get_token(self):
        """
        ##curl -X POST \
        # 'https://sso.sbb.ch/auth/realms/SBB_Public/protocol/openid-connect/token' \
        # -d 'grant_type=client_credentials&client_id=$clientId&client_secret=$clientSecret'
        :return:
        """
        delta = (self.token_timestamp-date.today())/60 > 30 if(not self.token_timestamp is None) else True
        if(delta):
            credential ={
                "grant_type":'client_credentials',
                "client_id": self.user,
                "client_secret": t_key
            }
            r = requests.post(url=self.tokenAdress, data=credential).json()
            self.token_request = r
            self.token_timestamp = date.today()
            self.accessToken = r['access_token']
            print("recived Token")
            print(self.accessToken)
        else:
            print("token was still valid")

    def get_locationRequest(self, location="Bern")->dict:
        """
        url -X GET \
         'https://b2p.api.sbb.ch/api/locations?name=Bern' \
         -H 'Authorization: Bearer $accessToken' \
         -H 'Cache-Control: no-cache' \
         -H 'Accept: application/json' \
         -H 'X-Contract-Id: ABC1234' \
         -H 'X-Conversation-Id: e5eeb775-1e0e-4f89-923d-afa780ef844b

        """
        self.get_token()

        query = {"name": location}
        self.conv_id = uuid.uuid4()  # conversation Id
        auth ={
            "Authorization": f"Bearer {self.accessToken}",
            "X-Contract-Id": self.conID,
            "X-Conversation-ID": str(self.conv_id)
        }
        self.r = requests.get(url=self.adress+'/locations', headers=auth, params=query)
        #print(self.r.url)
        #print(self.r.status_code)
        #print(self.r.text)
        return json.loads(self.r.text)

    def get_tripRequest(self, trip:OrderedDict=generate_trip_dict())->dict:
        """
        url -X GET \
         'https://b2p.api.sbb.ch/api/locations?name=Bern' \
         -H 'Authorization: Bearer $accessToken' \
         -H 'Cache-Control: no-cache' \
         -H 'Accept: application/json' \
         -H 'X-Contract-Id: ABC1234' \
         -H 'X-Conversation-Id: e5eeb775-1e0e-4f89-923d-afa780ef844b

        """
        self.get_token()

        print(trip)

        self.conv_id = uuid.uuid4()  # conversation Id
        auth ={
            "Authorization": f"Bearer {self.accessToken}",
            "X-Contract-Id": self.conID,
            "X-Conversation-ID": str(self.conv_id)
        }
        #print("auth conversation id: " + str(self.conv_id))
        self.r = requests.get(url=self.adress+'/trips', headers=auth, params=dict(trip))
        print(self.r.url)
        print(self.r.status_code)
        print(self.r.text)
        return json.loads(self.r.text)


class journey_maps_serivce(api_interface):
    style: str = "base_bright_v2" #"base_dark_v2
    adress: str = "https://journey-maps-tiles.geocdn.sbb.ch/styles/"+style+"/style.json?api_key="


    def get_information(self)->dict:
        self.r = requests.get(url=self.adress + s_key,)
        return json.loads(self.r.text)


"""
helper functions:
"""
## transfer
def generate_transfer_dict2(client:str= "polyhack", clientVersion:str="1.0.0", lang="de", fromStationID:int=8503000,
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

def generate_transfer_dict(fromStationID:int=8503000, toStationID:int=8507000, mot:str= "train", \
        lang:str='de', client:str='sbb-mobile-web-prod', clientVersion:int=1)-> OrderedDict:
    """
    Helper for inOrder https request.

    :param fromStationID:
    :param toStationID:
    :param mot:
    :return:
    """
    return OrderedDict({"fromStationID": fromStationID,
                         "toStationID": toStationID,
                         "mot": mot,
                         "lang": lang,
                         "client": client,
                         "clientVersion": clientVersion})


class journey_maps_routing(api_interface):
    header = {"x-api-key": m_key, }
    adress: str = "https://journey-maps.api.sbb.ch:443"


    def get_route_information(self, route:OrderedDict):
        request_url = self.adress + '/v1/route?' + "&".join(
            [str(k) + "=" + str(v) for k, v in route.items()])
        self.r = requests.get(request_url, headers=self.header)

        print(self.r.url)
        print(self.r.status_code)
        print(self.r.text)
        return json.load(self.r.text)


    def get_transfer_information(self, transfer:OrderedDict):
        request_url = self.adress + '/v1/transfer'

        self.r = requests.get(request_url, headers=self.header, params=transfer)

        print(self.r.url)
        print(self.r.status_code)
        print(self.r.text)
        return json.loads(self.r.text)


class swiss_topo_maps(api_interface):
    adress: str

def get_weather_request(time:datetime=datetime.fromisoformat('2021-10-29T00:00:00'), parameters:str=['t_2m:C','relative_humidity_2m:p'],
                        location:str=[47.4245,9.3767])->OrderedDict:
    return OrderedDict({"validateTime":str(time.astimezone().isoformat()),
                        "parameters":str(",".join(parameters)),
                        "location":str(",".join(map(str, location)))})

class weather_forcast(api_interface):
    """
        adress = 'https://api.meteomatics.com/<validdatetime>/<parameters>/<location>/<format>?<optionals>'
        https://api.meteomatics.com/2021-10-29T00:00:00ZP1D:PT1H/t_2m:C,relative_humidity_2m:p/47.4245,9.3767/html?model=mix
    """
    #adress: str = "https://weather.api.sbb.ch/"
    adress = 'https://api.meteomatics.com'
    ci = '56bae62c'
    tokenAdress : str = "https://sso-int.sbb.ch/auth/realms/SBB_Public/protocol/openid-connect/token"
    token_timestamp = None
    user : str = "af929f08"

    def get_token(self):
        """
        ##curl -X POST \
        # 'https://sso.sbb.ch/auth/realms/SBB_Public/protocol/openid-connect/token' \
        # -d 'grant_type=client_credentials&client_id=$clientId&client_secret=$clientSecret'
        :return:
        """
        delta = (self.token_timestamp-date.today())/60 > 30 if(not self.token_timestamp is None) else True
        if(delta):
            credential ={
                "grant_type":'client_credentials',
                "client_id":self.user,
                "client_secret": t_key
            }
            r = requests.post(url=self.tokenAdress, data=credential).json()
            print(r)
            self.token_request = r
            self.token_timestamp = date.today()
            self.accessToken = r['access_token']
            print("recived Token")
            print(self.accessToken)
        else:
            print("token was still valid")


    def get_weather(self, weather_request:OrderedDict):
        print(weather_request)
        auth ={
            "Authorization": f"Bearer {self.accessToken}",
            "'Accept": "application/json",
            #"X-Contract-Id": self.conID,
            #"X-Conversation-ID": str(self.conv_id)
        }
        credential = {
            "grant_type": 'client_credentials',
            "client_id": self.user,
            "client_secret": t_key
        }
        request_url = self.adress+"/"+weather_request['validateTime']+"/"+weather_request['parameters']+"/"+weather_request['location']+"/html?model=mix"
        self.r = requests.get(request_url, data=credential) #, headers=auth
        return self.r.text


class outdoor_active(api_interface):
    adress: str = "http://developers.outdooractive.com/Overview/"



class UMTS_3G_coverage(api_interface):
    adress: str
    data_dir_path = os.path.dirname(UGM_3G_data.__file__)
    data_gm_path = data_dir_path+"/Metadata_gm03.xml"
    data_iso_path = data_dir_path+"/Metadata_gm03.xml"

    def load(self):
        self.xTree = ET.parse(self.data_iso_path)


class Journey_service(api_interface):
    adress: str


class POI_service(api_interface):
    adress: str



if __name__ == "__main__":
    #SBB Timetables:
    # Works!
    #timetable = timetable_info()
    #timetable.get_token()
    #json_dict = timetable.get_locationRequest()
    #json_dict = timetable.get_tripRequest(trip=generate_trip_dict())
    print(json_dict)


    #journey_maps
    # Works
    #j_service = journey_maps_serivce()
    #json_dict = j_service.get_information()
    #print(json_dict)

    #journey_route
    ## route
    # Todo: does not work! - A bug on the server side?
    #https: // journey - maps.api.sbb.ch: 443 / v1 / route?fromStationID = 8503000 & toStationhID = 8507000 & mot = train
    #500
    #{"status": 500, "message": "[2006288006] Unexpected error occurred."}
    #jmR = journey_maps_routing()
    #json_dict = jmR.get_route_information(generate_route_dict())
    #print(json_dict)

    ##transfer:
    #visualize -> https://geojson.io/#map=10/47.1941/7.9879
    # Works!
    #geoJson_dict = jmR.get_route_information(generate_transfer_dict())
    #print(geoJson_dict)

    # Map Swisstopo
    #print(UGM_3G_data.__file__)
    #u3GD = UMTS_3G_coverage()
    #u3GD.load() #Todo: needs to be further parsed
    #print(vars(u3GD.xTree))


    #weather api
    #wtR= weather_forcast()
    #wtR.get_token()
    #json_dict = wtR.get_weather(get_weather_request())
    #print(json_dict)

    #Outdoor activity


    #3G-UMTS Coverage
    #root_node = ET.

    #Points of Interests – POI-Service.
