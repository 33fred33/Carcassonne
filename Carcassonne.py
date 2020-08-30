from collections import defaultdict
import random as rd

class City:
	def __init__(self,openings_count=1,points=1,meeples={}):
		self.points = points
		self.openings_count = openings_count
		self.contacts = []
		self.feature_type = 'c'
		self.complete = False
		self.newest = None
		self.meeples = defaultdict(lambda:0,meeples)
		if meeples == {}:
			self.has_meeple=False
		else:
			self.has_meeple=True
			self.meeples.update(meeples)

	def get_score(self):
		if self.complete:
			return self.score * 2
		else:
			return self.score

	def get_newest(self):
		if self.newest is None:
			return self
		else:
			return self.newest

	def __str__(self):
		return "City ,fields" + str(len(self.contacts)) + ",openings" + str(self.openings_count)


class Road:
	def __init__(self,openings_count=1,points=1,meeples={}):
		self.points = points
		self.openings_count = openings_count
		self.feature_type = 'r'
		self.complete = False
		self.newest = None
		self.meeples = defaultdict(lambda:0,meeples)
		if meeples == {}:
			self.has_meeple=False
		else:
			self.has_meeple=True
			self.meeples.update(meeples)

	def get_score(self):
		return self.points

	def get_newest(self):
		if self.newest is None:
			return self
		else:
			return self.newest

	def __str__(self):
		return "Road ,openings" + str(self.openings_count)

class Field:
	def __init__(self,meeples={}):
		self.feature_type = 'f'
		self.contacts = []
		self.points = 0
		self.newest = None
		self.meeples = defaultdict(lambda:0,meeples)
		if meeples == {}:
			self.has_meeple=False
		else:
			self.has_meeple=True
			self.meeples.update(meeples)


	def get_score(self,cities):
		return sum([3 for city in self.contacts if city.get_newest().complete])

	def get_newest(self):
		if self.newest is None:
			return self
		else:
			return self.newest

	def __str__(self):
		return "Field ,cities" + str(len(self.contacts))

class Monastery:
	def __init__(self,openings_count,meeples={}):
		self.meeples = meeples
		self.openings_count = openings_count
		self.feature = 'm'
		self.complete = False
		self.meeples = defaultdict(lambda:0,meeples)
		if meeples == {}:
			self.has_meeple=False
		else:
			self.has_meeple=True
			self.meeples.update(meeples)

	def get_score(self):
		return 9 - openings_count

	def __str__(self):
		return "Monastery ,points" + str(self.get_score())

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
		return 'Action. location:' + str(self.location) + ' ,rotation:' + str(self.rotation) + ' ,meeples:' + str(self.meeples)+ ' ,meeple_feature:' + str(self.meeple_feature)

class Tile:
	def __init__(self,type,features,rotations=[0,1,2,3],monastery=None,shield=False):
		self.rotation_mappings = {1:{'u':'l','r':'u','d':'r','l':'d','ul':'ld','ur':'lu','ru':'ul','rd':'ur','dl':'rd','dr':'ru','lu':'dl','ld':'dr'},
								2:{'u':'d','r':'l','d':'u','l':'r','ul':'dr','ur':'dl','ru':'ld','rd':'lu','dl':'ur','dr':'ul','lu':'rd','ld':'ru'},
								3:{'u':'r','r':'d','d':'l','l':'u','ul':'ru','ur':'rd','ru':'dr','rd':'dl','dl':'lu','dr':'ld','lu':'ul','ld':'ur'}}
		self.type = type
		self.features = features
		self.shield = shield
		self.monastery = monastery
		self.rotations = rotations

	def get_all_features(self):
		return list(set([feature for _,feature in self.features.items()]))

	def get_feature_sides(self,feature,rotation=0):
		feature_sides = [side for side,temp_feature in self.features.items() if temp_feature==feature]
		if rotation==0:
			return feature_sides
		else:
			rotated_feature_sides = [self.rotation_mappings[rotation][side] for side in feature_sides]
			return rotated_feature_sides

	def get_rotated_features(self,rotation):
		if rotation == 0:
			return self.features
		else:
			rotated_features = {self.rotation_mappings[rotation][side]:feature for side,feature in self.features.items()}
			return rotated_features

	def __str__(self):
		return 'Tile. type:' + str(self.type)

