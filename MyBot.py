#!/usr/bin/env python
from ants import *
from Intent import *

from random import shuffle
import logging

import os
os.remove('C:\Users\Amy\Documents\aichallenge\ants.log')

logging.basicConfig(filename='ants.log', level=logging.DEBUG)

import sys
from optparse import OptionParser
from logutils import initLogging,getLogger

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us

turn_number = 0
bot_version = 'v0.1'

getLogger().debug("------")

class LogFilter(logging.Filter):
  """
  This is a filter that injects stuff like TurnNumber into the log
  """
  def filter(self,record):
    global turn_number,bot_version
    record.turn_number = turn_number
    record.version = bot_version
    return True

class MyBot:
    def __init__(self):
        
        # define class level variables, will be remembered between turns
        pass
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        """Add our log filter so that botversion and turn number are output correctly"""        
        log_filter  = LogFilter()
        getLogger().addFilter(log_filter)

        self.hills = []
        self.directions = []

        self.seen = [] #areas that have been seen, use this to avoid repetition
        self.unseen = []
        self.stepped_on = []

        self.intent = {}
        self.lc = {} #center of mass for a location
        self.i = {} #number of iterations for an ant

        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row, col))
                self.intent[(row,col)] = Intent.GATHER

                self.lc[(row,col)] = (-1.0,-1.0) #set up center of mass
                self.i[(row,col)] = -1
    
    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        global turn_number
        turn_number = turn_number+1
        
        getLogger().debug(" ------ Starting Turn %d",turn_number)
        
        # track all moves, prevent collisions
        orders = {}

        for ant_loc in ants.my_ants():
            if self.lc[ant_loc] == (-1.0,-1.0):
                self.lc[ant_loc] = ant_loc #set up center of mass
            if self.i[ant_loc] == -1:
                self.i[ant_loc] = 0
        
        def do_move_direction(loc, direction):

##            hill_loc_cm_r = 0.0
##            hill_loc_cm_c = 0.0
##            num_hils = 0
##            for hill_loc_tmp in ants.my_hills():
##                hill_row_tmp, hill_col_tmp = hill_loc_tmp
##                hill_loc_cm_r += hill_row_tmp
##                hill_loc_cm_c += hill_col_tmp
##                num_hils += 1
##
##            hill_loc_cm_r = hill_loc_cm_r / num_hils
##            hill_loc_cm_c = hill_loc_cm_c / num_hils
            
##            getLogger().debug("Trying to move in %s",direction)
            
            if loc not in self.stepped_on:
                self.stepped_on.append(loc)

##            new_loc = ants.destination(loc, direction)
            
            row, col = loc
##            new_row, new_col = new_loc
            
            dlist = ['n','s','w','e']
            dlist.remove(direction)
            dlist.insert(0, direction) #direction you were trying to go to is first priority
            
            for d in dlist[:]:
                if not ants.passable(ants.destination(loc, d)):
                    dlist.remove(d)

            if len(dlist) == 0:
                dlist.append(ants.randlist(['n','s','w','e']))
                
            tempdir = dlist[0] #default direction to try
    
            for ant_loc in ants.my_ants():

                row_1, col_1 = ant_loc

                getLogger().debug("Focusing on ant [%d,%d]",row_1, col_1)

                if (self.intent[ant_loc] != Intent.EXPLORE):
                    break
                
                rib, cib = self.lc[ant_loc] #note: distinction between ci-bar and ci
                di_1 = float (abs(row_1 - rib) + abs(col_1 - cib)) #di at i-1
  
                for d in dlist:
                    row, col = ants.destination(ant_loc, d) #test all four directions

                    if self.i[ant_loc] < 0:
                        rib = row_1
                        cib = col_1
                  
                    if self.i[ant_loc] > 0:
                        new_rib = float(((self.i[ant_loc])*rib + 10*row)/(self.i[ant_loc] + 10))
                        new_cib = float(((self.i[ant_loc])*cib + 10*col)/(self.i[ant_loc] + 10)) #update the ci's and ri's

