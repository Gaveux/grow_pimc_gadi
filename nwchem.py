#!/bin/python2
# gaussian98 module - all the functions to sort through gaussian98 output

# NOTE - the functions all assume the state object has been passed to them as s

import util

def setup(s,i):
  ' Function to setup the coordinate files for a gaussian calculation '
  print '    g98_setup'
	# cleanup some temporary files
  util.Run('rm -f cdata*',s)
  util.Run('rm -f rub',s)
  util.Run('rm -f CARTVECS',s)
	# write out the coordinates chosen by choose
  f=open('cdata1','w')
  f.write(s.Chosen[i])
  f.close
	# make sure the geometries aren't flat and are in standard orientation
  util.Run('buckle < cdata1 > cdata2',s)
  util.Run('rotranz < cdata2 > cdata',s)
  util.Run('Bohr2Ang < cdata > cartSet',s)
  util.Run('makevecs < cdata > rub',s)


def calc(s):
	' Function to run a gaussian calculation '
	print '    g98_calc'
	# build the first com file, which is indexed as the zero'th
	build_comfile(s,0)

def add_to_POT(s):
  ' Function to strip output from gaussian calculation and add it to the POT file '
  print '   do_g98_add'

def build_comfile(s,i):
	' Function to build the ith gaussian com file '
	# build the command string which makes the input file
	command = ' cat ' + s.AI_Headers[i] + ' cdata ' 
	# if there is a footer for the gaussiam .com file, add it 
	if (len(s.AI_Footers) >= i+1):
		command += s.AI_Footers[i]
	elif (len(s.AI_Footers) == 1):
		command += s.AI_Footers[0]
	# add the target to the command string
	command += ' > ' + s.Molecule + '.com'
	# execute the command
	util.Run(command,s)
