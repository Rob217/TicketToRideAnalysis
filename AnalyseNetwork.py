# ways to improve:
#
# - rather than storing objects in lists, store keys to objects
# - account for duplicate routes and number of players
# - account for connections that make no sense for certain routes

import pandas as pd
import pickle
from collections import defaultdict
from bisect import insort
from SortedCollection import SortedCollection
from pprint import pprint
from operator import itemgetter
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import matplotlib.colors as mcolors
from PIL import Image
import numpy as np



class City():
  def __init__(self, name, location):
    self.name = name
    self.location = location
    self.neighbors = {}

  def add_connection(self, connection):
    city_1_name = connection.cities[0].name
    city_2_name = connection.cities[1].name
    if city_1_name != self.name:
      other_city_name = city_1_name
    else:
      other_city_name = city_2_name
    self.neighbors[other_city_name] = connection
    # self.neighbors.append(connection)


class Connection():
  ## could this be a dict rather than a class?
  def __init__(self, cities, distance, color):
    self.distance = distance
    self.color = color
    self.cities = cities
    self.route_cost = defaultdict(float)


class Network():
  def __init__(self, city_dict, connections_df):
    self.city_dict = {}
    self.tickets = {}
    self.connections_li = []

    for city_name in city_dict:
      temp_city = City(city_name, city_dict[city_name])
      self.city_dict[city_name] = temp_city
    self.n_cities = len(self.city_dict)

    for index, row in connections_df.iterrows():
      city_1, city_2 = row['City A'], row['City B']
      temp_connection = Connection((self.city_dict[city_1], self.city_dict[city_2]), \
                                    row['Distance'], row['Color'])
      self.connections_li.append(temp_connection)
      self.city_dict[city_1].add_connection(temp_connection)
      self.city_dict[city_2].add_connection(temp_connection)

    self.shortest_distances = {}
    self.find_shortest_distance()
    self.route_costs_info = {}

  def find_shortest_distance(self):

    already_visited = defaultdict(bool)

    # loop over starting cities
    for city_1_name in self.city_dict:
      # print(city_1_name)
      n_visited = 1
      already_visited[(city_1_name, city_1_name)] = True
      self.shortest_distances[(city_1_name, city_1_name)] = 0

      # initialize list of connections to be checked next
      check_next = SortedCollection(key=itemgetter(0)) # (total distance, connection)

      # initialize with nearest neighbors to city
      for neighbor_name in self.city_dict[city_1_name].neighbors:
        if already_visited[(city_1_name, neighbor_name)]:
          continue
        neighbor = self.city_dict[city_1_name].neighbors[neighbor_name]
        check_next.insert((neighbor.distance, neighbor_name, neighbor))

      # loop over all connections, adding more as we visit more cities
      while n_visited <= self.n_cities and len(check_next) > 0:
        distance_1_2, city_2_name, connection_1_2 = check_next[0]
        check_next.remove(check_next[0])

        # check if already visited from city_1
        if already_visited[(city_1_name, city_2_name)]:
          continue
        already_visited[(city_1_name, city_2_name)] = True
        self.shortest_distances[(city_1_name, city_2_name)] = distance_1_2

        # initialize with nearest neighbors to city
        for neighbor_name in self.city_dict[city_2_name].neighbors:
          if already_visited[(city_1_name, neighbor_name)]:
            continue
          neighbor = self.city_dict[city_2_name].neighbors[neighbor_name]
          check_next.insert((distance_1_2 + neighbor.distance, neighbor_name, neighbor))

        n_visited += 1

    # pprint(self.shortest_distances)

  def add_tickets(self, tickets_df, tickets_name):

    self.tickets[tickets_name] = []
    for index, row in tickets_df.iterrows():
      city_1, city_2, points = row['City A'], row['City B'], row['Points']
      self.tickets[tickets_name].append((city_1, city_2, points))
    # pprint(self.tickets[tickets_name])


  def find_route_costs(self, tickets_name):
    # loop over all tickets in tickets_name
    # for each ticket, find n shortest ways of realizing that route

    # loop over all starting tickets
    for ticket in self.tickets[tickets_name]:
      city_1 = ticket[0]
      city_2 = ticket[1]
      points = ticket[2]
      dist_1_2 = self.shortest_distances[city_1, city_2]

      # loop over all connections
      for connection in self.connections_li:
        city_a, city_b = connection.cities
        dist_a_b = connection.distance
        dist_1_a = self.shortest_distances[city_1, city_a.name]
        dist_1_b = self.shortest_distances[city_1, city_b.name]
        dist_2_a = self.shortest_distances[city_2, city_a.name]
        dist_2_b = self.shortest_distances[city_2, city_b.name]
        dist_list = [dist_1_a, dist_1_b, dist_2_a, dist_2_b]
        shortest_dist = min([dist_a_b + dist_1_a + dist_2_b, \
                             dist_a_b + dist_1_b + dist_2_a])
        connection.route_cost[tickets_name] += (points/shortest_dist)**2

    min_cost = 1.e8
    max_cost = -1.e8
    for connection in self.connections_li:
      max_cost = max(max_cost, connection.route_cost[tickets_name])
      min_cost = min(min_cost, connection.route_cost[tickets_name])

    self.route_costs_info[tickets_name] = {'min_cost': min_cost, 'max_cost': max_cost}

    # for connection in self.connections_li:
    #   pprint(vars(connection))

  def print_route_costs(self, tickets_name):
    # plot the likelihood of each route being used

    plotCols = {'K': 'k', \
                'W': 'w', \
                'P': [213/255, 136/255, 180/255], \
                'B': 'b', \
                'G': 'g', \
                'Y': 'y', \
                'X': [0.5, 0.5, 0.5], \
                'O': [0.5, 0.5, 0], \
                'R': 'r'}

    my_dpi = 100
    fig = plt.figure(1, figsize=(1024/my_dpi, 683/my_dpi))

    im = Image.open('T2R_USA_MAP.jpg')
    height = im.size[1]
    im = np.array(im).astype(np.float) / 255
    fig.figimage(im, 0, 0, resize=False, alpha=0.5)
    print(np.shape(im))


    ax = plt.axes([0, 0, 1, 1])
    # dims = (1052.3622, 744.09448) # overall dimensions
    dims = (1, 1)
    plt.xlim([0, dims[0]])
    plt.ylim([0, dims[1]])
    plt.axis('off')
    # ax = plt.gca()

    # ax.set_facecolor([184/255, 255/255, 126/255])
    # fig.patch.set_alpha(0.5)
    # ax.set_facecolor('None')

    # cmap = cm.get_cmap('viridis', 12)
    cmap = cm.get_cmap('winter', 12)
    # fig.colorbar(cm.ScalarMappable(norm=1, cmap=cmap))

    max_cost = self.route_costs_info[tickets_name]['max_cost']
    min_cost = self.route_costs_info[tickets_name]['min_cost']

    # cmap = cm.ScalarMappable(
    #   norm = mcolors.Normalize(min_cost, max_cost),
    #   cmap = plt.get_cmap('viridis'))
    # fig.colorbar(cmap)



    for connection in self.connections_li:
      city_1, city_2 = connection.cities
      x1, y1 = city_1.location
      x2, y2 = city_2.location

      col = cmap((connection.route_cost[tickets_name] - min_cost)/(max_cost-min_cost))
      # col = plotCols[connection.color]
      plt.plot([x1, x2], [y1, y2], color = col, linewidth = 5)


    # for key in self.cities:
    #   x, y = self.cities[key].getLocation()
    #   plt.scatter(x, y)



    plt.savefig('Route_costs.pdf')

    plt.show()







if __name__ == "__main__":

  # load city names and locations
  with open('stationLocations.dictionary', 'rb') as city_file:
    city_dict = pickle.load(city_file)

  # load connections
  connections_df = pd.read_csv(r'Routes.csv')

  # initialize network
  my_network = Network(city_dict, connections_df)

  # load tickets
  tickets_orig_df = pd.read_csv(r'Tickets_OriginalVersion.csv')
  my_network.add_tickets(tickets_orig_df, 'original_tickets')

  # calculate routes through tickets
  my_network.find_route_costs('original_tickets')
  my_network.print_route_costs('original_tickets')
