from collections import defaultdict
import random as rd

class City:
	def __init__(self,openings_count,index=None,points=1,meeples={}):
		self.index = index
		self.points = points
		self.openings_count = openings_count
		self.contacts = []
		self.feature_type = 'c'
		self.complete = False
		self.meeples = defaultdict(lambda:0,meeples)

	def get_score(self):
		if self.complete:
			return self.score * 2
		else:
			return self.score

	def __str__(self):
		return "City" + str(self.index) + ",fields" + str(len(self.contacts)) + ",openings" + str(self.openings_count)


class Road:
	def __init__(self,openings_count,index=None,points=1,meeples={}):
		self.index = index
		self.points = points
		self.openings_count = openings_count
		self.feature_type = 'r'
		self.complete = False
		self.meeples = defaultdict(lambda:0,meeples)

	def get_score(self):
		return self.points

	def __str__(self):
		return "Road" + str(self.index) + ",openings" + str(self.openings_count)

class Field:
	def __init__(self,index=None,meeples={}):
		self.index = index
		self.feature_type = 'f'
		self.contacts = []
		self.points = 0
		self.meeples = defaultdict(lambda:0,meeples)

	def get_score(self,cities):
		return sum([3 for city_index in self.contacts if cities[city_index].complete])

	def __str__(self):
		return "Field" + str(self.index) + ",contacts" + str(len(self.contacts))

class Monastery:
	def __init__(self,openings_count,index=None,meeples={}):
		self.index = index
		self.meeples = meeples
		self.openings_count = openings_count
		self.feature = 'm'
		self.complete = False
		self.meeples = defaultdict(lambda:0,meeples)

	def get_score(self):
		return 9 - openings_count

	def __str__(self):
		return "Monastery" + str(self.index) + ",points" + str(self.get_score())

class Player:
	def __init__(self,meeples,index):
		self.index = index
		self.meeples = meeples
		self.score = 0
		self.virtual_score = 0

	def __str__(self):
		return "Player" + str(self.index) + ",meeples" +  str(self.meeples) + ",score" +  str(self.score) + ",virtual_score" +  str(self.virtual_score)

class Action:
	def __init__(self,tile,location,rotation,meeples={},meeple_feature=None):
		self.tile = tile
		self.location = location
		self.rotation = rotation
		self.meeples = meeples
		self.meeple_feature = meeple_feature

	def __str__(self):
		return 'Action. location:' + str(self.location) + ' ,rotation:' + str(self.rotation) + ' ,meeples:' + str(self.meeples)+ ' ,meeple_feature:' + str(self.meeples)

class Tile:
	def __init__(self,type,features,monastery=None,shield=False):
		self.type = type
		self.features = features
		self.shield = shield
		self.monastery = monastery

	def __str__(self):
		return 'Tile. type:' + str(self.type)

