#!/usr/bin/python2
#============================================
# the utils module of the Grow2.2 package
#============================================
#containing wrappers for various system calls

import sys
import os
import string

#=============================
# a universal controlled exit
#=============================
def DieError(name,reason,s):
  ' Function giving clean exits when terminal errors occur '
  print '\n*--> DieError during: ', s.Stage
  print '*-->', name, reason,'\n'
  print '\n'
  sys.exit(1)

#===================================================
# system call which monitors exit status of command
#===================================================
def Run(cmd,s):
  ' Function to run a unix command line and catch the exit status '
  status = os.system(cmd)
  if (status != 0):
    DieError('System call', '\"' + cmd + '\" failed ',s)

#=======================================================
# the common task of slurping in the contents of a file
#=======================================================
def grab_contents(file,s):
  'Returns the contents of file as a list, dies gracefully if the file does not exist'
  # test for existence of file
  f = check_for(file)
  fc = f.readlines()
  f.close()
  return fc

#===================================
# quietly removes the argument file
#===================================
def Rmf(file):
  'Local implementation of the unix "rm -f", ie, removes file without complaint'
  try:
    os.remove(file)
  except OSError:
    pass

#=============================
# check for existence of file
#=============================
def check_for(fname):
  try:
    f = open(fname,'r') 
  except:
    if os.path.exists(fname):
      print '\n IOError: While trying to open file \"' + fname + '\"\n'
    else:
      print '\n IOError: file \"' + fname + '\"  does not exist.\n'
      sys.exit(1)
  else:
      return f
 
#================================================
# swap atomic numbers for element symbols
#===============================================

elements = ['H','He','Li','Be', 'B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar']

def atomic_symbol(n):
  ' Give an atomic number return the atomic symbol '
  if n <= len(elements):
     return elements[n-1]
  else:
     print '''
  Error: Only first and second rows elements implemented 
       : Edit array "elements" in utilities.py
'''
     sys.exit(1)

#================================================
# grab atom labels from IN_SYSTEM 
#===============================================

def get_atom_labels(s):
  ' get atom labels from IN_SYSTEM '
  fc = grab_contents('IN_SYSTEM',s)
  lab = string.split(fc[4],',')
  # Remove newline character from the end of last label
  lab[len(lab)-1] = lab[len(lab)-1][0:-1]
  return lab

