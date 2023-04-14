import random
import copy


'''
Initializing game board with builtin dictionary data structure
* Game's rule for this version of Monopoly:
    1. Eliminated Chances and Community chest cards.
    2. No Trade and Auction.
    3. No double dice rule(i mean if 3 times happend then player should go to jail).
    4. One action per turn.
    5. No color(it means streets dont have any color and if player landed on a street can buy it and build house and hotels for it).
    6. No sell option(yet).
'''
class stats:
    def __init__(self, id, location, balance, jail, ownedP, ownedRR, ownedUT):
        self.id = id # store the id of each player (int: 1 , 2)
        self.location = location  # store the location of the player (string or index of dictionary)
        self.balance = balance  # store the amount of money the player has (int data)
        self.jail = jail  # store whether the player is in jail or not (bool data)
        self.ownedP = ownedP  # store the properties that the player has bought (list of property names or index)
        self.ownedRR = ownedRR  # store the railroads that the player has bought (list of railroad names or index)
        self.ownedUT = ownedUT  # store the utilities that the player has bought (list of utility names or index)

# set up players with stats class
player = {}
for count in range(0, 3):
    if count == 0: # this is for ignoring 0 index and just count 1 and 2 as players.
        player.update({count: stats(0, 0, 0, False, [], [], [])})
    else:
        player.update({count: stats(count, 0, 1500, False, [],[], [])})

number_of_players = 2 #player
current_player = 1 #current
flag = False
player_left = number_of_players #pleft

# defining some important functions:
# roll dice return a tuple of two numbers that they generated randomly.
def roll_dice():
    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    return (dice1, dice2)

# updates players location.
def move_player(player, rolls): 
    current_location = player.location
    
    roll = rolls[0] + rolls[1]
    
    # calculate the new location by adding the roll to the current location
    new_location = (current_location + roll) % 34
    
    # check if the player passed Go
    if new_location < current_location:
        print(f"{player} passed GO and collected 200$.")
        player.balance += 200
    
    # update the player's location
    player.location = new_location

def is_terminal(player):
     if player.balance <= 0:
         return True
     return False

def purchase(player):
     prop_type = properties[player.location]["type"]
     owner_id  = properties[player.location]["owner"]

     if  prop_type in ["property", "railroad", "utility"] and owner_id == "none":
          properties[player.location]["owner"] =  player.id
          player.balance -= properties[player.location]["price"]
          
          if prop_type == "property":
               player.ownedP.append(player.location)
          
          elif prop_type == "railroad":
               player.ownedRR.append(player.location) 

          elif prop_type == "utility":
               player.ownedUT.append(player.location) 
     
     elif owner_id != "none":
          raise ValueError("This propertie is owned by other player(ownership error)")
    
     else:
          raise ValueError("You can't buy this place(type error)")

def charge_rent(player):
     rent = properties[player.location]["rent"]
     owner_id = properties[player.location]["owner"]

     if owner_id != "none" and owner_id != player.id:
          if properties[player.location]["hotel"] == 0:
               player.balance = player.balance - (rent + 10*properties[player.location]["houses"])
               player[owner_id].balance = player[owner_id].balance + (rent + 10*properties[player.location]["houses"])
               print(f"{player.id} paid {rent + 10*properties[player.location]['houses']}$ to {owner_id}") 
          else:
               player.balance = player.balance - (rent + 10*(properties[player.location]["houses"] + 1))
               player[owner_id].balance = player[owner_id].balance + (rent + 10*(properties[player.location]["houses"] + 1))
               print(f"{player.id} paid {rent + 10*properties[player.location]['hotel']}$ to {owner_id}") 
     
     else:
          #Either this property is not owned by any player or the player is the owner of this property.
          raise ValueError(f"Error: Unable to charge rent from {player.id}.") 

def build_house(player, property):
     # Check if the property belongs to the player and is a valid property to build on
     if property in player.ownedP and properties[property]["houses"] < 4:
          
          # Check if the player has enough money to build a house
          if player.balance >= properties[property]["hprice"]:
               # Subtract the cost of the house from the player's balance
               player.balance -= properties[property]["hprice"]
               # Increase the number of houses on the property by 1
               properties[property]["houses"] += 1
               print(f"{player.name} built a house on {property}")
          else:
               raise ValueError(f"{player.name} doesn't have enough money to build a house on {property}")
     else:
          raise ValueError(f"{property} is not a valid property to build a house on or it doesn't belong to {player.name}")
     
def build_hotel(player, property):
     if property in player.ownedP and properties[property]["type"] == "property" and properties[property]["houses"] == 4:
          if player.balance >= properties[property]["hprice"]:
               player.balance -= properties[property]["hprice"]
               properties[property]["houses"] = 0
               properties[property]["houses"] = True
               print(f"{player.id} built a hotel on {properties[property]['name']} for {properties[property]['hprice']}$")
          else:
               raise ValueError("Insufficient funds to build hotel")
     else:
          raise ValueError("Cannot build hotel on this property")
     