class Carcassonne:
	def __init__(self,players=2,starting_meeples={0:7,1:7},tile_copies={0:4,1:3,2:2,3:3,4:3,5:5,6:3}):
		self.players = {i:Player(meeples=starting_meeples[i],index=i) for i in range(players)}
		self.player_turn = 0
		self.city_count,self.road_count,self.field_count,self.monastery_count = 0,0,0,0
		self.players={i:Player(meeples=starting_meeples[i],index=i) for i in range(players)}
		self.rotations = (0,1,2,3)
		self.main_sides=('u','r','d','l')
		self.feature_types=('c','r','f','m')
		self.sides=('u','r','d','l','ul','ur','ru','rd','dl','dr','lu','ld')
		self.rotation_mappings = {0:{s:s for s in self.sides},
								1:{'u':'l','r':'u','d':'r','l':'d','ul':'ld','ur':'lu','ru':'ul','rd':'ur','dl':'rd','dr':'ru','lu':'dl','ld':'dr'},
								2:{'u':'d','r':'l','d':'u','l':'r','ul':'dr','ur':'dl','ru':'ld','rd':'lu','dl':'ur','dr':'ul','lu':'rd','ld':'ru'},
								3:{'u':'r','r':'d','d':'l','l':'u','ul':'ru','ur':'rd','ru':'dr','rd':'dl','dl':'lu','dr':'ld','lu':'ul','ld':'ur'}}
		self.adjacent_mappings = {'u':'d','r':'l','d':'u','l':'r','ul':'dr','ur':'dl','ru':'lu','rd':'ld','dl':'ur','dr':'ul','lu':'ru','ld':'rd'}
		self.tile_copies = tile_copies
		self.tile_stack = {}
		self.board = defaultdict(lambda:defaultdict(lambda:None))
		"""
		###      ur  u   ul      
		###    ---------------   
		###    |             |   
		### lu |             | ru 
		###    |             |   
		###  l |             | r 
		###    |             |   
		### ld |             | rd
		###    ---------------   
		###      dl  d    dr 
		"""

		#initialise tiles:
		for tile_type,copies in self.tile_copies.items():
			temp_tiles = []
			if tile_type == 0:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   ccccccc   | 
				###    |             |   
				###    |rrrrrrrrrrrrr|  
				###    |             |   
				###    |             |  
				###    --------------- 
				for copy in range(copies):
					city = City(openings_count=1)
					road = Road(openings_count=2)
					field1 = Field()
					field2 = Field()
					city.contacts.append(field2)
					field2.contacts.append(city)
					features = {'u':city,'r':road,'d':field1,'l':road,'ru':field2,'rd':field1,'lu':field2,'ld':field1}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 1:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   cccccccccc| 
				###    |       cccccc|   
				###    |         cccc|  
				###    |           cc|   
				###    |            c|  
				###    ---------------
				for copy in range(copies):
					city = City(openings_count=2)
					field = Field()
					city.contacts.append(field)
					field.contacts.append(city)
					features = {'u':city,'r':city,'d':field,'l':field}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 2:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   cccccc-S-c| 
				###    |       cccccc|   
				###    |         cccc|  
				###    |           cc|   
				###    |            c|  
				###    ---------------
				for copy in range(copies):
					city = City(points=2,openings_count=2)
					field = Field()
					road = Road(openings_count=2)
					city.contacts.append(field)
					field.contacts.append(city)
					features = {'u':city,'r':city,'d':field,'l':field}
					temp_tile = Tile(type=tile_type,features = features,shield=True)
					temp_tiles.append(temp_tile)

			elif tile_type == 3:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   ccccccc   | 
				###    |             |   
				###    |      rrrrrrr|  
				###    |      r      |   
				###    |      r      |  
				###    ---------------
				for copy in range(copies):
					city = City(points=1,openings_count=1)
					field1 = Field()
					field2 = Field()
					road = Road(openings_count=2)
					city.contacts.append(field1)
					field1.contacts.append(city)
					features = {'u':city,'r':road,'d':road,'l':field1,'dr':field2,'dl':field1,'ru':field1,'rd':field2}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 4:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   ccccccc   | 
				###    |             |   
				###    |rrrrrrr      |  
				###    |      r      |   
				###    |      r      |  
				###    ---------------
				for copy in range(copies):
					city = City(points=1,openings_count=1)
					field1 = Field()
					field2 = Field()
					road = Road(openings_count=2)
					city.contacts.append(field1)
					field1.contacts.append(city)
					features = {'u':city,'r':field1,'d':road,'l':road,'dr':field1,'dl':field2,'lu':field1,'ld':field2}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 5:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   ccccccc   | 
				###    |             |   
				###    |             |  
				###    |             |   
				###    |             |  
				###    ---------------
				for copy in range(copies):
					city = City(points=1,openings_count=1)
					field = Field()
					city.contacts.append(field)
					field.contacts.append(city)
					features = {'u':city,'r':field,'d':field,'l':field}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 6:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   ccccccc   | 
				###    |             |   
				###    |             |  
				###    |   ccccccc   |   
				###    |ccccccccccccc|  
				###    ---------------
				for copy in range(copies):
					city1 = City(points=1,openings_count=1)
					city2 = City(points=1,openings_count=1)
					field = Field()
					city1.contacts.append(field)
					city2.contacts.append(field)
					field.contacts.extend([city1,city2])
					features = {'u':city1,'r':field,'d':city2,'l':field}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			self.tile_stack.update({tile_type:temp_tiles})

		self.all_tiles = []
		for tile_type,_ in self.tile_copies.items():
			self.all_tiles.extend(self.tile_stack[tile_type])

	def start_game(self):
		first_action = Action(tile=self.tile_stack[0][0],rotation=0,location=(0,0))
		self.make_action(first_action)

	def update_feature(self,feature,new_points,new_meeples,new_openings=None):
		feature.points = feature.points + new_points
		#feature.meeples = [feature.meeples[i] + new_meeples[i] for i in range(self.players)]
		if new_openings is not None:
			feature.openings_count = feature.openings_count + new_openings
		if feature.type != ['f'] and feature.openings_count <= 0:
			feature.complete = True

	def turn_shift(self):
		self.player_turn = self.player_turn + 1
		if self.player_turn >= self.players:
			self.player_turn = 0

	def mix_features(self,feature1,feature2):
		pass

	def get_adjacent_locations(self,location,side):
		if side in ['u','ur','ul']:
			return (location[0],location[1]+1)
		elif side in ['r','ru','rd']:
			return (location[0]+1,location[1])
		elif side in ['d','dr','dl']:
			return (location[0],location[1]-1)
		elif side in ['l','lu','ld']:
			return (location[0]-1,location[1])

	def rotate_features(self,features,rotation):
		if rotation == 0:
			return features
		else:
			rotated_features = {self.rotation_mappings[rotation][side]:feature for side,feature in features.items()}
			return rotated_features

	def get_random_tile(self):
		return rd.choice(self.all_tiles)

	def get_available_actions(self,tile):
		actions = []
		available_locations = self.get_available_locations(tile)
		for location,rotations in available_locations.items():
			for rotation in rotations:
				actions.append(Action(tile=tile,location=location,rotation=rotation))
		return actions

	def get_available_locations(self,tile):
		available_locations = {}
		for location,features in self.board.items():
			add_location = False
			rotations_to_add = []
			for rotation in self.rotations:
				temp_tile_features = self.rotate_features(tile.features,rotation)
				for side in self.main_sides:
					if features[side] is not None:
						if temp_tile_features[side].feature_type == features[side].feature_type:
							rotations_to_add.append(rotation)
							add_location = True
			if add_location:
				available_locations[location] = rotations_to_add
		return available_locations

	def remove_tile(self,tile):
		self.tile_stack[tile.type].remove(tile)
		self.all_tiles.remove(tile)

	def make_action(self,action):
		self.remove_tile(tile=action.tile)
		tile_features = self.rotate_features(action.tile.features,action.rotation)
		for side,feature in tile_features.items():
			adjacent_location = self.get_adjacent_locations(action.location,side)
			adjacent_side = self.adjacent_mappings[side]
			if self.board[adjacent_location][side] is None:
				self.board[adjacent_location].update({adjacent_side:feature})

			
Game = Carcassonne()
Game.start_game()
tile = Game.get_random_tile()
print(tile)
actions = Game.get_available_actions(tile)
print('options: ', len(actions))
for action in actions: print(action) 








