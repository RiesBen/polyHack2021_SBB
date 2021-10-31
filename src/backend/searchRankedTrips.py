import os
import numpy as np
import pandas as pd
import datetime

#implemented
from src.backend.api_wrapper import getData
#init_api
oa = getData.outdoor_active()
js = getData.journey_service()
timetable = getData.timetable_info()
weather = getData.weather_forcast()

def get_switzerland_rankings()->pd.DataFrame:
    """
    This function returns a dataframe with hikes all over switzerland!
    :return:
        pd.DataFrame
        contains information about hikes, stations, and train tips
    """
    siwss_df_path = os.path.dirname(__file__)+"/data/swiss_oa_df.obj"
    if(os.path.exists(siwss_df_path)):
        swiss_df = pd.read_pickle(siwss_df_path)
        swiss_df = _calculate_ranking(swiss_df)
    else:
        raise IOError("could not find swiss df!")
    return swiss_df


def rank_trips(startLocation, starting_time, destination, destination_radius, verbose=False)->pd.DataFrame:
    """
    Generate convenient hike trips close to the destination. Gets slow for large Search areas!

    :param startLocation:   Where do you want to start
    :param starting_time:   Time/Date to start
    :param destination: Where do you want to go
    :param destination_radius:  radius around the destination, that helps
    :param verbose: I can talk!
    :return:
        pd.Dataframe
            contains hike information, stations and trips.
    """
    # Get starting Info
    if verbose: print("Get Information")
    oa_df = _get_information(destination, destination_radius, startLocation, starting_time, verbose=verbose)

    ## Feature extract
    if verbose: print("Get Features")
    print(oa_df.columns)
    fastest_trip_time = pd.Series([float(x['t'])/60 for x in oa_df["fastestTripToDestination"]])
    nsegments_trip = pd.Series([float(x['nSegments']) for x in oa_df["fastestTripToDestination"]])
    last_mileDist = pd.Series([float(x['distanceToOA']) for x in oa_df["nextStation"]])

    oa_df["feat_tripTime"] = fastest_trip_time
    oa_df["feat_nsegments_trip"] = nsegments_trip
    oa_df["feat_lastMile"] = last_mileDist

    ## Rank Features:
    oa_df = _calculate_ranking(oa_df)
    return oa_df


"""
    Private Functions, don't look! ;)
"""
def _dist2DDeg_KM(x, y):
    """
        Approx distance
    """
    dLon =x["lon"]-y["latitude"]
    dLat =x["lat"]-y["longitude"]
    return dLat*111.32+(40075*np.cos(dLat)/360) *dLon


def _get_information(destination, destination_radius, startLocation, starting_time, verbose=False):
    # Get starting Info
    if verbose: print("Get Starting Information")
    startLocation_OBJ = timetable.get_locationRequest(location=startLocation)[0]
    startLocation_ID = startLocation_OBJ["id"]
    destination_OBJ = timetable.get_locationRequest(location=destination)[0]
    destination_ID = destination_OBJ["id"]

    # Get outdoor activity
    if verbose: print("Get OA")
    oa_df = _get_oa_info(destination_OBJ, destination_radius)
    if verbose: print("Data:", oa_df.shape)

    # get closest station
    if verbose: print("Get closestStation")
    oa_df = _get_station_info(oa_df)
    if verbose: print("Data:", oa_df.shape)

    ##Gather TripInformation
    if verbose: print("Get TripInfo")
    oa_df = _get_trip_info(oa_df, starting_time, startLocation_ID)
    if verbose: print("Data:", oa_df.shape)

    return oa_df


def _get_fastest_trip(destinationStation_ID, startLocation_ID, starting_time):
        trip_request = getData.generate_trip_dict(originId=startLocation_ID,
                                                  destinationId=destinationStation_ID,
                                                  date=starting_time.date(),
                                                  time=starting_time.time())
        trips = timetable.get_tripRequest(trip_request)
        if (len(trips) == 0):
            return np.nan
        else:
            t_deltas = []
            segments = []
            for trip in trips:
                start_time = datetime.datetime.fromisoformat(trip['segments'][0]['stops'][0]['departureDateTime'])
                end_time = datetime.datetime.fromisoformat(trip['segments'][-1]['stops'][-1]["arrivalDateTime"])
                deltaT = end_time - start_time
                segments.append(len(trip['segments']))
                t_deltas.append(deltaT.seconds)

            t_deltas = np.array(t_deltas)
            segments = np.array(segments)

            fastest_trip_i = np.argmin(t_deltas)
            fastest_trip = trips[np.argmin(t_deltas)]
            fastest_trip_t = np.min(t_deltas)
            fastest_trip.update({"t": fastest_trip_t, "nSegments": segments[fastest_trip_i]})
            return fastest_trip


