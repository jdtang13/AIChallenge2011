from ants import *
from Intent import *

#   debugging to remove later
import logging
import os
#os.remove('C:/Users/Amy/Documents/aichallenge/ants.log')

logging.basicConfig(filename='ants.log', level=logging.DEBUG)

import sys
from optparse import OptionParser
from logutils import initLogging,getLogger
#   end debugging

turn_number = 0
bot_version = 'v0.1'

getLogger().debug("------")

def emit(self,record):
  msg = self.format(record)
  fs = "%s" if getattr(record, "continued", False) else "%s\n"
  self.stream.write(fs % msg)
  self.flush()

logging.StreamHandler.emit = emit #Stuff to suppress newline
continued = dict(continued = True)

logging.error("Testing...",extra=continued); logging.error(" Done")

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

        self.diffuse = {}
        self.intent = {}

        self.last_seen = {}

##        self.waters = set() #use a set to make it faster

        self.food_value = 12000
        self.water_value = -1000
        self.hill_value = 20000
        self.unseen_value = 1000

##        self.lc = {} #center of mass for a location
##        self.i = {} #number of iterations for an ant

        #self.com_all_ants = {} #center of mass of all ants
        self.com_all_ants = (0.0, 0.0)

        #getLogger().debug("map setup: ")

        for row in range(ants.rows):
            for col in range(ants.cols):
              
              loc = (row,col)

##              self.lc[(row,col)] = (-1.0,-1.0) #set up center of mass
##              self.i[(row,col)] = -1

              #getLogger().debug("(%d,%d) map value is %d ", row, col, ants.map[row][col] )
              
##              if (not ants.passable((row,col))):
##                self.waters.append(loc)
##                getLogger().debug("added to waters %d,%d ", row, col)

              self.last_seen[loc] = 0
              self.diffuse[loc] = self.unseen_value
            
##              if ((row,col) in ants.food() ): #this can be optimized
##                self.diffuse[(row,col)] = 16000
##              elif (not ants.passable((row,col)) ):
##                self.diffuse[(row,col)] = 0
##                
##              elif ((row,col) in self.hills):
##                self.diffuse[(row,col)] = 10000
##
##              else:
##                self.diffuse[(row,col)] = 0
##
##              if ((row,col) in self.unseen):
##                self.diffuse[(row,col)] += 1000

                #getLogger().debug("%d", self.diffuse[(row,col)])
    
    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        global turn_number
        turn_number = turn_number+1
        getLogger().debug("----- Starting Turn %d", turn_number)
      
        orders = {}

        def calc_update_com():
          row_com = 0.0
          col_com = 0.0
          
          for (row,col) in ants.my_ants():
            row_com += row
            col_com += col

          row_com /= len(ants.my_ants())
          col_com /= len(ants.my_ants())

          if turn_number <= 1:
            self.com_all_ants = (row_com, col_com)
          else:
            k = 2
            row_prev, col_prev = self.com_all_ants
            row_temp = (row_prev + row*(k-1))/k # k^i weighted average
            col_temp = (col_prev + col*(k-1))/k
            self.com_all_ants = (row_temp, col_temp)

          return self.com_all_ants

        def do_com_diffuse(ant_loc, my_dir, com):
          row_prev, col_prev = ant_loc
          row_com, col_com = com

          dist_prev = ants.distance(ant_loc,com)

          dlist = ['n','e','s','w']

          dist_list = []

          for d in dlist:
            dist_list.append( (ants.distance(com, ants.destination(ant_loc, d)), d) )

          dist_list.sort()
          dist_list.reverse()

          for (dist, direction) in dist_list:

            if dist > dist_prev:
##              getLogger().debug("%d is diffuse value before", self.diffuse[ants.destination(ant_loc,direction)])
              self.diffuse[ants.destination(ant_loc,direction)] += 0#self.food_value/10000
##              getLogger().debug("added! %d is now diffuse value", self.diffuse[ants.destination(ant_loc,direction)])

              if len(ants.food()) == 0:
                self.diffuse[ants.destination(ant_loc,direction)] += self.food_value

              break
              
