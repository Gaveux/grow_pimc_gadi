#!/bin/python2
#===================================================
# the ab initio module of the Grow2.2 package
# modified by Meredith Jordan to include g03 March 2006
#===================================================
#
# Note that the choices in the do_blah() functions must match the entries
# in the list _abprog in the state.py module.  To add new packages just
# add another 'elif' block, emulating the existing code

import util
import g98
import g03
import g09
import g16
import molpro
import nwchem
import aces2
import cfour
import os

#===============================================================================
# called once at beginning of Grow2.2 run
#===============================================================================

def do_setup(s):
  ' Initialise things needed for ab initio calculations '
  print ' Setting up data structures for ab initio calculations '
  # perform program specific setup - build arrays used later to make com files
  print 'in do_setup ab initio package:', s.AI_Package

  if ( s.AI_Package == 'Gaussian16'):
    g16.setup(s)
  elif ( s.AI_Package == 'Gaussian09'):
    g09.setup(s)
  elif ( s.AI_Package == 'Gaussian03'):
    g03.setup(s)
  elif ( s.AI_Package == 'Gaussian98'):
    g98.setup(s)
  elif ( s.AI_Package == 'Molpro2002'):
    molpro.setup(s)
  elif ( s.AI_Package == 'NWChem4.1'):
    nwchem.setup(s)
  elif ( s.AI_Package == 'Aces2'):
    aces2.setup(s)
  elif ( s.AI_Package == 'CFour'):
    cfour.setup(s)
  else:
    # shouldn't be able to get here because s was validated in the grow.py
    util.DieError('ChoiceError',' ab initio package = ' + s.AI_Package,s)


#===============================================================================
# these two functions are called from inside the main loop in grow.py
#===============================================================================

def do_calc(s):
  ' function to prepare the chosen coordinates and call the appropriate \
    ab initio program to generate potential energy data'
  print ' Now running ab initio calculation ',s.PtsAdded+1,' of ',len(s.Chosen)
  # prepare the coordinates - shouldn't depend on the package
  setup_coords(s)
  # call the appropriate ab initio package
  if ( s.AI_Package == 'Gaussian16'):
    g16.calc(s)
  elif ( s.AI_Package == 'Gaussian09'):
    g09.calc(s)
  elif ( s.AI_Package == 'Gaussian03'):
    g03.calc(s)
  elif ( s.AI_Package == 'Gaussian98'):
    g98.calc(s)
  elif ( s.AI_Package == 'Molpro2002'):
    molpro.calc(s)
  elif ( s.AI_Package == 'NWChem4.1'):
    nwchem.calc(s)
  elif ( s.AI_Package == 'Aces2'):
    aces2.calc(s)
  elif ( s.AI_Package == 'CFour'):
    cfour.calc(s)
  else:
    # shouldn't be able to get here because s was validated in the grow.py
    util.DieError('ChoiceError:',' ab initio package = ' + s.AI_Package,s)
  # set the flag to false, so we don't do this again until we've done add_to_POT
  s.AI_DoCalc = 'false'

def do_add_to_POT(s):
  print ' Adding data point ',s.NumData+1
  # call the appropriate munging routine to process ab initio output
  if ( s.AI_Package == 'Gaussian16'):
    g16.add_to_POT(s)
  elif ( s.AI_Package == 'Gaussian09'):
    g09.add_to_POT(s)
  elif ( s.AI_Package == 'Gaussian03'):
    g03.add_to_POT(s)
  elif ( s.AI_Package == 'Gaussian98'):
    g98.add_to_POT(s)
  elif ( s.AI_Package == 'Molpro2002'):
    molpro.add_to_POT(s)
  elif ( s.AI_Package == 'NWChem4.1'):
    nwchem.add_to_POT(s)
  elif ( s.AI_Package == 'Aces2'):
    aces2.add_to_POT(s)
  elif ( s.AI_Package == 'CFour'):
    cfour.add_to_POT(s)
  else:
    # shouldn't be able to get here because s was validated in the grow.py
    util.DieError('ChoiceError:',' ab initio package = ' + s.AI_Package,s)
  # set the flag to true, so the next time through the main loop
  # in grow.py, do_calc() will be called
  s.AI_DoCalc = 'true'
  print ''


#=========================================================================
# package independent functions
#=========================================================================

# the coordinates don't depend on which program uses them
# this function comes here rather than in the dynamics module to make it
# easier to keep track of errors by treating each point to be added
# separately.  possibly overkill but a boon to debugging

def setup_coords(s):
  ' Takes currently selected geometry in bohr and prepares it for inlusion in an ab initio input file'
  print '    setup_coords'
  #print '    chosen geometries from COUT copied into file cdata2'
  # cleanup some temporary files
  util.Rmf('cdata_bohr')
  util.Rmf('cdata_ang')
  util.Rmf('cdata2')
  #util.Rmf('rub')
  util.Rmf('CARTVECS')
  # write out the coordinates chosen by choose
  # Needed to change cdata2 to cdata1 for rotranz after commenting out buckle
  f=open('cdata2','w')
  f.writelines(s.Chosen[s.PtsAdded])
  f.write('\n')
  f.close()
  #print '   chosen geometry in Bohr:'
  #os.system("cat cdata2")
  #print ' '
  #we will attempt to grow the system without using buckle.  The exclusion of small singular values shall overcome
  #the issues that buckle attempts to overcome
  #make sure the geometries aren't flat and are in standard orientation
  #util.Run('buckle < cdata1 > cdata2',s)
  if s.CoordUnit == 'bohr':
    util.Run('rotranz < cdata2 > cdata_bohr',s)
    util.Run('Bohr2Ang < cdata_bohr > cdata_ang',s)
  elif s.CoordUnit == 'angstrom':
    util.Run('rotranz < cdata2 > cdata_ang',s)
    util.Run('Ang2Bohr < cdata_ang > cdata_bohr',s)
  else:
    util.DieError('Units:','CoordUnit must be one of "angstroms" or "bohr"',s)
  #util.Run('makevecs < cdata_bohr > rub',s)  # makevecs produces CARTVECS file


#=========================================================================
# utility functions
#=========================================================================

def coords_from_logfile(file,s):
  ' pipes through to the package-specific function '
  coords=[]
  # switch on ab initio package
  if ( s.AI_Package == 'Gaussian16'):
    coords = g16.coords_from_logfile(file,s)
  elif ( s.AI_Package == 'Gaussian09'):
    coords = g09.coords_from_logfile(file,s)
  elif ( s.AI_Package == 'Gaussian03'):
    coords = g03.coords_from_logfile(file,s)
  elif ( s.AI_Package == 'Gaussian98'):
    coords = g98.coords_from_logfile(file,s)
  elif ( s.AI_Package == 'Molpro2002'):
    coords = molpro.coords_from_logfile(file,s)
  elif ( s.AI_Package == 'NWChem4.1'):
    coords = nwchem.coords_from_logfile(file,s)
  elif ( s.AI_Package == 'Aces2'):
    coords = aces2.coords_from_logfile(file,s)
  else:
    # shouldn't be able to get here because s was validated in the grow.py
    util.DieError('ChoiceError:',' ab initio package = ' + s.AI_Package,s)

  return coords


