from datetime import timedelta
from dateutil import parser
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import json



# returns the value put in by the user (if its a 0 or a 1)
# else it runs again
# used for defining some variables in ratestart()
def yorn(string):
  var = input(string)
  if var == '0' or var == '1':
    return int(var)
  else:
    print('I NEED A BOOLEAN! 1 for true, 0 for false.')
    yorn(string)
    
   
   
# returns the value put in by the user (if its an integer)
# else it runs again
# used for defining some integer variables
def numbertry(string):
  
  var = input(string)
  
  # defaults to 20
  if var == '':
    print('Argument defaulted to 20.')
    return 20
  
  try: return int(var)
  except:
    print("Hey, that's not an integer!")
    numbertry(string)



# just closes the program in a nice way
# not really necessary
def bye():
  input('See you later! Press Enter to exit.')
  exit()

      


# gets the n timestamps with the highest/lowest value in the column
def first(column, number, orientation):
  
  
  # flips the data around if the user requested the lowest values
  # else it does nothing
  orienteddf = data[column] * orientation
  
  
  # i still dont know how this works,
  # but it calculates all the local peaks that are at least 10 seconds from one another.
  # i use this instead of just choosing the 10 highest values so that it doesnt pick multiple
  # timestamps that are basically part of the same moment
  peaks, _ = find_peaks(orienteddf, distance=10)
  
  # sorts the peaks from highest to lowest
  peaksdf = pd.DataFrame((orienteddf).iloc[peaks]) \
            .sort_values(by = column, ascending = 0)
  
  # creates an empty list, and fills it with the n highest peaks
  peakslist = []
  for i in range (0, number):
    
    try:
      # grabs ith item in peakslist and
      # removes the '0 days' string if its there (cause its super ugly)
      timestamp = str(peaksdf.index[i])
      if timestamp.startswith('0 days '):
        timestamp = timestamp.replace('0 days ', '')
      
      # appends string to the list, alongside score corresponding to said timestamp
      peakslist.append(str(i + 1) + '. ' + timestamp + \
                    ' (' + str(int(orientation * peaksdf.iloc[i, 0])) + ')')
    except:
      # if it cant find the ith item (because it has already reached the end of the list),
      # it ends the loop early and prints out that the list had to be cut short
      print('(There were only ' + str(len(peakslist)) + ' moments available, ' + \
      'so we had to cut the list short)')
      break
  
  # this is pretty self explanatory i think (i hope i dont come back to this code
  # a year later and regret what i just said lol)
  print('Here is your list for ' + column + ':\n' + '\n'.join(peakslist))



# takes in user inputs for the first() command
def firststart(orientation):
  
  columnlist = list(data)
  columnlist.remove('#files')
  columnlist.remove('#start_times')
  
  print('The following columns are available: ' + '; '.join(columnlist))
  column = input('Enter the column you want to sort: ')
  
  # checks if column is in data
  if not column in list(data) or column.startswith('#'):
    print("That column doesn't exist!")
    firststart(orientation)
  
  else:
    number = numbertry('Enter the number of items you want: ')
    first(column, number, orientation)
  


# defines top() and bottom()
def top():
  firststart(1)

def bottom():
  firststart(-1)

  

# finds words in a line
def find(words, line, exact, capsens):

  # depending on the values of exact and capsens,
  # returns 1 if one of the words is in the message,
  # returns 0 otherwise
  for word in words:
    
    if exact == False and capsens == False:
      if word.lower() in line[23:].lower().strip():
        return 1

    elif exact == False and capsens == True:
      if word in line[23:].strip():
        return 1

    elif exact == True and capsens == False:
      if word.lower() == line[23:].lower().strip():
        return 1

    elif exact == True and capsens == True:
      if word == line[23:].strip():
        return 1

  return 0



# creates a new column with the specified words and requirements
def rate(name, plusword, minusword, exact, capsens, interval):
  

  print('Starting ' + name + '...')
  
 
  # creates empty dict to store all timestamps with messages
  maindata = {}
  
  
  for file in filelist:

    day = timedelta(days = filelist.index(file) + 1)
    
    t_start = parser.parse(data.iloc[filelist.index(file), 1])

    with open('logs/' + file + '.log', encoding = 'utf-8') as f:
      content = f.readlines()
      for line in content:
          
        # if the timestamp is not in maindata, set the score of the timestamp
        # to be the score of the message (score of plusword - score of minusword)
        if not parser.parse(line[1:20]) - t_start + day in maindata:
          maindata[parser.parse(line[1:20]) - t_start + day] \
          = find(plusword, line, exact, capsens) - \
          find(minusword, line, exact, capsens)
            
        # if the timestamp is in maindata, add the score of the message
        # to the score of the timestamp  
        else:
          maindata[parser.parse(line[1:20]) - t_start + day] \
          += find(plusword, line, exact, capsens) - \
          find(minusword, line, exact, capsens)
    
    print(file + ' ready!')


  # maps all key/value pairs from maindata onto a temporary column
  data['#main'] = pd.Series(maindata)
  
  
  # i dont know how this works,
  # but it does a forward rolling sum for the next n seconds
  # and maps that as the actual column we want
  window = pd.api.indexers.FixedForwardWindowIndexer(window_size=interval)
  data[name] = data['#main'].rolling(window=window, min_periods=1).sum()

  #deletes the temporary column
  del data['#main']
  
  #replaces all NaN values with 0 (idk if its useful but it looks nicer imo)
  data[name].fillna(0, inplace=True)
  
  #saves data (with the new column) to csv
  data.to_csv(datafile)

  print(name + ' all done!')
    


