#!/usr/bin/python2
#============================================
# the setup module of the Grow2.2 package
# modified by Meredith Jordan March 03
#============================================
# read input files and assign global variables before starting the
# main loop of the Grow package

import os
import sys
import pickle
import string
import util
import state

#===========================================================
# all the different ways of starting the script...
#===========================================================
def command_line(argv):
  ' Decides what to do with the command line arguments to Grow '
  # restart an existing cycle
  if len(argv) == 3:
    if argv[1].lower() == 'restart':
      fname = argv[2] + '.state'
      f=util.check_for(fname)
      banner()
      print ' Restarting from ' + '\"' + fname + '\"'
      s = pickle.load(f)
      s.Mode = 'restart'
      s.svdtol = 0
      return s
    elif argv[1].lower() == '-nqs':
      banner()
      print ' Starting a new nqs run from ', argv[1]
      s = state.GrowState()
      s.Mode = 'nqs'
      s.Stage = 'setup'
      s.svdtol = 0
      read_instructions(argv[2],s)
      return s
    else:
      usage()
  elif len(argv) == 5:
    runset=False
    svdset=False
    if argv[1].lower() == 'restart':
      fname = argv[2] + '.state'
      f=util.check_for(fname)
      banner()
      print ' Restarting from ' + '\"' + fname + '\"'
      s = pickle.load(f)
      s.Mode = 'restart'
      runset=True
    elif argv[1].lower() == '-nqs':
      banner()
      print ' Starting a new nqs run from ', argv[1]
      s = state.GrowState()
      s.Mode = 'nqs'
      s.Stage = 'setup'
      read_instructions(argv[2],s)
      runset=True
    elif argv[1].lower() == 'svdtol':
      s.svdtol = int(argv[2])
      print ' Using svd cutoff ' + str(s.svdtol) + ' '
      svdset=True
    else:
      usage()
    if argv[3].lower() == 'svdtol':
      if (svdset):
        print 'svdtol has already been set'
        usage()
      s.svdtol = int(argv[4])
      print ' Using svd cutoff ' + str(s.svdtol) + ' '
      svdset=True
    elif argv[3].lower() == 'restart':
      fname = argv[4] + '.state'
      f=util.check_for(fname)
      banner()
      print ' Restarting from ' + '\"' + fname + '\"'
      s = pickle.load(f)
      s.Mode = 'restart'
      if (runset):
        print 'restart has already been set'
        usage()

    elif argv[3].lower() == '-nqs':
      banner()
      print ' Starting a new nqs run from ', argv[3]
      s = state.GrowState()
      s.Mode = 'nqs'
      s.Stage = 'setup'
      read_instructions(argv[4],s)
      if (runset):
        print 'restart has already been set'
        usage()
    else:
      usage()
    return s
  # begin a new Grow run
  # begin a new Grow run
  elif (len(argv) == 2):
    if argv[1].lower() == 'restart':
      usage()
    else:
      banner()
      print ' Starting a new run from ', argv[1]
      s = state.GrowState()
      s.svdtol=0
      s.Mode = 'new'
      s.Stage = 'setup'
      s.CoordUnit = 'bohr'
      read_instructions(argv[1],s)
      f=file('chooseHWt.inp','w')
      f.write('hwt\n\n')
      f.close()
      f=file('chooseRMS.inp','w')
      f.write('rms\n\n')
      f.close()
      f=file('pts2add.inp','w')
      f.write(str(s.Pts2add)+'\n')
      f.close()
      return s
  # exit with some help messages
  else:
    usage()

#====================
# usage message
#====================
def usage():
    print '''
  Usage: Grow2.2 <input file>
       : Grow2.2 restart Molecule

'''
    sys.exit(1)


#===========================================================
# assign ab initio package from command line possibilities
#===========================================================
def assign_ab_initio_package(z,s):
  if z == 'g09' or z == 'Gaussian09' or z == 'Gaussian' or z == 'gaussian':
    x = s._abprog[0]
  elif z == 'g16' or z == 'Gaussian16':
    x = s._abprog[1]
  elif z == 'g03' or z == 'Gaussian03':
    x = s._abprog[2]
  elif z == 'g98' or z == 'Gaussian98':
    x = s._abprog[3]
  elif z == 'Molpro' or z == 'MolPro' or z == 'MolPro2002' or z == 'molpro':
    x = s._abprog[4]
  elif z == 'nwchem' or z == 'NWChem' or z == 'NWChem4.1':
    x = s._abprog[5]
  elif z == 'aces2' or z == 'Aces2' or z == 'AcesII' or z == 'acesII':
    x = s._abprog[6]
  elif z == 'cfour' or z == 'CFour' or z == 'Cfour':
    x = s._abprog[7]

  return x