##              if do_move_direction(ant_loc, direction):
##                bool_tmp = True
##                break
            
        def do_move_direction(loc, direction):

            tempdir = direction
            
            if loc not in self.stepped_on:
                self.stepped_on.append(loc)

            new_loc = ants.destination(loc, direction)
            
            row, col = loc
            new_row, new_col = new_loc

            dlist = ['n','s','w','e']
            points = {}
            
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

        #collaborative diffusion attempt

        def diffuse((row,col)):

          def score(value,decay,my_loc,goal_loc):
            goal_row, goal_col = goal_loc
            my_row, my_col = my_loc
            
            dist = abs(goal_row-my_row) + abs(goal_col-my_col)
            score = value - (.5*value/decay)*(dist)

            if value>0:
              if score <0:
                score =0

            else:
              if score > 0:
                score = 0
                
            return score

          self.diffuse[(row,col)] = 0
        
          loc = row,col

          food_value = self.food_value
          food_decay = 5
          
          water_value = self.water_value
          water_decay = 1
          
          hill_value = self.hill_value
          hill_decay = 6

          if not ants.visible((row,col)):
            self.diffuse[(row,col)] += self.unseen_value * self.last_seen[(row,col)]

          else:

            for (food_row, food_col) in ants.food():
              dist = abs(food_row-row) + abs(food_col - col)
              self.diffuse[loc] += food_value/(dist+1)              
              #self.diffuse[loc] += score(food_value,food_decay,(row,col),(food_row,food_col))

            for (water_row, water_col) in ants.water():
              #getLogger().debug("diffusing waters")
              
              dist = abs(water_row-row) + abs(water_col - col)
              self.diffuse[loc] += water_value/(dist+1)
              
              #self.diffuse[loc] += score(water_value,water_decay,(row,col),(water_row,water_col))
              
            for (hill_row, hill_col) in self.hills:
              dist = abs(hill_row-row) + abs(hill_col - col)
              self.diffuse[loc] += hill_value/(dist+1)

            #defensive action
            for enemy_ant_loc, enemy_owner in ants.enemy_ants():
              
              dist_arr = []

##              row_tmp,col_tmp = enemy_ant_loc
##              getLogger().debug("enemy_ant_loc is %d,%d ", row_tmp, col_tmp)
##              
              for hill_loc in ants.my_hills():
             
                dist_arr.append( (ants.distance(hill_loc, enemy_ant_loc), hill_loc) )
                

              dist_arr.sort()
              (d, h) = dist_arr[0]

              self.diffuse[h] += (food_value)/(d+1) #the closer an enemy ant gets, the more you want to defend
              
            #self.diffuse[(row,col)] += unseen_value*self.last_seen[(row,col)]

        # record hills
        for hill_loc, hill_owner in ants.enemy_hills():
            if hill_loc not in self.hills:
                self.hills.append(hill_loc)
        
        for row in range(ants.rows):
          for col in range(ants.cols):

            if not ants.visible((row,col)):
              self.last_seen[(row,col)] += 1
              #getLogger().debug("Last seen %d,%d  at %d", row, col, self.last_seen[(row,col)] )
            else:
              self.last_seen[(row,col)] = 0

            diffuse((row,col)) #diffuse only if visible
            
            s = ", "

            if col >= ants.cols-1:
              s = ""
            
            msg = `self.diffuse[(row,col)]`+s

## logging error line
            #logging.error(msg,extra=continued)

          #logging.error("")

        calc_update_com()
        
        for ant_loc in ants.my_ants(): #try to take spots with the highest value
            if ant_loc not in orders.values():
            
              dlist = ['n','e','s','w']
              loc_list = []


              for d in dlist:
                do_com_diffuse(ant_loc, d, self.com_all_ants)
                neighbor_loc = ants.destination(ant_loc, d)
                
                value = self.diffuse[neighbor_loc]
                loc_list.append( (value,d) )
              
              loc_list.sort()
              loc_list.reverse()

              for (value,d) in loc_list:

                if do_move_direction(ant_loc,d):
                  break


                
        # unblock own hill
##        for hill_loc in ants.my_hills():
##            if hill_loc in ants.my_ants() and hill_loc not in orders.values():
##
##                #try to get off the hill in any of the four directions by trying all possibilities
##                for direction in ('s','e','w','n'):
##                    if do_move_direction(hill_loc, direction):
##                        break
				
            
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
