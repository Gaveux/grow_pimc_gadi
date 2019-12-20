#!/bin/python2
# ====================
# the startpot module
# ====================


# load standard modules
import sys
import pickle
# load grow-specific modules
import setup
import state
import ab_initio
import util
import string
import shutil

# evaluate command line, create the state object
if len(sys.argv) == 5:
  setup.banner() 
  s = state.GrowState()
  s.Mode ='startPOT'
  s.Stage = 'setup'
  setup.read_instructions(sys.argv[1],s)
  coordfile = sys.argv[2]
  checkpoint = sys.argv[3]
  derivs = sys.argv[4]
  s.Chosen = ab_initio.coords_from_logfile(coordfile,s)
  s.Pts2add = len(s.Chosen)
  if ( s.AI_Package == 'Gaussian16'):
    s.CoordUnit = 'angstrom'
  elif ( s.AI_Package == 'Gaussian09'):
    s.CoordUnit = 'angstrom'
  if ( s.AI_Package == 'Gaussian03'):
    s.CoordUnit = 'angstrom'
  if ( s.AI_Package == 'Gaussian98'):
    s.CoordUnit = 'angstrom'
  elif ( s.AI_Package == 'Molpro2002'):
    s.CoordUnit = 'angstrom'         # this might need changing at some point
  elif ( s.AI_Package == 'NWChem4.1'):
    s.CoordUnit = 'angstrom'         # as might this
  elif ( s.AI_Package == 'Aces2'):
    s.CoordUnit = 'bohr'
else:
  print '''
  usage: makePOT <Grow2.0 input> <gaussian logfile> <checkpoint file> <deriv file>
''' 
  sys.exit(1)

# cleanup some temporary files

util.Rmf('cdata_bohr')
util.Rmf('cdata1')

# write coordinates into file cdata1 and transform to bohr

f=open('cdata1','w')
f.writelines(s.Chosen[s.PtsAdded])
f.write('\n')
f.close()

util.Run('Ang2Bohr < cdata1 > cdata_bohr',s)

# now grab all the relevant results from frequency calculation:

# format the checkpoint file

# get the energy and derivative data from the formatted checkpoint file 

fc = util.grab_contents(checkpoint,s)
energy=''
natom=''
for line in range(0,len(fc)):
 if string.find(fc[line],'Total Energy') != -1:
   energy = fc[line].split()[3] + '\n'
for line in range(0,len(fc)):
 if string.find(fc[line],'Number of atoms') != -1:
   natom = fc[line].split()[4]
natom = int(natom)

# get the derivatives from the deriv file

fc = util.grab_contents(derivs,s)
grad=''
ForceConst=[]
freq=''
for line in range(natom,2*natom):
  grad += fc[line].split()[0] + '  ' + fc[line].split()[1] + '  ' + fc[line].split()[2] + '\n'
for line in range(2*natom,len(fc)):
  ForceConst += fc[line].split() 
while len(ForceConst) != 0:
  freq += '  ' + ForceConst.pop(0) + ' \n'

# get coordinate info from cdata_bohr
fc=util.grab_contents('cdata_bohr',s)
coord=''
for line in range(0,natom):
  coord += fc[line].split()[1] + '  ' + fc[line].split()[2] + '  ' + fc[line].split()[3] + '\n'

# write the derivative information to a file for bfinvert to read
dat=file('freq.dat','w')
dat.writelines(coord)
dat.writelines(energy)
dat.writelines(grad)
dat.writelines(freq)
dat.close()

if s.AI_JobType == 'simple':   
  shutil.copy2('freq.dat', s.Molecule + '.simple.dat')
elif s.AI_JobType == 'scaled':
  shutil.copy2('freq.dat','freq.small.dat')

# add data point to the POT file

ab_initio.do_add_to_POT(s)  

