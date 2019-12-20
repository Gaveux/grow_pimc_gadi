#!/bin/python2
# ====================================
# the startpot module
# modified by Meredith Jordan March03
# ====================================


# load standard modules
import sys
import pickle
# load grow-specific modules
import setup
import state
import ab_initio
import util

# evaluate command line, create the state object
if len(sys.argv) == 3:
  if sys.argv[1].lower() == 'restart':
    fname = sys.argv[2] + '.state'
    f=util.check_for(fname)
    setup.banner()
    print ' Restarting from ' + '\"' + fname + '\"'
    s = pickle.load(f)
    s.Mode = 'startPOT'
  else:
    setup.banner() 
    s = state.GrowState()
    s.Mode ='startPOT'
    s.Stage = 'setup'
    setup.read_instructions(sys.argv[1],s)
    coordfile = sys.argv[2]
    s.Chosen = ab_initio.coords_from_logfile(coordfile,s)
    s.Pts2add = len(s.Chosen)
    if ( s.AI_Package == 'Gaussian16'):
      s.CoordUnit = 'angstrom'
    elif ( s.AI_Package == 'Gaussian09'):
      s.CoordUnit = 'angstrom'
    elif ( s.AI_Package == 'Gaussian03'):
      s.CoordUnit = 'angstrom'
    elif ( s.AI_Package == 'Gaussian98'):
      s.CoordUnit = 'angstrom'
    elif ( s.AI_Package == 'Molpro2002'):
      s.CoordUnit = 'angstrom'         # this might need changing at some point
    elif ( s.AI_Package == 'NWChem4.1'):
      s.CoordUnit = 'angstrom'         # as might this
    elif ( s.AI_Package == 'Aces2'):
      s.CoordUnit = 'bohr'
else:
  print '''
#  usage: startPOT <Grow2.2 input file> <coordinate file>
#       : startPOT restart Molecule
#''' 
  sys.exit(1)

#parsing user defined POT filename
#POTfilename = sys.argv[3]

# write a title line to the POT file
f=file(POTfilename,'w')
f.write('A data file for the PES of ' + s.Molecule + '\n')
f.close()

# write a title line to the cart_pot file
f=file('cart_pot','w')
f.write('A data file for the PES of ' + s.Molecule + '\n')
f.close()

# initiliase ab initio stuff, validate state, save state
ab_initio.do_setup(s)
s.validate()
s.dump()

# do an ab initio frequency at each geometry
# set flag, do calculation, add to POT
s.Stage = 'ab initio'
for i in range(s.PtsAdded,s.Pts2add):   # start loop at last point added
  if s.AI_DoCalc == 'true':             # if we died in add_to_POT, 
    ab_initio.do_calc(s)                #   don't redo ab initio calc 
    s.dump()                            # save state so restart works
  ab_initio.do_add_to_POT(s)  
  s.NumData+=1                          # Number of points in POT file ++
  s.PtsAdded+=1                         # increment local counter
  s.dump()                              # save current position in cycle 
 
