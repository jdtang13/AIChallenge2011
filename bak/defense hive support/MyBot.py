#!/usr/bin/env python
from ants import *
from Intent import *

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
        self.directions = []

        self.seen = [] #areas that have been seen, use this to avoid repetition
        self.unseen = []
        self.stepped_on = {}

        self.intent = {}
        self.to_explore = []

        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row, col))
                self.intent[(row,col)] = Intent.GATHER
    
    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        # track all moves, prevent collisions
        orders = {}
        
        def do_move_direction(loc, direction):

            tempdir = direction
            
            if loc not in self.stepped_on:
                self.stepped_on[loc] = loc
            
            new_loc = ants.destination(loc, direction)
            
            row, col = loc
            new_row, new_col = new_loc

            dlist = ['n','s','w','e'] #WORKS! seemingly

            points = {}

            #this block seems to make it a bit stupider
            
            if (self.intent[loc] == Intent.EXPLORE or self.intent[loc] == Intent.CONQUER):
                #exploration/conquer handling...no moving backwards!
                pass
                    
            self.directions.append(tempdir)

            if ants.unoccupied(new_loc) and new_loc not in orders:
                
                ants.issue_order((loc, tempdir)) #only move if no one else is there
                orders[new_loc] = loc
                return True
            else:
                return False
				
	targets = {}
		
        def do_move_location(loc, dest): #move ants from here to there
            directions = ants.find_path(loc, dest, self.intent[loc], self.stepped_on, ants.my_hills())
            
            for direction in directions:
                if do_move_direction(loc, direction):
                    
                    targets[dest] = loc
                    return True
            return False

        def move_around(loc, dest): #get ants to cluster around
                #getting an "is not iterable" error
        
            possibles = []

            row, col = dest

            possibles.append((row+2,col))
            possibles.append((row-2,col))
            possibles.append((row,col+2))
            possibles.append((row,col-2))
            possibles.append((row+1,col+1))
            possibles.append((row-1,col+1))
            possibles.append((row+1,col-1))
            possibles.append((row-1,col-1))
            
##            possibles.append(ants.destination(dest, 'n'))
##            possibles.append(ants.destination(dest, 's'))
##            possibles.append(ants.destination(dest, 'w'))
##            possibles.append(ants.destination(dest, 'e'))

            ri = random.randint(0,7)

            do_move_location(loc,possibles[ri])
            

        # prevent stepping on own hill
        for hill_loc in ants.my_hills():
            orders[hill_loc] = None

        # find close food

        for ant_loc in ants.my_ants():
            if self.intent[ant_loc] == Intent.DEFEND:
                for hill_loc in ants.my_hills():
                    move_around(ant_loc,hill_loc)
        
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
                
                self.intent[ant_loc] = Intent.GATHER
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
            self.intent[ant_loc] = Intent.CONQUER
            do_move_location(ant_loc, hill_loc)

        #aggro!!!
        #do offensive stuff only if you have good numbers
##        attackers = 0
##        for intent in self.intent:
##            if intent == Intent.KILL:
##                attackers += 1
##                
##        if len(ants.my_ants()) > 3:
##
##            if attackers < 3*len(ants.enemy_ants()):
##                
##                ant_dist = []
##
##                #error: enemy_loc is seen as an integer, not tuple?
##                for enemy_loc in ants.enemy_ants():
##                    for ant_loc in ants.my_ants():
##                        if ant_loc not in orders.values():
##                            dist = ants.distance(ant_loc, enemy_loc)
##                            ant_dist.append( (5, ant_loc, enemy_loc) )
##
##                ant_dist.sort()
##
##                count = 0
##                for dist, ant_loc, enemy_loc in ant_dist: #ants closest to my enemies go
##                    count += 1
##                    
##                    self.intent[ant_loc] = Intent.KILL
##                    move_around(ant_loc, enemy_loc)
##                    
##                    if count >= 4:
##                        break

        #do defensive stuff only if you have good numbers
##        defenders = 0
##        for intent in self.intent:
##            if intent == Intent.DEFEND:
##                defenders += 1
##                
##        if len(ants.my_ants()) > 3:
##
##            if defenders < 4*len(ants.my_hills()):
##                
##                ant_dist = []
##
##                for hill_loc in ants.my_hills():
##                    for ant_loc in ants.my_ants():
##                        if ant_loc not in orders.values():
##                            dist = ants.distance(ant_loc, hill_loc)
##                            ant_dist.append((dist, ant_loc, hill_loc))
##
##                ant_dist.sort()
##
##                count = 0
##                for dist, ant_loc, hill_loc in ant_dist: #ants closest to my hills go
##                    count += 1
##                    
##                    self.intent[ant_loc] = Intent.DEFEND
##                    move_around(ant_loc, hill_loc)
##                    
##                    if count >= 4:
##                        break
        
        # explore unseen areas
        for loc in self.unseen[:]:
            if ants.visible(loc):
                self.seen.append(loc)
                self.unseen.remove(loc)

        for ant_loc in ants.my_ants():
            if ant_loc not in orders.values():

                for t in self.to_explore[:]:
                    if ant_loc == t:
                        self.to_explore.remove(t) #delete a location once you've touched it

                if len(self.to_explore)<4:
                    
                    unseen_dist = []

                    for unseen_loc in self.unseen:
                        dist = ants.distance(ant_loc, unseen_loc)
                        unseen_dist.append( (dist, unseen_loc) )
                        
                    unseen_dist.sort()
                    
                    for dist, unseen_loc in unseen_dist[:]:
                        if (len(self.to_explore)>4): #keep a running list of things to explore for
                            break
                        elif unseen_loc not in self.to_explore:
                            self.to_explore.append(unseen_loc)

                for t in self.to_explore: #move to the unexplored areas on the list
                    self.intent[ant_loc] = Intent.EXPLORE
                    if do_move_location(ant_loc, t):
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