# takes in user inputs for the rate() command
def ratestart():

  # this function checks whether the name is valid
  # you cant use names that start with # because they are used for other things
  def nametry():
    var = input('Enter a NAME value: ')
    if var in list(data):
      print('That name is already used!')
      nametry()
    elif var.startswith('#'):
      print("You can't use names that start with a '#' symbol. Sorry about that.")
      nametry()
    else: return var
  
  name = nametry()

  # these are just the other inputs
  plusword = input('Enter a PLUSWORD list: ').split('; ')

  minusword = input('Enter a MINUSWORD list: ').split('; ')

  exact = yorn('Enter a boolean for EXACT: ')

  capsens = yorn('Enter a boolean for CAP-SENSITIVE: ')

  interval = numbertry('Enter an INTERVAL value: ')
  
  # removes empty strings if you havent actually written anything
  
  if plusword == ['']:
    plusword = []
  if minusword == ['']:
    minusword = []

  #runs the rate() command with the specified inputs
  rate(name, plusword, minusword, exact, capsens, interval)




# list of commands that the user can input,
# maps them to their corresponding command
commandlist = {
  'rate': ratestart,
  'top': top,
  'bottom': bottom,
  'bye': bye
}



# this is the main screen you see
def menu():
  
  command = input('\nEnter a command: ')
  
  # checks if user input is a valid command (tries to run the value associated
  # with the key from commandlist as a function)
  try: commandlist[command.lower()]()
  except KeyError:
    print("I don't think that's a valid command.")



# this is for running defaults (stored in the defaults.json file)
def rundefs():
  
  #tries loading defaults from the file, errors out if it cant find the file
  try:
    with open('defaults.json') as file:
      defaults = json.load(file)
  except:
    return print("The defaults.json file could not be found. DEFAULTS halted.")

  # this is like commandlist but for bitrate to check when it needs to run defaults
  deflist = {
  'rate': rate,
  'first': first,
  'bye': bye
  }
  
  print('Ok, starting defaults!')
  
  # for each list in defaults.json
  for elem in defaults:
    
    # if the list contains a single element, it runs it as a function with no arguments
    if len(elem) == 1: deflist[elem[0]]()
    
    # if the list contains more than one element, it runs the first element as a function,
    # and the rest as arguments
    else: deflist[elem[0]](*elem[1:])




def timestamps():
  global data

  startlist = []
      
  timestamps = pd.Index([])
      
  for file in filelist:
        
    with open('logs/' + file + '.log', encoding = 'utf-8') as f:
      t_start = f.readline()[1:20]
      startlist.append(t_start)
      
      content = f.readlines()
      for line in content:
        last_line = line
          
    t_end = parser.parse(last_line[1:20])
        
    days = str(filelist.index(file) + 1) + ' days'
        
    daystamps = pd.timedelta_range(
      start = days + " 00:00:00",
      end = days + ' ' + str(t_end - parser.parse(t_start)), freq='S')
        
    timestamps = timestamps.union(daystamps)
      
  data = pd.DataFrame(index=timestamps)
  
  data['#files'] = np.nan
  data['#start_times'] = np.nan
  
  s = pd.Series(filelist)
  s.index = data.index[:len(s)]
  data.loc[:,'#files'] = s

  s = pd.Series(startlist)
  s.index = data.index[:len(s)]
  data.loc[:,'#start_times'] = s
  
  data.to_csv(datafile)



def start():
  global filelist, datafile, data, defaults
    
  where = input('Enter whether you will run on OLD or NEW data: ')

  if where.lower() == 'old':
        
    csvname = input('Enter the .csv file you are going to work with: ')
    datafile = 'data/' + csvname + '.csv'
    
    try:
      data = pd.read_csv(datafile, index_col=0, dtype={'#files': str})
      
      # this converts the index values to timedelta values
      data.index = pd.to_timedelta(data.index)
      
      filelist = [x for x in data['#files'].tolist() if pd.isnull(x) == False]
      
      print('Great! ' + csvname + ' it is.')
      
      print('(Remember you can always press Ctrl+C to return to this menu)')
    
    except:
      print("Couldn't find that .csv file! Returning to start...")
      start()
    
    
  elif where.lower() == 'new':
    
    filenames = input('Enter the list of .log files you are going to work with: ')
  
    filelist = filenames.split('; ')
    
    try:
      for file in filelist:
        with open('logs/' + file + '.log') as f:
          pass
    
    except:
      print('At least one of the files is not valid! Returning to start...')
      start()
    
    else:
      
      print('Creating the corresponding .csv file...')
      datafile = 'data/' + filelist[0] + '-' + filelist[-1] + '.csv'
      timestamps()
      
      defs = input('Would you like to run DEFAULTS? (Y/N): ')
      if defs.lower() == 'y':
        rundefs()

      print('(Remember you can always press Ctrl+C to return to this menu)')
        
         
  else:
    print("That's neither OLD nor NEW!")
    start()




# says hello, then runs the start screen
print('\nHullo! Welcome to BitRate!')
start()

# runs menu every time there is no other command actively running
# if it detects keyboard interrupt (ctrl+c), it halts whatever command it was running
# and returns to the menu
while True:
  try: menu()
  except KeyboardInterrupt:
    print('\nReturning to menu...')
    continue