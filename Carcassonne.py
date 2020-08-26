
class Tile:
	def __init__(self,features,links):
		pass
		"""
		###      u0  u1  u2      
		###    ---------------   
		###    |ccccccccccccc|   
		### l2 |   ccccccc   | r0 
		###    |             |   
		### l1 |rrrrrrrrrrrrr| r1 
		###    |             |   
		### l0 |             | r2
		###    ---------------   
		###      b2  b1  b0 
		###     
		### f = field
		### c = city
		### r = road
		### m = monastery
		### features = [u0,u1,u2,l0,l1,l2,r0,r1,r2,b0, b1, b2]  
		###             f0,f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11
		### links = [(f1),(f4,f7),()] 
		"""


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

class Player:
	def __init__(self,meeples,index):
		self.index = index
		self.meeples = meeples
		self.score = 0
		self.virtual_score = 0

	def __str__(self):
		return "Player" + str(self.index) + ",meeples" +  str(self.meeples) + ",score" +  str(self.score) + ",virtual_score" +  str(self.virtual_score)

class Board_spot:
	def __init__(self
				,up=None
				,right=None
				,down=None
				,left=None
				,up_right=None
				,up_left=None
				,right_up=None
				,right_down=None
				,down_right=None
				,down_left=None
				,left_up=None
				,left_down=None):
		self.up=up
		self.right=right
		self.down=down
		self.left=left
		self.up_right=up_right
		self.up_left=up_right
		self.right_up=right_up
		self.right_down=right_down
		self.down_right=down_right
		self.down_left=down_left
		self.left_up=left_up
		self.left_down=left_down

class Carcassonne:
	def __init__(self,players=2,starting_meeples=(7,7),tile_stack=None):
		self.no_meeples = [0 for _ in range(players)]
		self.new_meeple = [[0 if p!=i else 1 for p in range(players)] for i in range(players)]
		self.city_count,self.road_count,self.field_count,self.monastery_count = 0,0,0,0
		self.cities = {}
		self.board = {}
		self.players={i:Player(meeples=starting_meeples[i],index=i) for i in range(players)}

		#Play starting tile
		new_city = self.create_city(meeples=self.no_meeples,openings_count=1)
		new_field1 = self.create_field(meeples=self.no_meeples)
		self.city_field_contact(new_city,new_field1)
		new_field2 = self.create_field(meeples=self.no_meeples)
		new_road = self.create_road(meeples=self.no_meeples,openings_count=2)
		self.board.update({(-1,0):Board_spot(left=new_road,left_up=new_field1,left_down=new_field2)
							,(0,-1):Board_spot(up=new_field2,up_left=new_field2,up_right=new_field2)
							,(1,0):Board_spot(right=new_road,right_up=new_field1,right_down=new_field2)
							,(0,1):Board_spot(down=new_city)})


	def create_city(self,meeples,openings_count=None):
		feature = City(index=self.city_count,meeples=meeples,openings_count=openings_count)
		self.cities[self.city_count] = feature
		self.city_count = self.city_count + 1
		print("Created feature ", feature)
		return feature

	def create_road(self,meeples,openings_count=None):
		feature = Road(index=self.road_count,meeples=meeples,openings_count=openings_count)
		self.road_count = self.road_count + 1
		print("Created feature ", feature)
		return feature

	def create_field(self,meeples):
		feature = Field(index=self.field_count,meeples=meeples)
		self.field_count = self.field_count + 1
		print("Created feature ", feature)
		return feature

	def create_monastery(self,meeples,openings_count=None):
		pass

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

Game = Carcassonne()
print(Game.board)
print(Game.board[(0,1)])
print(Game.board[(0,1)].down)
print(Game.board[(-1,0)].left)
print(Game.players)







