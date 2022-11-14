from io import BytesIO
import urllib.request
import datetime as dt
import pandas as pd


def download_catalog_sed(
        start_time: dt.datetime = dt.datetime(1970, 1, 1),
        end_time: dt.datetime = dt.datetime.now(),
        min_latitude: float = None,
        max_latitude: float = None,
        min_longitude: float = None,
        max_longitude: float = None,
        min_magnitude: float = 0.01,
        delta_m: float = 0.1,
        only_earthquakes: bool = True
) -> pd.DataFrame:
    """Downloads the Swiss earthquake catalogue.

    Args:
      start_time: start time of the catalogue.
      end_time: end time of the catalogue. defaults to current time.
      min_latitude: minimum latitude of catalogue.
      max_latitude: maximum latitude of catalogue.
      min_longitude: minimum longitude of catalogue.
      max_longitude: maximum longitude of catalogue.
      min_magnitude: minimum magnitude of catalogue.
      delta_m: magnitude bin size. if >0, then
        events of magnitude >= (min_magnitude - delta_m/2) will be downloaded.
      only_earthquakes: if True, only events of type earthquake are returned.

    Returns:
      The catalog as a pandas DataFrame.

    """
    base_query = 'http://arclink.ethz.ch/fdsnws/event/1/query?'
    st_tm = 'starttime=' + start_time.strftime("%Y-%m-%dT%H:%M:%S")
    end_tm = '&endtime=' + end_time.strftime("%Y-%m-%dT%H:%M:%S")
    min_mag = '&minmagnitude=' + str(min_magnitude - delta_m / 2)
    min_lat = '&minlatitude=' + str(min_latitude) \
        if min_latitude is not None else None
    min_lon = '&minlongitude=' + str(min_longitude) \
        if min_longitude is not None else None
    max_lat = '&maxlatitude=' + str(max_latitude) \
        if max_latitude is not None else None
    max_lon = '&maxlongitude=' + str(max_longitude) \
        if max_longitude is not None else None

    link = base_query + st_tm + end_tm + min_mag \
        + ''.join([part for part in [min_lat, min_lon, max_lat, max_lon]
                   if part is not None]) \
        + '&format=text'
    response = urllib.request.urlopen(link)
    data = response.read()

    df = pd.read_csv(BytesIO(data), delimiter="|")

    df.rename(
        {
            "Magnitude": "magnitude",
            "Latitude": "latitude",
            "Longitude": "longitude",
            "Time": "time",
            "Depth/km": "depth",
            "EventType": 'event_type'
        }, axis=1, inplace=True)

    df["time"] = pd.to_datetime(df["time"])
    df.sort_values(by="time", inplace=True)

    if only_earthquakes:
        df.query('event_type == "earthquake"', inplace=True)

    return df
