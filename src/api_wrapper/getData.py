import json, os
import requests
import uuid
from datetime import timezone, date, datetime, time
from requests.auth import HTTPBasicAuth
from src.api_wrapper.data import s_key, m_key, t_key, w_key, j_key
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
        delta = (self.token_timestamp-date.today()).seconds/60 > 30 if(not self.token_timestamp is None) else True
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

        query = {"name": location,
                 }
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


    def get_route_information(self, route:OrderedDict):
        request_url = self.adress + '/v1/route?' + "&".join(
            [str(k) + "=" + str(v) for k, v in route.items()])
        self.r = requests.get(request_url, headers=self.header)

        print(self.r.url)
        print(self.r.status_code)
        print(self.r.text)
        return json.loads(self.r.text)


    def get_transfer_information(self, transfer:OrderedDict)->dict:
        request_url = self.adress + '/v1/transfer'

        self.r = requests.get(request_url, headers=self.header, params=transfer)

        print(self.r.url)
        print(self.r.status_code)
        print(self.r.text)
        return json.loads(self.r.text)


class swiss_topo_maps(api_interface):
    adress: str

def get_weather_request(time:datetime=datetime.fromisoformat('2021-10-29T00:00:00'), parameters:str=['t_2m:C','relative_humidity_2m:p', "wind_speed_10m:ms","precip_1h:mm"],
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
    adress = 'https://weather.api.sbb.ch'
    tokenAdress : str = "https://sso.sbb.ch/auth/realms/SBB_Public/protocol/openid-connect/token"
    token_timestamp = None
    user : str = "56bae62c"

    def __init__(self):
        self.get_token()

    def get_token(self):
        """
        ##curl -X POST \
        # 'https://sso.sbb.ch/auth/realms/SBB_Public/protocol/openid-connect/token' \
        # -d 'grant_type=client_credentials&client_id=$clientId&client_secret=$clientSecret'
        :return:
        """

        delta = (self.token_timestamp-date.today()).seconds/60 > 30 if(not self.token_timestamp is None) else True
        if(delta):
            credential ={
                "grant_type":'client_credentials',
                "client_id": self.user,
                "client_secret": w_key
            }
            r = requests.post(url=self.tokenAdress, data=credential).json()
            self.token_request = r
            self.token_timestamp = date.today()
            self.accessToken = r['access_token']
        else:
            print("token was still valid")


    def get_weather(self, weather_request:OrderedDict):
        """
        curl -X GET --header 'Accept: application/json' --header 'Authorization: Bearer $accesToken
        https://weather.api.sbb.ch/2019-02-15T12:15:00ZP2D:PT1H/snowdepth:cm/46.2942,7.881

        :param weather_request:
        :return:
        """
        self.get_token()
        auth ={
            "Authorization": f"Bearer {self.accessToken}",
            "'Accept": "application/json",
            #"X-Contract-Id": self.conID,
            #"X-Conversation-ID": str(self.conv_id)
        }

        #request_url = str(self.adress)
        data=""+str(weather_request['validateTime'])
        data+="/"+str(weather_request['parameters'])
        data+="/"+str(weather_request['location'])+"/csv"
        print(data)
        print()

        self.r = requests.get(self.adress+"/"+data, headers=auth)
        header = self.r.text.split("\n")[0].split(";")
        data = self.r.text.split("\n")[1].split(";")

        cond ={k:v for k,v in zip(header[1:], data[1:])}
        weather = {data[0]:cond}
        return weather


class outdoor_active(api_interface):
    def get_swiss_route_IDs(self):
        jsonhead={'Accept':'application/json'}
        r=requests.get(url='http://www.outdooractive.com/api/project/api-dev-oa/nearby/tour?location=8.23656,46.79803&radius=50000&key=yourtest-outdoora-ctiveapi', headers=jsonhead)
        return json.loads(r.text)["result"]


class UMTS_3G_coverage(api_interface):
    adress: str
    data_dir_path = os.path.dirname(UGM_3G_data.__file__)
    data_gm_path = data_dir_path+"/Metadata_gm03.xml"
    data_iso_path = data_dir_path+"/Metadata_gm03.xml"

    def load(self):
        self.xTree = ET.parse(self.data_iso_path)


class journey_service(api_interface):
    adress: str = "https://journey-service-int.api.sbb.ch/b2c/v2"
    tokenAdress : str = "https://login.microsoftonline.com/2cda5d11-f0ac-46b3-967d-af1b2e1bd01a/oauth2/v2.0/token"
    tokenScope : str = " api://c11fa6b1-edab-4554-a43d-8ab71b016325/.default"
    userID : str = "10e4b078-dd1f-4faa-8f0b-a0111ddd5398"
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
        delta = (self.token_timestamp-date.today()).seconds/60 > 30 if(not self.token_timestamp is None) else True
        if(delta):
            credential = {
                'grant_type': 'client_credentials',
                'client_id': self.userID,
                'client_secret': j_key,
                'scope': self.tokenScope
            }
            r = requests.post(url=self.tokenAdress, data=credential).json()
            self.token_request = r
            self.token_timestamp = date.today()
            self.accessToken = r['access_token']
        else:
            print("token was still valid")


    def get_locationRequestByCoords(self, coords=[47.3765468379,8.5356070469]) -> dict:
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
        self.conv_id = uuid.uuid4()  # conversation Id
        auth = {
            "Authorization": f"Bearer {self.accessToken}",
            "X-Contract-Id": self.userID,
            "X-Conversation-ID": str(self.conv_id)
        }

        self.r = requests.get(url=self.adress+"/locations/"+ "/".join(map(str,coords)) , headers=auth)
        print(self.r.url)
        print(self.r.status_code)
        print(self.r.text)
        return json.loads(self.r.text)


class POI_service(api_interface):
    adress: str



if __name__ == "__main__":
    pass
    #SBB Timetables:
    # Works!
    #timetable = timetable_info()
    #json_dict = timetable.get_locationRequest()
    #json_dict = timetable.get_tripRequest(trip=generate_trip_dict())
    #json_dict = timetable.get_locationRequestByCoords()
    #print(json_dict)


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
    #geoJson_dict = jmR.get_transfer_information(generate_transfer_dict())
    #print(geoJson_dict)

    # Map Swisstopo
    #print(UGM_3G_data.__file__)
    #u3GD = UMTS_3G_coverage()
    #u3GD.load() #Todo: needs to be further parsed
    #print(vars(u3GD.xTree))


    #weather api
    #wtR= weather_forcast()
    #wtR.get_token()
    #dayTime = datetime.today()
    #json_dict = wtR.get_weather(get_weather_request(time=dayTime))

    #Outdoor activity


    #3G-UMTS Coverage
    #root_node = ET.

    #Points of Interests – POI-Service.


    #journey service
    jrS = journey_service()
    jrS.get_token()
    jrS.get_locationRequestByCoords()