class Carcassonne:
	def __init__(self,players=2,starting_meeples={0:7,1:7},tile_copies={0:4,1:3,2:2,3:3,4:3,5:5,6:3,7:2,8:3,9:1,10:1,11:2,12:1,13:1,14:4,15:8,16:9,17:2,18:4,19:3,20:2,21:3,22:1,23:2}):
		self.players = {i:Player(meeples=starting_meeples[i],index=i) for i in range(players)}
		self.player_count = players
		self.player_turn = 0
		self.city_count,self.road_count,self.field_count,self.monastery_count = 0,0,0,0
		self.main_sides=('u','r','d','l')
		self.feature_types=('c','r','f','m')
		self.sides=('u','r','d','l','ul','ur','ru','rd','dl','dr','lu','ld')
		self.rotation_mappings = {0:{s:s for s in self.sides},
								1:{'u':'l','r':'u','d':'r','l':'d','ul':'ld','ur':'lu','ru':'ul','rd':'ur','dl':'rd','dr':'ru','lu':'dl','ld':'dr'},
								2:{'u':'d','r':'l','d':'u','l':'r','ul':'dr','ur':'dl','ru':'ld','rd':'lu','dl':'ur','dr':'ul','lu':'rd','ld':'ru'},
								3:{'u':'r','r':'d','d':'l','l':'u','ul':'ru','ur':'rd','ru':'dr','rd':'dl','dl':'lu','dr':'ld','lu':'ul','ld':'ur'}}
		self.adjacent_mappings = {'u':'d','r':'l','d':'u','l':'r','ul':'dr','ur':'dl','ru':'lu','rd':'ld','dl':'ur','dr':'ul','lu':'ru','ld':'rd'}
		self.tile_copies = tile_copies
		self.all_tiles = {}
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
					city = City()
					road = Road(openings_count=2)
					field1,field2 = Field(),Field()
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
					city = City()
					field1,field2 = Field(),Field()
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
					city = City()
					field1,field2 = Field(),Field()
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
					city = City()
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
					city1,city2 = City(),City()
					field = Field()
					city1.contacts.append(field)
					city2.contacts.append(field)
					field.contacts.extend([city1,city2])
					features = {'u':city1,'r':field,'d':city2,'l':field}
					temp_tile = Tile(type=tile_type,features = features,rotations=[0,1])
					temp_tiles.append(temp_tile)

			elif tile_type == 7:
				###    ---------------   
				###    |cccccccccccc |   
				###    |   ccccccc cc| 
				###    |          ccc|   
				###    |          ccc|  
				###    |           cc|   
				###    |            c|  
				###    ---------------
				for copy in range(copies):
					city1,city2 = City(),City()
					field = Field()
					city1.contacts.append(field)
					city2.contacts.append(field)
					field.contacts.extend([city1,city2])
					features = {'u':city1,'r':city2,'d':field,'l':field}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 8:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   cccccccccc| 
				###    |    ccccccccc|   
				###    |    ccccccccc|  
				###    |   cccccccccc|   
				###    |ccccccccccccc|  
				###    ---------------
				for copy in range(copies):
					city = City(openings_count=3)
					field = Field()
					city.contacts.append(field)
					field.contacts.append(city)
					features = {'u':city,'r':city,'d':city,'l':field}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 9:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   cccccc-S-c| 
				###    |    ccccccccc|   
				###    |    ccccccccc|  
				###    |   cccccccccc|   
				###    |ccccccccccccc|  
				###    ---------------
				for copy in range(copies):
					city = City(points=2,openings_count=3)
					field = Field()
					city.contacts.append(field)
					field.contacts.append(city)
					features = {'u':city,'r':city,'d':city,'l':field}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 10:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   cccccccccc| 
				###    |    ccccccccc|   
				###    |rrr ccccccccc|  
				###    |   cccccccccc|   
				###    |ccccccccccccc|  
				###    ---------------
				for copy in range(copies):
					city = City(openings_count=3)
					field1,field2 = Field(),Field()
					road = Road()
					city.contacts.extend([field1,field2])
					field.contacts.append(city)
					features = {'u':city,'r':city,'d':city,'l':road,'lu':field1,'ld':field2}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 11:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   cccccc-S-c| 
				###    |    ccccccccc|   
				###    |rrr ccccccccc|  
				###    |   cccccccccc|   
				###    |ccccccccccccc|  
				###    ---------------
				for copy in range(copies):
					city = City(points=2,openings_count=3)
					field1,field2 = Field(),Field()
					road = Road()
					city.contacts.extend([field1,field2])
					field.contacts.append(city)
					features = {'u':city,'r':city,'d':city,'l':road,'lu':field1,'ld':field2}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 12:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |ccccccccc-S-c| 
				###    |ccccccccccccc|   
				###    |ccccccccccccc|  
				###    |ccccccccccccc|   
				###    |ccccccccccccc|  
				###    ---------------
				for copy in range(copies):
					city = City(points=2,openings_count=4)
					features = {'u':city,'r':city,'d':city,'l':city}
					temp_tile = Tile(type=tile_type,features = features,rotations=[0])
					temp_tiles.append(temp_tile)

			elif tile_type == 13:
				###    ---------------   
				###    |      r      |   
				###    |      r      | 
				###    |      r      |   
				###    |rrrrr   rrrrr|  
				###    |      r      |   
				###    |      r      |  
				###    ---------------
				for copy in range(copies):
					road1,road2,road3,road4 = Road(),Road(),Road(),Road()
					field1,field2,field3,field4 = Field(),Field(),Field(),Field()
					features = {'u':road1,'r':road2,'d':road3,'l':road4,'ul':field1,'ur':field2,'ru':field2,'rd':field3,'dl':field4,'dr':field3,'lu':field1,'ld':field4}
					temp_tile = Tile(type=tile_type,features = features,rotations=[0])
					temp_tiles.append(temp_tile)

			elif tile_type == 14:
				###    ---------------   
				###    |             |   
				###    |             | 
				###    |             |   
				###    |rrrrr   rrrrr|  
				###    |      r      |   
				###    |      r      |  
				###    ---------------
				for copy in range(copies):
					road1,road2,road3 = Road(),Road(),Road()
					field1,field2,field3 = Field(),Field(),Field()
					features = {'u':field1,'r':road2,'d':road3,'l':road4,'ru':field1,'rd':field2,'dl':field3,'dr':field2,'lu':field1,'ld':field3}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 15:
				###    ---------------   
				###    |             |   
				###    |             | 
				###    |             |   
				###    |rrrrrrrrrrrrr|  
				###    |             |   
				###    |             |  
				###    ---------------
				for copy in range(copies):
					road = Road(openings_count=2)
					field1,field2= Field(),Field()
					features = {'u':field1,'r':road,'d':field2,'l':road,'ru':field1,'rd':field2,'lu':field1,'ld':field2}
					temp_tile = Tile(type=tile_type,features = features,rotations=[0,1])
					temp_tiles.append(temp_tile)

			elif tile_type == 16:
				###    ---------------   
				###    |             |   
				###    |             | 
				###    |             |   
				###    |      rrrrrrr|  
				###    |      r      |   
				###    |      r      |  
				###    ---------------
				for copy in range(copies):
					field1,field2 = Field(),Field()
					road = Road(openings_count=2)
					features = {'u':field1,'r':road,'d':road,'l':field1,'dr':field2,'dl':field1,'ru':field1,'rd':field2}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 17:
				###    ---------------   
				###    |             |   
				###    |             | 
				###    |     mmm     |   
				###    |     mmm     |  
				###    |      r      |   
				###    |      r      |  
				###    ---------------
				for copy in range(copies):
					field = Field()
					road = Road()
					features = {'u':field,'r':field,'d':road,'l':field}
					temp_tile = Tile(type=tile_type,features = features,monastery=True)
					temp_tiles.append(temp_tile)

			elif tile_type == 18:
				###    ---------------   
				###    |             |   
				###    |             | 
				###    |     mmm     |   
				###    |     mmm     |  
				###    |             |   
				###    |             |  
				###    ---------------
				for copy in range(copies):
					field = Field()
					features = {'u':field,'r':field,'d':field,'l':field}
					temp_tile = Tile(type=tile_type,features = features,monastery=True,rotations=[0])
					temp_tiles.append(temp_tile)

			elif tile_type == 19:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   cccccccccc| 
				###    |       cccccc|   
				###    |rrrrrr   cccc|  
				###    |      r    cc|   
				###    |      r     c|  
				###    ---------------
				for copy in range(copies):
					city = City(openings_count=2)
					field1,field2 = Field(),Field()
					road = Road(openings_count=2)
					city.contacts.append(field1)
					field1.contacts.append(city)
					features = {'u':city,'r':city,'d':road,'l':road,'dl':field2,'dr':field1,'lu':field1,'ld':field2}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 20:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   cccccc-S-c| 
				###    |       cccccc|   
				###    |rrrrrr   cccc|  
				###    |      r    cc|   
				###    |      r     c|  
				###    ---------------
				for copy in range(copies):
					city = City(points=2,openings_count=2)
					field1,field2 = Field(),Field()
					road = Road(openings_count=2)
					city.contacts.append(field1)
					field1.contacts.append(city)
					features = {'u':city,'r':city,'d':road,'l':road,'dl':field2,'dr':field1,'lu':field1,'ld':field2}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 21:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |  ccccccccc  | 
				###    |             |   
				###    |rrrrr   rrrrr|  
				###    |      r      |   
				###    |      r      |  
				###    ---------------
				for copy in range(copies):
					road1,road2,road3 = Road(),Road(),Road()
					field1,field2,field3 = Field(),Field(),Field()
					city = City()
					features = {'u':city,'r':road2,'d':road3,'l':road4,'ru':field1,'rd':field2,'dl':field3,'dr':field2,'lu':field1,'ld':field3}
					temp_tile = Tile(type=tile_type,features = features)
					temp_tiles.append(temp_tile)

			elif tile_type == 22:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   cccccccc  | 
				###    |    cccccc   |   
				###    |    cccccc   |  
				###    |   cccccccc  |   
				###    |ccccccccccccc|  
				###    ---------------
				for copy in range(copies):
					city = City(openings_count=2)
					field1,field2 = Field(),Field()
					city.contacts.extend([field1,field2])
					field.contacts.append(city)
					features = {'u':city,'r':field1,'d':city,'l':field2}
					temp_tile = Tile(type=tile_type,features = features,rotations=[0,1])
					temp_tiles.append(temp_tile)

			elif tile_type == 23:
				###    ---------------   
				###    |ccccccccccccc|   
				###    |   cccc-S-c  | 
				###    |    cccccc   |   
				###    |    cccccc   |  
				###    |   cccccccc  |   
				###    |ccccccccccccc|  
				###    ---------------
				for copy in range(copies):
					city = City(points=2,openings_count=2)
					field1,field2 = Field(),Field()
					city.contacts.extend([field1,field2])
					field.contacts.append(city)
					features = {'u':city,'r':field1,'d':city,'l':field2}
					temp_tile = Tile(type=tile_type,features = features,rotations=[0,1])
					temp_tiles.append(temp_tile)

			self.all_tiles.update({tile_type:temp_tiles})

		self.tile_stack = []
		for tile_type,_ in self.tile_copies.items():
			self.tile_stack.extend(self.all_tiles[tile_type])

	def start_game(self,seed=None):
		first_action = Action(tile=self.all_tiles[0][0],rotation=0,location=(0,0))
		self.make_action(first_action)

		self.seed = seed
		if self.seed is not None:
			rd.seed(self.seed)
		rd.shuffle(self.tile_stack)

	def get_next_tile(self):
		return self.tile_stack[0]

	def update_feature(self,feature,new_points,new_meeples,new_openings=None):
		feature.points = feature.points + new_points
		#feature.meeples = [feature.meeples[i] + new_meeples[i] for i in range(self.players)]
		if new_openings is not None:
			feature.openings_count = feature.openings_count + new_openings
		if feature.type != ['f'] and feature.openings_count <= 0:
			feature.complete = True

	def turn_shift(self):
		self.player_turn = self.player_turn + 1
		if self.player_turn >= self.player_count:
			self.player_turn = 0

	def get_adjacent_location(self,location,side):
		if side in ['u','ur','ul']:
			return (location[0],location[1]+1)
		elif side in ['r','ru','rd']:
			return (location[0]+1,location[1])
		elif side in ['d','dr','dl']:
			return (location[0],location[1]-1)
		elif side in ['l','lu','ld']:
			return (location[0]-1,location[1])

	def get_random_tile(self):
		return rd.choice(self.tile_stack)

	def get_available_actions(self,tile):
		actions = []
		available_locations = self.get_available_locations(tile)
		for location,rotations in available_locations.items():
			for rotation in rotations:
				actions.append(Action(tile=tile,location=location,rotation=rotation))

		actions_to_add = []
		for action in actions:
			for feature in action.tile.get_all_features():
				rotated_feature_sides = action.tile.get_feature_sides(feature=feature,rotation=action.rotation)
				add_meeple = True
				for side in rotated_feature_sides:
					if self.board[action.location][side] is not None:
						if self.board[action.location][side].has_meeple:
							add_meeple = False
				if add_meeple:
					actions_to_add.append(Action(tile=action.tile,location=action.location,rotation=action.rotation,meeples={self.player_turn:1},meeple_feature=feature))

		actions.extend(actions_to_add)
		return actions

	def get_available_locations(self,tile):
		available_locations = {}
		for location,features in self.board.items():
			add_location = False
			rotations_to_add = []
			for rotation in tile.rotations:
				temp_tile_features = tile.get_rotated_features(rotation=rotation)
				for side in self.main_sides:
					if features[side] is not None:
						if temp_tile_features[side].feature_type == features[side].feature_type:
							rotations_to_add.append(rotation)
							add_location = True
			if add_location:
				available_locations[location] = rotations_to_add
		return available_locations

	def remove_tile(self,tile):
		self.all_tiles[tile.type].remove(tile)
		self.tile_stack.remove(tile)

	def make_action(self,action):
		self.remove_tile(tile=action.tile)
		tile_features = action.tile.get_rotated_features(rotation=action.rotation)
		updated_features = {side:feature.get_newest() for side,feature in tile_features.items()}
		"""
		for feature in action.tile.get_all_features():
			rotated_feature_sides = action.tile.get_feature_sides(feature=feature)
			matching_features = [self.board[action.location][side] for side in ]
		"""
		

		for side,feature in updated_features.items():
			adjacent_location = self.get_adjacent_location(action.location,side)
			adjacent_side = self.adjacent_mappings[side]
			if self.board[adjacent_location][side] is None:
				self.board[adjacent_location].update({adjacent_side:feature})


		self.turn_shift()

			
Game = Carcassonne()
Game.start_game(seed=1)
print('tile_stack:', [tile.type for tile in Game.tile_stack])
tile = Game.get_next_tile()
print(tile)
actions = Game.get_available_actions(tile)
print('options: ', len(actions))
for action in actions: print(action) 








