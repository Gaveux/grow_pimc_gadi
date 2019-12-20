#!/usr/bin/python2
#===================================
#                                  #
#            Grow 2.2              #
#                                  #
#=================================== 
#
# This is the main body of the Grow package as re-written in Python
# by Keiran Thompson in February 2003
# Updated for distribution edition by Deb Crittenden in March 2005
# Updated for g03 by Meredith Jordan March 2006                      
# Updated for cfour by Deb Crittenden in November 2011
#
# Note: Everything is passed through the state object, s.
#     : There should be no need to modify this file.  
#
# The other files in this package are:
#                             ab_initio.py
#                             dynamics.py
#                             setup.py
#                             state.py
#                             util.py
#
# and some program specific modules: g98.py g98_dat.py molpro.py nwchem.py ...

# load standard modules
import sys
# load grow-specific modules
import setup
import dynamics
import ab_initio

# evaluate command line, returning the state object
s = setup.command_line(sys.argv)

# count the number of data points already in the POT file 
# and prepare ab initio methods, perform sanity check on internal state
setup.POT_count(s)
ab_initio.do_setup(s)
s.validate()
s.dump()

# if not restarting then change state to sampling
if (s.Mode != 'restart'):
  s.Stage='sample'

# main loop: arranged as a switched while to enable restarting mid-loop
while s.Iter <= s.MaxIter:
  print '>========= Iteration ',s.Iter,' of ',s.MaxIter,' =================================================<\n'
  if (s.Stage == 'sample'):
    print 'running dynamics iteration',s.Iter
    print 'number of points in POT file:',s.NumData
    print ' '
    dynamics.do_dynamics(s)                 # set the flag so we do choose next
    s.Stage = 'choose'                      # save state so we don't redo 
    s.dump()                                # sampling on restart
  if (s.Stage == 'choose'):                 
    dynamics.do_choose(s)                   # set the flag so we do ab initio 
    s.Stage = 'ab initio'                   # calcs next.  save state so we 
    s.dump()                                # don't redo choosing on restart
  if (s.Stage == 'ab initio'):           
    for i in range(s.PtsAdded,s.Pts2add):   # start loop at last point added
      if s.AI_DoCalc == 'true':             # if we died in add_to_POT, 
        ab_initio.do_calc(s)                #   don't redo ab initio calc 
        s.dump()                            # save state so restart works
      ab_initio.do_add_to_POT(s)  
      s.NumData+=1                          # Number of points in POT file ++
      s.PtsAdded+=1                         # increment local counter
      s.dump()                              # save current position in cycle 
    s.PtsAdded=0                            # reset counter before next loop 
  if (((s.Iter > 0 ) and ( (s.Iter % s.CvgceChk) == 0 )) or ( s.Stage == 'convergence')):
    s.Stage = 'convergence'
    print '>===============================================================================<\n'
    dynamics.do_convergence_check(s)
  s.Stage = 'sample'   # reset the Stage so we start from sampling again
  s.Iter+=1            # update the loop counter 
  s.dump()             # save the current state

# cleanup?
 
  
