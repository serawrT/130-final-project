import pandas as pd
from pygments import highlight

# importing and cleaning the data
df1 = pd.read_csv('cal_cities_lat_long.csv')
df2 = pd.read_csv('cal_populations_city.csv')
df2 = df2.sort_values('pop_april_2010', ascending=False)

# to find 200 biggest cities in california
df2 = df2.reset_index(drop=True)
df2 = df2[0:200]

# merging the cities with their coordinates in other dataframe
df = pd.merge(df2, df1, left_on='City', right_on='Name', how='inner')

# merging the cities on itself to further calculate each pair of distances between them
df = pd.merge(df, df, how='cross', suffixes=('_1', '_2'))
df = df[df['City_1'] != df['City_2']]

from math import radians, degrees, sin, cos, asin, acos, sqrt

# function for calculating distance between various cities given the coordinates
# and taking curvature of earth into consideration
def great_circle(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    return 3959 * (
        acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2)))

df['distance'] = df.apply(lambda x: great_circle(x.Longitude_1, x.Latitude_1, x.Longitude_2, x.Latitude_2), axis=1)

# Here we make an assumption that the roads connect the city to it's 5 closest biggest neighbors
# since roads usually do not go straight from one city to another for say 300 miles without intercepting any others
df = df.sort_values(['City_1', 'distance'], ascending=[True, True]).groupby('City_1').head(5).reset_index(drop=True)

