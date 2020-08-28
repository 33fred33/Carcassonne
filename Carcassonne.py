from collections import defaultdict


class City:
	def __init__(self,index,meeples,openings_count,points=1,contacts=[]):
		self.index = index
		self.points = points
		self.meeples = meeples
		self.openings_count = openings_count
		self.contacts = contacts
		self.feature = 'c'
		self.complete = False

	def get_score(self):
		if self.complete:
			return self.score * 2
		else:
			return self.score

	def __str__(self):
		return "City" + str(self.index) + ",meeples" + str(self.meeples) + ",fields" + str(self.contacts) + ",openings" + str(self.openings_count)


class Road:
	def __init__(self,index,meeples,openings_count,points=1):
		self.index = index
		self.points = points
		self.meeples = meeples
		self.openings_count = openings_count
		self.feature = 'r'
		self.complete = False

	def get_score(self):
		return self.points

	def __str__(self):
		return "Road" + str(self.index) + ",meeples" + str(self.meeples) + ",openings" + str(self.openings_count)

class Field:
	def __init__(self,index,meeples,contacts=[]):
		self.index = index
		self.feature = 'f'
		self.meeples = meeples
		self.contacts = contacts
		self.points = 0

	def get_score(self,cities):
		return sum([3 for city_index in self.contacts if cities[city_index].complete])

	def __str__(self):
		return "Field" + str(self.index) + ",meeples" + str(self.meeples) + ",cities" + str(self.contacts)

class Monastery:
	def __init__(self,index,meeples,openings_count):
		self.index = index
		self.meeples = meeples
		self.openings_count = openings_count
		self.feature = 'm'
		self.complete = False

	def get_score(self):
		return 9 - openings_count

	def __str__(self):
		return "Monastery" + str(self.index) + ",meeples" + str(self.meeples) + ",points" + str(self.get_score())

class Player:
	def __init__(self,meeples,index):
		self.index = index
		self.meeples = meeples
		self.score = 0
		self.virtual_score = 0

	def __str__(self):
		return "Player" + str(self.index) + ",meeples" +  str(self.meeples) + ",score" +  str(self.score) + ",virtual_score" +  str(self.virtual_score)