def _get_trip_info(oa_df, starting_time, startLocation_ID):

    oa_df["fastestTripToDestination"] = oa_df.apply(
        lambda x: _get_fastest_trip(x["nextStation"]['uicOrId'], startLocation_ID=startLocation_ID,
                                    starting_time=starting_time), axis=1)
    oa_df["fastestTripHome"] = oa_df.apply(
        lambda x: _get_fastest_trip(startLocation_ID=startLocation_ID, destinationStation_ID=x["nextStation"]['uicOrId'],
                                    starting_time=starting_time + datetime.timedelta(minutes=x["time"]["min"])), axis=1)
    oa_df.dropna(subset=["fastestTripToDestination", "fastestTripHome"], inplace=True)

    return oa_df


def _get_station_info(oa_df):
    next_station = []
    next_station_d = []
    closeStations = []
    for i, row in oa_df.iterrows():
        if (isinstance(row['closeStations'], list)):
            stations = row['closeStations']
            print(type(stations), stations)
            close_stations_distances = [_dist2DDeg_KM(row['startingPoint'], station['coordinatesWGS84']) / 1000 for
                                        station in stations]
            closest_station_i = np.argmin(close_stations_distances)
            closest_station_dmin = np.min(close_stations_distances)
            closest_station = row['closeStations'][closest_station_i]

            # Add info to closeStations
            print(row['closeStations'], )
            [station.update({"distanceToOA": dist}) for station, dist in zip(stations, close_stations_distances)]
            closeStations.append(stations)
            next_station.append(closest_station)
            next_station_d.append(closest_station_dmin)
        else:
            closeStations.append(np.nan)
            next_station.append(np.nan)
            next_station_d.append(np.nan)
    # print(len(close_stations))
    oa_df["nextStation"] = pd.Series(next_station)
    oa_df["closeStations"] = pd.Series(closeStations)
    oa_df.dropna(how='all', inplace=True)
    oa_df.dropna(subset=["closeStations"], inplace=True)
    return  oa_df


def _get_oa_info(destination_OBJ, destination_radius):
    oa_df = oa.get_dataframe_of_ch(getData.get_coords_request(lat=destination_OBJ["coordinates"]['latitude'],
                                                              lon=destination_OBJ["coordinates"]['longitude']),
                                   radius=destination_radius)
    # Get close stations to oa
    oa_df['closeStations'] = oa_df.apply(
        lambda x: js.get_locationRequestByCoords(getData.get_coords_request(**x['startingPoint'])), axis=1)
    # clean empty stations:
    drop_empty_stations = [i for i, row in oa_df.iterrows() if (len(row['closeStations']) == 0)]
    oa_df = oa_df.drop(index=drop_empty_stations)
    return oa_df


def _calculate_ranking(oa_df)->pd.DataFrame:
    counts, axes = np.histogram(oa_df["feat_tripTime"].dropna(),
                                bins=int(np.ceil(oa_df["feat_tripTime"].shape[0] / 40)))
    bin_size = 2
    if (len(axes) > 2):
        time_bins = axes[2::2]
        data0_bin = oa_df.where(oa_df.feat_tripTime < time_bins[0]).dropna(how="all")
        data0_bin = data0_bin.sort_values(by=["feat_lastMile", "feat_nsegments_trip"], )
        dfs = [data0_bin]
        for i, time_bin in enumerate(time_bins[1:]):
            data_bin = oa_df.where(oa_df.feat_tripTime < time_bin).where(
                oa_df.feat_tripTime > time_bins[i - 1]).dropna(how="all")
            data_bin = data_bin.sort_values(by=["feat_lastMile", "feat_nsegments_trip"], ascending=True)
            dfs.append(data_bin)

        sortedtrip_oa_df = data0_bin.append(dfs)
    else:
        sortedtrip_oa_df = oa_df.sort_values(by=["feat_tripTime", "feat_lastMile", "feat_nsegments_trip"], )


    return sortedtrip_oa_df




if __name__ == "__main__":
    # Input:
    #all
    #df = get_switzerland_rankings()
    #print(df.shape)

    #querry
    startLocation = "Zürich HB"
    starting_time = datetime.datetime.fromisoformat('2021-10-30T12:02:00.036331')

    destination = "Ilanz"  # None
    #destination = "Zug"
    destination_radius = 5000
    print("START")
    df = rank_trips(startLocation=startLocation, starting_time=starting_time, destination=destination, destination_radius=destination_radius, verbose=True)
    print(df)
    print("DONE")
