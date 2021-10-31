import datetime

import pandas as pd

from src.backend.api_wrapper import getData
from src.backend.searchRankedTrips import weather


def get_weather_info(destination:pd.Series, starting_time )->dict:
    """
        enter row of hike locations, get weather info back.

    :param destination: pd.Series
    :param starting_time: datetime
    :return:
        dict
            with weather info.
    """
    weather_request = getData.get_weather_request(time=starting_time+datetime.timedelta(minutes=destination['feat_tripTime']),
                                                  location=[destination["startingPoint"]["lon"], destination["startingPoint"]["lat"]])
    return weather.get_weather(weather_request)


def get_pictures(destination:pd.Series, primaryPicture:bool=False, limit_pics=5, format=[300,200], force_redownload:bool=False, url_mode=False)->list:
    """
    This function retrieves pictures for Hiking locations, provided

    :param destination: pd.Series, row from pdDataframe to get data
    :param limit_pics: how many pictures maximally should be downloaded?
    :return:
        list[str]
            img paths to tmp folder
    """
    oa =getData.outdoor_active()
    oa.img_format=format
    if(primaryPicture):
        possible_img = [destination['primaryImage']]
    else:
        possible_img = destination['images']["image"]
    img_paths = []
    if(len(possible_img)< limit_pics):
        limit_pics = len(possible_img)

    for img_dict in possible_img[:limit_pics]:
        img_path = oa.get_image_info(ID=img_dict["id"], url_mode=url_mode)
        img_paths.append(img_path)
    return img_paths