class Carcassonne:
	def __init__(self,players=2,starting_meeples=(7,7),tile_stack=None):
		self.no_meeples = [0 for _ in range(players)]
		self.new_meeple = [[0 if p!=i else 1 for p in range(players)] for i in range(players)]
		self.city_count,self.road_count,self.field_count,self.monastery_count = 0,0,0,0
		self.cities = {}
		self.players={i:Player(meeples=starting_meeples[i],index=i) for i in range(players)}
		self.sides=('u','r','d','l')
		self.feature_types=('c','r','f','m')
		self.links=('u','r','d','l','ul','ur','ru','rd','dl','dr','lu','ld')
		self.rotation_mappings = {1:{'u':'l','r':'u','d':'r','l':'d','ul':'ld','ur':'lu','ru':'ul','rd':'ur','dl':'rd','dr':'ru','lu':'dl','ld':'dr'},
								2:{'u':'d','r':'l','d':'u','l':'r','ul':'dr','ur':'dl','ru':'ld','rd':'lu','dl':'ur','dr':'ul','lu':'rd','ld':'ru'},
								3:{'u':'r','r':'d','d':'l','l':'u','ul':'ru','ur':'rd','ru':'dr','rd':'dl','dl':'lu','dr':'ld','lu':'ul','ld':'ur'}}
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

		#Tile database
		self.tile_sides = {0:{'u':'c','r':'r','d':'f','l':'r'},
						###    ---------------   
						###    |ccccccccccccc|   
						###    |   ccccccc   | 
						###    |             |   
						###    |rrrrrrrrrrrrr|  
						###    |             |   
						###    |             |  
						###    --------------- 
						1:{'u':'c','r':'f','d':'f','l':'f'},
						###    ---------------   
						###    |ccccccccccccc|   
						###    |   ccccccc   | 
						###    |             |   
						###    |             |  
						###    |             |   
						###    |             |  
						###    ---------------
						2:{'u':'c','r':'c','d':'f','l':'f'}
						###    ---------------   
						###    |ccccccccccccc|   
						###    |   cccccccccc| 
						###    |       cccccc|   
						###    |         cccc|  
						###    |           cc|   
						###    |            c|  
						###    ---------------
						}
		self.tile_features = {0:{'c':[['u']],'r':[['r','l']],'f':[['ld','d','rd'],['lu','ru']],'m':[[]],'cf':[[0,1]]},
							1:{'c':[['u']],'r':[[]],'f':[['l','d','r']],'m':[[]],'cf':[[0,0]]},
							2:{'c':[['u','r']],'r':[[]],'f':[['l','d']],'m':[[]],'cf':[[]]}}
		#'cf' needs to be last, in it: first city index, then field index

	#Play starting tile
		self.play_tile(tile_index=0,rotations=0,location=(0,0),meeples=self.no_meeples)

	def get_tile_sides(self,tile_index,rotations=0):
		if rotations==0:
			return self.tile_sides[tile_index]
		else:
			return {self.rotation_mappings[rotations][key]:value for key, value in self.tile_sides[tile_index].items()}

	def get_tile_features(self,tile_index,rotations=0):
		if rotations == 0:
			return self.tile_features[tile_index]
		else:
			return {key:[[self.rotation_mappings[rotations][i] if key!='cf' else i for i in link] for link in value] for key,value in self.tile_features[tile_index].items() }

	def create_feature(self,feature_type,location,meeples,openings):
		if feature_type == 'c':
			feature = City(index=self.city_count,meeples=meeples,openings_count=len(openings))
			self.cities[self.city_count] = feature
			self.city_count = self.city_count + 1

		elif feature_type == 'r':
			feature = Road(index=self.road_count,meeples=meeples,openings_count=len(openings))
			self.road_count = self.road_count + 1

		elif feature_type == 'f':
			feature = Field(index=self.field_count,meeples=meeples)
			self.field_count = self.field_count + 1

		elif feature_type == 'm':
			pass

		else: print("ERROR: create_feature method received a wrong feature_type")

		self.board[location].update({opening:feature for opening in openings})
		print("Created feature ", feature)
		return feature


	def city_field_contact(self,city,field):
		self.update_feature_contacts(city,new_contacts = [field.index])
		self.update_feature_contacts(field,new_contacts = [city.index])

	def update_feature_contacts(self,feature,new_contacts=[],deleted_contacts=[]):
		feature.contacts = feature.contacts + new_contacts
		for contact in deleted_contacts:
			feature.contacts.remove(contact)

	def update_feature(self,feature,new_points,new_meeples,new_openings=None):
		feature.points = feature.points + new_points
		feature.meeples = [feature.meeples[i] + new_meeples[i] for i in range(self.players)]
		if new_openings is not None:
			feature.openings_count = feature.openings_count + new_openings
		if feature.type != ['f'] and feature.openings_count <= 0:
			feature.complete = True

	def mix_features(self,feature1,feature2):
		pass

	def play_tile(self,tile_index,rotations,location,meeples,meeple_feature=None,meeple_feature_index=None):
		tile_features = self.get_tile_features(tile_index,rotations)
		for feature_type,links in tile_features.items():
			if feature_type == 'c':
				for feature_index,openings in enumerate(links):
					if meeple_feature == feature_type and meeple_feature_index == feature_index:
						meeples = meeples
					else:
						meeples = self.no_meeples
					if sum([self.board[location][opening] == None for opening in openings]) == len(openings):
						self.create_feature(feature_type=feature_type,location=location,meeples=meeples,openings=openings)

			if feature_type == 'r':
				for feature_index,openings in enumerate(links):
					if meeple_feature == feature_type and meeple_feature_index == feature_index:
						meeples = meeples
					else:
						meeples = self.no_meeples
					if sum([self.board[location][opening] == None for opening in openings]) == len(openings):
						self.create_feature(feature_type=feature_type,location=location,meeples=meeples,openings=openings)

			if feature_type == 'f':
				for feature_index,openings in enumerate(links):
					if meeple_feature == feature_type and meeple_feature_index == feature_index:
						meeples = meeples
					else:
						meeples = self.no_meeples
					if sum([self.board[location][opening] == None for opening in openings]) == len(openings):
						self.create_feature(feature_type=feature_type,location=location,meeples=meeples,openings=openings)

			if feature_type == 'cf':
				for contacts in tile_features['cf']:
					self.city_field_contact(self.board[location][tile_features['c'][contacts[0]][0]],
											self.board[location][tile_features['f'][contacts[1]][0]])






Game = Carcassonne()
print(Game.board[(0,0)]['u'])
print(Game.board[(0,0)]['l'])
print(Game.board[(0,0)]['d'])








