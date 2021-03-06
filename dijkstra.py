from math import radians, degrees, sin, cos, asin, acos, sqrt
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


# function for calculating distance between various cities given the coordinates
# and taking curvature of earth into consideration

def great_circle(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    return 3959 * (
        acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2)))


df['distance'] = df.apply(lambda x: great_circle(
    x.Longitude_1, x.Latitude_1, x.Longitude_2, x.Latitude_2), axis=1)

# Here we make an assumption that the roads connect the city to it's 5 closest biggest neighbors
# since roads usually do not go straight from one city to another for say 300 miles without intercepting any others
df = df.sort_values(['City_1', 'distance'], ascending=[True, True]).groupby(
    'City_1').head(5).reset_index(drop=True)

# implementing the priority queue class


class PriorityQueue(object):
    def __init__(self):
        self.queue = []

    def __str__(self):
        return ' '.join([str(i) for i in self.queue])

    # for checking if the queue is empty
    def isEmpty(self):
        return len(self.queue) == 0

    # for inserting an element in the queue
    def insert(self, data):
        self.queue.append(data)

    # for popping an element based on Priority
    def delete(self):
        if(not self.isEmpty()):
            min_dist_id = 0
            for i in range(1, len(self.queue)):
                if self.queue[i][1] < self.queue[min_dist_id][1]:
                    min_dist_id = i
            item = self.queue[min_dist_id]
            self.queue.pop(min_dist_id)
            return item
        else:
            return None

# implementing the graph class


class Graph(object):
    def __init__(self):
        self.adj_list = {}

    def __str__(self):
        return str(self.adj_list)

    def add_vertex(self, value):
        if(value not in self.adj_list.keys()):
            self.adj_list[value] = {}

    def add_edge(self, vertex_1, vertex_2, dist):
        keys = self.adj_list.keys()
        if(vertex_1 in keys and vertex_2 in keys):
            self.adj_list[vertex_1][vertex_2] = dist
            self.adj_list[vertex_2][vertex_1] = dist

    def get_neighbors(self, vertex):
        return self.adj_list[vertex]


# constructing the graph with the previously found cities and distances
graph = Graph()
distinct_cities = df['City_1'].unique()
for city in distinct_cities:
    graph.add_vertex(city)

df.apply(lambda x: graph.add_edge(x.City_1, x.City_2, x.distance), axis=1)


# implementing dijkstra
def dijkstra(graph, start, end):
    visiting_queue = PriorityQueue()
    visiting_queue.insert((start, 0))
    visited = []
    dijkstra_table = {start: (start, 0)}
    while(not visiting_queue.isEmpty()):
        # visit the node with smallest dietance
        current_place, curr_dist = visiting_queue.delete()
        for place, dist in graph.get_neighbors(current_place).items():
            if (place not in visited):
                if (place in dijkstra_table.keys()):
                    if(dijkstra_table[place][1] > curr_dist + dist):
                        dijkstra_table[place] = (
                            current_place, curr_dist + dist)
                        visiting_queue.insert((place, curr_dist + dist))

                else:
                    dijkstra_table[place] = (current_place, curr_dist + dist)
                    visiting_queue.insert((place, curr_dist + dist))
        visited.append(current_place)
    return dijkstra_table


for i, city in enumerate(distinct_cities):
    print(f'{i} : {city}')

# starting_city = 'San Jose' # uncomment this whole line for using san jose as startingpoint only
# comment this for san jose starting point only
starting_city = input("Input the starting city's id or its name: ")
destination_city = input("Input the destination city's id or its name: ")
print('Choose a starting and the destination city from the above list:')

highway_consumption = float(
    input("Your average fuel consumtpion (miles/gallon)) on highway: "))
city_consumption = float(
    input("Your average fuel consumtpion (miles/gallon) in the city: "))
fuel_price = float(input("Your average fuel  $/Gallon: "))

if (starting_city.isnumeric()):  # comment this for san jose starting point only
    # comment this for san jose starting point only
    starting_city = distinct_cities[int(starting_city)]

if (destination_city.isnumeric()):
    destination_city = distinct_cities[int(destination_city)]

shortest_path = dijkstra(graph, starting_city, destination_city)

# finding the order of cities
current_city = destination_city
list_of_cities = [destination_city]
while (current_city != starting_city):
    current_city = shortest_path[current_city][0]
    list_of_cities.append(current_city)

print(list_of_cities)
total_distance_to_travel = shortest_path['San Diego'][1]
print(f'Total distance to travel: {total_distance_to_travel} miles')

# Calculating fuel consumption of the trip:
# It depends on the number of cities that the traveller have passed through,
# since typicaly there's more fuel spent in and around the cities due to
# traffic and the driving infrastructure.
# We will roughly estimate that each 5 mile area around the city is a high fuel consumption area
# and rest is a highway.
fuel_consumption = len(list_of_cities) * 5 * (1 / city_consumption) + (
    total_distance_to_travel - (len(list_of_cities) * 5)) * (1 / highway_consumption)
print(
    f'The estimated fuel consumption of the given trip is: {fuel_consumption} gallons')
print(
    f'The estimated fuel cost of the given trip is: {fuel_consumption * fuel_price}$')
