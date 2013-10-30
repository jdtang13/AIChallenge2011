#!/usr/bin/env python
from ants import *

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
class MyBot:
    def __init__(self):
        # define class level variables, will be remembered between turns
        pass
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        self.hills = []

        self.seen = [] #areas that have been seen, use this to avoid repetition
        
        self.unseen = []
        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row, col))
    
    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        # track all moves, prevent collisions
        orders = {}
        
        def do_move_direction(loc, direction):
            new_loc = ants.destination(loc, direction)
            
            if (ants.unoccupied(new_loc) and new_loc not in orders):
                
                ants.issue_order((loc, direction)) #only move if no one else is there
                orders[new_loc] = loc
                return True
            else:
                return False
				
	targets = {}
		
        def do_move_location(loc, dest): #move ants from here to there
            directions = ants.find_path(loc, dest)
            
            for direction in directions:
                if do_move_direction(loc, direction):
                    targets[dest] = loc
                    return True
            return False

        # prevent stepping on own hill
        for hill_loc in ants.my_hills():
            orders[hill_loc] = None

        # find close food
        ant_dist = []
        for food_loc in ants.food():
            for ant_loc in ants.my_ants():
                dist = ants.distance(ant_loc, food_loc)
                ant_dist.append((dist, ant_loc, food_loc))
        ant_dist.sort() #perform actions for the shortest distances first
        for dist, ant_loc, food_loc in ant_dist:
		
            if food_loc not in targets and ant_loc not in targets.values():
				#only retrieve food if no other ant is gathering it
				#and if the given ant is not doing anything else
                do_move_location(ant_loc, food_loc)

        # attack hills
        
        for hill_loc, hill_owner in ants.enemy_hills():
            if hill_loc not in self.hills:
                self.hills.append(hill_loc)
                
        ant_dist = []
        
        for hill_loc in self.hills:
            for ant_loc in ants.my_ants():
                if ant_loc not in orders.values():
                    
                    dist = ants.distance(ant_loc, hill_loc)
                    ant_dist.append((dist, ant_loc, hill_loc))

        ant_dist.sort()
        
        for dist, ant_loc, hill_loc in ant_dist:
            
            do_move_location(ant_loc, hill_loc)

        # explore unseen areas
        # bug: if there are too many things to explore for, they will circle around
        for loc in self.unseen[:]:
            if ants.visible(loc): 
                self.seen.append(loc)
                self.unseen.remove(loc)

            elif loc in self.seen: # try not to search areas you've already seen
                self.unseen.remove(loc)
                self.unseen.append(loc) #add to the end of the array
                
        for ant_loc in ants.my_ants():
            if ant_loc not in orders.values():
                
                unseen_dist = []
                
                for unseen_loc in self.unseen:
                    dist = ants.distance(ant_loc, unseen_loc)
                    unseen_dist.append((dist, unseen_loc))
                    
                unseen_dist.sort()
                
                for dist, unseen_loc in unseen_dist:
                    if do_move_location(ant_loc, unseen_loc):
                        break

        # unblock own hill
        for hill_loc in ants.my_hills():
            if hill_loc in ants.my_ants() and hill_loc not in orders.values():

                #try to get off the hill in any of the four directions by trying all possibilities
                for direction in ('s','e','w','n'):
                    if do_move_direction(hill_loc, direction):
                        break
				
            
if __name__ == '__main__':
    # psyco will speed up python a little, but is not needed
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        Ants.run(MyBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