def switch_player(current_player) -> int:
     if current_player == 1:
          return 2
     else:
          return 1

def get_valid_actions(player):
     actions = []

     if properties[player.location]["name"] in ["Go", "Just Visiting/Jail", "Free Parking"]:
          actions.append(all_actions[0])
          
     elif properties[player.location]["name"] == "Go To Jail":
          actions.append(all_actions[6])

     # Check if player is on a property
     elif properties[player.location]["type"] in ["property", "railroad", "utility"]:
          # Check if the property is unowned
          if properties[player.location]["owner"] == "none":
               # Add the "BUY_PROP" action
               actions.append(all_actions[0])
               actions.append(all_actions[1])
          elif properties[player.location]["owner"] != player.id :
               # Add the "PAY_RENT" action
               actions.append(all_actions[2])
          elif properties[player.location]["type"] == "property":
               # Add the "BUILD_HOUSE" or "BUILD_HOTEL" action
               if player.balance >= properties[player.location]["hprice"] and properties[player.location]["houses"] < 4:
                    # Add the "BUILD_HOUSE" action
                    actions.append(all_actions[0])
                    actions.append(all_actions[4])
          
               # Check if player has enough money to build a hotel
               elif player.balance >= properties[player.location]["hprice"]:
                    # Add the "BUILD_HOTEL" action
                    actions.append(all_actions[0])
                    actions.append( all_actions[5])
     
     # Check if player is on tax
     elif properties[player.location]["type"] == "tax":
          # Add the "PAY_TAX" action
          actions.append(all_actions[3])

     return actions

def evaluate_utility(player):
     net_worth = 0
     for prop_loc in player.ownedP:
          if properties[prop_loc]["hotel"] == 0:
               net_worth += properties[prop_loc]["rent"]+ 10*properties[prop_loc]["houses"]
          else:
               net_worth += properties[prop_loc]["rent"]+ 10*(properties[prop_loc]["houses"] + 1)
     
     for rr_loc in player.ownedRR:
          net_worth += properties[rr_loc]["rent"]
     
     for ut_loc in player.ownedUT:
          net_worth += properties[ut_loc]["rent"]
          
     net_worth += player.balance

     return net_worth


def transition(player, action):
     new_properties = copy.deepcopy(properties)
     new_player = copy.deepcopy(player)

     # Execute action
     if action == all_actions[1]: # Buy property
          new_player.balance -= new_properties[new_player.location]["price"]
          new_player.ownedP.append(new_player.location)
          new_properties[new_player.location]["owner"] = new_player.id

     elif action == all_actions[0]: # Don't buy property
          pass

     elif action == all_actions[2]: # Pay rent
          charge_rent(new_player)
          
     elif action == all_actions[3]: # Pay tax
          new_player.balance -= new_properties[new_player.location]["tax_price"]
          
     elif action == all_actions[4]: # Build house
          build_house(new_player, new_player.location)
          
     elif action == all_actions[5]: # Build hotel
          build_hotel(new_player, new_player.location)
          
     elif action == all_actions[6]: # Jail free
          new_player.location = 8
          new_player.balance -= 100
     
     return new_player, new_properties