#=======================================
# how many data points in POT already?
#=======================================
def POT_count(s):
  'Function to count the number of data points in POT file'
  fc = util.grab_contents('POT',s)
  n=0
  for line in fc:
    if string.find(line,'data point') != -1:
      n+=1
  s.NumData = n
  print 'number of data points in the POT file:',s.NumData

#======================================
# read a file whose name is passed in
#======================================
def read_instructions(fname,s):
  ' reads the specified file in the current working directory '
  # try to read the file fname
  fc = util.grab_contents(fname,s)
  # now go through and find the keywords and their values
  s.Molecule   = snaffle_last(fc,'molecule name')
  s.MaxIter    = int(snaffle_last(fc,'maximum number of iterations'))
  s.CvgceChk   = int(snaffle_last(fc,'convergence check'))
  s.Dyn_Sample = string.lower(snaffle_last(fc,'sampling method'))
  s.Dyn_Cvgce  = string.lower(snaffle_last(fc,'convergence method'))
  s.rmsPts2add = int(snaffle_last(fc,'rms points to add'))
  s.hwtPts2add = int(snaffle_last(fc,'hwt points to add'))
  tmp_ai       = snaffle_last(fc,'ab initio package')
  s.AI_Package = assign_ab_initio_package(tmp_ai,s)
  s.AI_Charge  = int(snaffle_last(fc,'charge'))
  s.AI_Spin    = int(snaffle_last(fc,'spin'))
  s.AI_Scratch = snaffle_last(fc,'scratch directory')
  s.AI_Memory  = snaffle_last(fc,'memory')
  s.AI_Rwf     = snaffle_last(fc,'read-write')
  s.AI_NProc   = snaffle_last(fc,'number of processors')
  s.AI_JobType = snaffle_last(fc,'job type')
  if s.AI_JobType == 'simple':
    s.AI_Simple = snaffle_last(fc,'simple method')
    s.AI_Basis = snaffle_last(fc,'universal basis set')
    s.AI_Footers['simple'] = snaffle_verbatim(fc,'simple basis set','+++')
  elif s.AI_JobType == 'scaled':
    s.AI_Low   = snaffle_last(fc,'low correlation method')
    s.AI_High  = snaffle_last(fc,'high correlation method')
    s.AI_Footers['small'] = snaffle_verbatim(fc,'small basis set','+++')
    s.AI_Footers['large'] = snaffle_verbatim(fc,'large basis set','+++')
    s.AI_BasSmall = snaffle_last(fc,'universal basis - small')
    s.AI_BasLarge = snaffle_last(fc,'universal basis - large')
  s.Pts2add = 1

  print 'finished read instructions'

#=============================
# snaffling functions
#=============================
def snaffle_last(list,word):
  ' little subroutine to grab the last word on a line containing "word" in fc '
  value=''
  for line in list:
    if string.find(line,word) != -1:
      tmp = line.split()
      k = len(tmp)
      value = tmp[k-1]
      break
  if value == '':
    print 'Missing Parameter: "' + word + '" not found in input file \n'
    sys.exit(1)
  else:
    print word, value
    return value

#=============================
def snaffle_verbatim(list,word,delimeter):
  ' little subroutine to grab all the lines between word and delimeter '
  snaffled = ''
  for line in range(0,len(list)):
    if string.find(list[line],word) != -1:
      line+=1
      while string.find(list[line],delimeter) == -1:
        snaffled+=list[line]
        line+=1
      break
  if snaffled == '':
    print 'Missing Parameter: "' + word + '" not found in input file \n'
    sys.exit(1)
  else:
    print word,delimeter,snaffled
    return snaffled

#=================
# banner function
#=================
def banner():
  # print a banner
  print '\n\t\t============================================'
  print '\t\t|                                          |'
  print '\t\t|               Grow 2.2                   |'
  print '\t\t|                                          |'
  print '\t\t|      How do you take your tea?           |'
  print '\t\t|                                          |'
  print '\t\t============================================\n'