##                        new_rib = float((rib + 0.5*row)/(1 + 0.5))
##                        new_cib = float((cib + 0.5*col)/(1 + 0.5)) #update the ci's and ri's
                        
                    else:
                        new_rib = row
                        new_cib = col
                        
                    di =  float(abs(row - new_rib) + abs(col - new_cib)) #di at i

                    getLogger().debug("d %s, self.i %d, row_1 %d, row %d, rib %2f, new_rib %.2f", d, self.i[ant_loc], row_1, row, rib, new_rib)
                    getLogger().debug("d %s, self.i %d, col_1 %d, col %d, cib %2f, new_cib %2f, di %2f, di_1 %2f", d, self.i[ant_loc], col_1, col, cib, new_cib, di, di_1)

                    tempdir = d #TODO: double check all this

                    if di >= di_1 - 0.1: # if this is true, go this way!
                        tempdir = d #TODO: double check all this
                        break
                
##                        new_loc_tmp = ants.destination(loc, tempdir)    # don't go if you run into water later         
##                        if ants.passable(ants.destination(new_loc_tmp, tempdir)):
##                            break
                    
                    
##                    else:
##                        if (row_1 == row) or (col_1 == col):       
##                            tempdir = d #TODO: double check all this
##                            break
                    else:
                        tempdir = ants.randlist(dlist)
                    
##                        new_loc_tmp = ants.destination(loc, tempdir)             
##                        if ants.passable(ants.destination(new_loc_tmp, tempdir)):
##                            break

##                getLogger().debug("self.i %d, row_1 %, row %d, rib %d, cib %d, di %d, di_1 %d", self.i[ant_loc], row_1, row, rib, cib, di, di_1)    

            self.directions.append(tempdir)
            new_loc = ants.destination(loc, tempdir)

            if (self.intent[ant_loc] == Intent.EXPLORE):
                
                self.lc[new_loc] = new_rib, new_cib
                self.i[new_loc] = self.i[ant_loc] + 1

                self.lc[ant_loc] = (-1.0, -1.0)
                self.i[ant_loc] = -1
            
            getLogger().debug("Trying to move in %s",direction)
            getLogger().debug("Actually moving in %s",tempdir)

            self.intent[ant_loc] = Intent.GATHER

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
##            possibles.append((row+1,col+1))
##            possibles.append((row-1,col+1))
##            possibles.append((row+1,col-1))
##            possibles.append((row-1,col-1))

            ri = random.randint(0,3)

            do_move_location(loc,possibles[ri])

        # prevent stepping on own hill
        for hill_loc in ants.my_hills():
            orders[hill_loc] = None

        # find close food

        for ant_loc in ants.my_ants():
            if self.intent[ant_loc] == Intent.DEFEND:
                for hill_loc in ants.my_hills():
                    c,r = ant_loc
                    getLogger().debug("Defending Hill with %d,%d",c,r)
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
##        count = 0
##        enemy_loc = ants.closest_enemy_ant(ant_loc, None)
##        if enemy_loc != None:
##            for ant_loc in ants.my_ants(): #ants closest to my enemies go
##                if ant_loc not in orders.values():
##                    count += 1
##
##                if enemy_loc == None:
##                    continue
##                else:
##                    self.intent[ant_loc] = Intent.KILL
##                    
##                    if count == 1:
##                        do_move_location(ant_loc, enemy_loc)
##                    else:
##                        move_around(ant_loc, enemy_loc)
##                    
##                if count >= 10:
##                    break

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
        # TODO: FIX THIS. Have them continuously go in random directions and then turn around if they bump into something

        for loc in self.unseen[:]:
            if ants.visible(loc):
                self.seen.append(loc)
                self.unseen.remove(loc)
                
        for ant_loc in ants.my_ants():
            if ant_loc not in orders.values():
                
                unseen_dist = []
                for unseen_loc in self.unseen:
                    
                    dist = ants.distance(ant_loc, unseen_loc)
                    unseen_dist.append((dist, unseen_loc))
                    
                unseen_dist.sort()

                self.intent[ant_loc] = Intent.EXPLORE
                
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