# properties
properties = {0: {"name": "Go",
                  "price": 0,
                  "rent": 0, 
                  "color": "none", 
                  "type": "corner", 
                  "owner": "none", 
                  "houses": 0, 
                  "hotels": 0},
              
              1: {"name": "Mediterranean Avenue", 
                  "price": 60, 
                  "hPrice": 50, 
                  "rent": 2, 
                  "color": "brown", 
                  "type": "property", 
                  "owner": "none", 
                  "houses": 0, 
                  "hotels": 0},
              
              2: {"name": "Baltic Avenue", 
                  "price": 60, 
                  "hPrice": 50, 
                  "rent": 4, 
                  "color": "brown", 
                  "type": "property", 
                  "owner": "none", 
                  "houses": 0, 
                  "hotels": 0},
              
              3: {"name": "Income Tax", 
                  "price": 0, 
                  "rent": 0, 
                  "color": "none", 
                  "type": "tax",
                  "tax_price": 200,
                  "owner": "none", 
                  "houses": 0, 
                  "hotels": 0},
              
              4: {"name": "Reading Railroad", 
                  "price": 200, 
                  "rent": 25, 
                  "color": "none", 
                  "type": "railroad", 
                  "owner": "none", 
                  "houses": 0, 
                  "hotels": 0},
              
              5: {"name": "Oriental Avenue", 
                  "price": 100, 
                  "rent": 6, 
                  "color": "light blue", 
                  "type": "property", 
                  "owner": "none", 
                  "houses": 0, 
                  "hotels": 0},
              
              6: {"name": "Vermont Avenue", 
                  "price": 100, 
                  "hPrice": 50, 
                  "rent": 6, 
                  "color": "light blue", 
                  "type": "property", 
                  "owner": "none", 
                  "houses": 0, 
                  "hotels": 0},
              
              7: {"name": "Connecticut Avenue", 
                  "price": 120, 
                  "hPrice": 50, 
                  "rent": 8, 
                  "color": "light blue", 
                  "type": "property", 
                  "owner": "none", 
                  "houses": 0, 
                  "hotels": 0},
              
              8: {"name": "Just Visiting/Jail", 
                   "price": 0, 
                   "rent": 0, 
                   "color": "none", 
                   "type": "corner", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              9: {"name": "St. Charles Place", 
                   "price": 140, 
                   "hPrice": 100, 
                   "rent": 10, 
                   "color": "pink", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              10: {"name": "Electric Company",
                   "price": 150, 
                   "rent": 20, 
                   "color": "none", 
                   "type": "utility", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              11: {"name": "States Avenue", 
                   "price": 140, 
                   "hPrice": 100, 
                   "rent": 10, 
                   "color": "pink", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              12: {"name": "Virginia Avenue", 
                   "price": 160, 
                   "hPrice": 100, 
                   "rent": 12, 
                   "color": "pink", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              13: {"name": "Pennsylvania Railroad", 
                   "price": 200, 
                   "rent": 25, 
                   "color": "none", 
                   "type": "railroad", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              14: {"name": "St. James Place", 
                   "price": 180, 
                   "hPrice": 100, 
                   "rent": 14, 
                   "color": "orange", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              15: {"name": "Tennessee Avenue", 
                   "price": 180, 
                   "hPrice": 100, 
                   "rent": 14, 
                   "color": "orange", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              16: {"name": "New York Avenue", 
                   "price": 200, 
                   "hPrice": 100, 
                   "rent": 16, 
                   "color": "orange", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              17: {"name": "Free Parking", 
                   "price": 0, 
                   "rent": 0, 
                   "color": "none", 
                   "type": "corner", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              18: {"name": "Kentucky Avenue", 
                   "price": 220, 
                   "hPrice": 150, 
                   "rent": 18, 
                   "color": "red", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              19: {"name": "Indiana Avenue", 
                   "price": 220, 
                   "hPrice": 150, 
                   "rent": 18, 
                   "color": "red", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              20: {"name": "Illinois Avenue", 
                   "price": 240, 
                   "hPrice": 150, 
                   "rent": 20, 
                   "color": "red", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              21: {"name": "B. & O. Railroad", 
                   "price": 200, 
                   "rent": 25, 
                   "color": "none", 
                   "type": "railroad", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              22: {"name": "Atlantic Avenue", 
                   "price": 260, 
                   "hPrice": 150, 
                   "rent": 22, 
                   "color": "yellow", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              23: {"name": "Ventnor Avenue", 
                   "price": 260, 
                   "hPrice": 150, 
                   "rent": 22, 
                   "color": "yellow", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              24: {"name": "Water Works", 
                   "price": 150, 
                   "rent": 20, 
                   "color": "none", 
                   "type": "utility", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              25: {"name": "Marvin Gardens", 
                   "price": 280, 
                   "hPrice": 150, 
                   "rent": 24, 
                   "color": "yellow", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              26: {"name": "Go To Jail", 
                   "price": 0, 
                   "rent": 0, 
                   "color": "none", 
                   "type": "corner", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              27: {"name": "Pacific Avenue", 
                   "price": 300, 
                   "hPrice": 200, 
                   "rent": 26, 
                   "color": "green", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              28: {"name": "North Carolina Avenue", 
                   "price": 300, 
                   "hPrice": 200, 
                   "rent": 26, 
                   "color": "green", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              29: {"name": "Pennsylvania Avenue", 
                   "price": 320, 
                   "hPrice": 200, 
                   "rent": 28, 
                   "color": "green", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              30: {"name": "Short Line", 
                   "price": 200, 
                   "rent": 25, 
                   "color": "none", 
                   "type": "railroad", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              31: {"name": "Park Place", 
                   "price": 350, 
                   "hPrice": 200, 
                   "rent": 35, 
                   "color": "dark blue", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              32: {"name": "Luxury Tax", 
                   "price": 0, 
                   "rent": 0, 
                   "color": "none", 
                   "type": "tax", 
                   "tax_price": 100,
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0},
              
              33: {"name": "Boardwalk",
                   "price": 400, 
                   "hPrice": 200, 
                   "rent": 50, 
                   "color": "dark blue", 
                   "type": "property", 
                   "owner": "none", 
                   "houses": 0, 
                   "hotels": 0}
             }

all_actions = {
    0: "NOTHING",
    1: "BUY_PROP",
    2: "PAY_RENT",
    3: "PAY_TAX",
    4: "BUILD_HOUSE",
    5: "BUILD_HOTEL",
    6: "JAIL_FREE"        
}

probability = {
    2: 1 / 36,
    3: 2 / 36,
    4: 3 / 36,
    5: 4 / 36,
    6: 5 / 36,
    7: 6 / 36,
    8: 5 / 36,
    9: 4 / 36,
    10: 3 / 36,
    11: 2 / 36,
    12: 1 / 36,
}