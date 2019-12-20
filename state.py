#!/usr/bin/python2
#==========================================
# the state module of the Grow2.2 package
# modified by Meredith Jordan March 2006
#==========================================

# it also contains various predefined lists:
# edit the list _abprog to change/add to the recognised ab initio packages
# edit the list _dynamics to change/add to the ways new configurations are generated
# do not edit the list _stages unless you know exactly what you are doing!!

import pickle
import util

#=============================================
# define the GrowState object and its methods
#=============================================
class GrowState:
  "The state class for the Grow script, including predefined lists"

  # some lists which might change
  _dynamics = [ 'classical', 'qdmc', 'pimc', 'fms90' ]
  _abprog = [ 'Gaussian09', 'Gaussian16', 'Gaussian03', 'Gaussian98', 'Molpro2002', 'NWChem4.1', 'Aces2', 'CFour' ]

  # a list which probably should not change
  _stages = [ 'restart', 'setup', 'sample', 'choose', 'ab initio', 'convergence' ]
  _modes = ['new','restart','startPOT']

  def __init__(self):
    # system specific variables
    self.Molecule = ''     # string to use as stem for all temporary files
    # iteration variables
    self.MaxIter  = 1      # number of iterations to perform
    self.Pts2add  = 1      # number of data points to add at each iteration
    self.rmsPts2add = 1    # number of rms points to add per iteration
    self.hwtPts2add = 1    # number of hwt points to add per iteration
    self.PtsAdded = 0      # number of data points added in this  iteration
    self.CvgceChk = 1      # run a convergence job every CvgceChk iterations
    self.Iter = 1          # counter for iterations
    self.NumData = 0       # index of current data point to be added to POT
    self.Stage = ''        # string identifying current stage in current iteration
    self.Mode = ''         # one of _modes, how was the script started?
    # ab initio variables
    self.AI_DoCalc = 'true'# Flag for doing or skipping ab initio calculation
    self.AI_Charge   = 0   # the overall charge of the molecule
    self.AI_Spin     = 0   # spin of the electronic system being calculated
    self.AI_Verbatim = ''  # string to place in command line of input file
    self.AI_Scratch = ''   # string specifying scratch directory
    self.AI_Rwf     = ''   # string specifying read-write specs
    self.AI_NProc   = ''   # number of processors to use in ab initio calc
    self.AI_Headers = {}   # dictionary of ab initio headers
    self.AI_Footers = {}   # dictionary of ab initio footers
    self.AI_Command = {}   # dictionary of command lines for ab initio calcs
    self.AI_Package  = ''  # name of program called to perform ab initio calcs
    self.AI_JobType  = ''  # simple frequencies or scaled by lower accuracy calcs?
    self.AI_High     = ''  # Method to use for high accuracy jobs
    self.AI_Low      = ''  # Method to use for lower accuracy jobs
    self.AI_Simple = ''    # ab initio method used for simple calculations
    self.AI_Basis  = ''    # basis set used for simple calculations
    self.AI_BasSmall = ''  # basis set used for small component of scaled jobs
    self.AI_BasLarge = ''  # basis set used for large component of scaled jobs
    # dynamics variables
    self.Dyn_Sample = ''   # how are new data geometries generated?
    self.Dyn_Cvgce  = ''   # how are observables calculated?
    self.Chosen = []       # a list of lists of coordinates assigned in do_choose()
    self.ChooseType= 'hwt' # method used to select next data point
    self.CoordUnit= 'bohr' # units of configurations passed to ab_initio.py
    self.svdtol = 0        # the zero value tolerance for the singular values decomposition

  def dump(self):
    ' Function to dump state object to a pickled file, fname'
    fname = self.Molecule + '.state'
    f = open(fname, 'w')
    pickle.dump(self,f)
    f.close()

  def validate(self):
    ' check attributes lie in sensible ranges '
    if (self.MaxIter < 0):
      util.DieError('MaxIter:', "Number of iterations may not be negative",self)
    if (self.PtsAdded < 0):
       util.DieError('PtsAdded:', "Number of points added may not be negative",self)
    if (self.CvgceChk < 0):
      util.DieError('CvgceChk:', "Parameter must be positive or zero",self)
    if (self.CvgceChk > self.MaxIter):
      util.DieError('CvgceChk:', "Parameter cannot be greater than NumIter",self)
    if (self.AI_Spin < 0):
      util.DieError('AI_Spin:', "Total electron spin cannot be less than 1",self)
    if (self.AI_DoCalc != 'true' and self.AI_DoCalc != 'false'):
      util.DieError('AI_DoCalc:', "Parameter must be either true or false",self)
    if (self._dynamics.count(self.Dyn_Sample) != 1):
      util.DieError('Dyn_Sample:', "Samplng must be via one of " + str(self._dynamics),self)
    if (self._dynamics.count(self.Dyn_Cvgce) != 1):
      util.DieError('Dyn_Cvgce:', "Convergence must be via one of " + str(self._dynamics),self)
    if (self._stages.count(self.Stage) != 1):
      util.DieError('Stage:', "Variable must be one of " + str(self._stages),self)
    if (self._abprog.count(self.AI_Package) != 1):
      util.DieError('AI_Package:', "Variable must be one of " + str(self._abprog),self)
    if (self._modes.count(self.Mode) != 1):
      util.DieError('Mode:', "Variable must be one of " + str(self._modes),self)
    if (self.AI_JobType != 'simple' and self.AI_JobType != 'scaled'):
      util.DieError('AI_JobType:', 'Parameter must be one of \"simple\" or \"scaled\"',self)
    if (self.rmsPts2add > 1):
      util.DieError('rmsPts2add:',' It doesnt make sense to add more than 1 rms point per iteration, please change rms points to add back to 1',self)

  def IncrementStage(self):
    index = self._stages.index(self.Stage)
    index+=1
    self.Stage = self._stages[index]

  def increment_ChooseType(self):
    if self.ChooseType == 'hwt':
      self.ChooseType = 'rms'
    elif self.ChooseType == 'rms':
      self.ChooseType = 'hwt'
    else:
      self.ChooseType = 'rnd'


  def print_AI(self):
    print ' Package  = ' + self.AI_Package
    print ' Scratch  = ' + self.AI_Scratch
    print ' JobType  = ' + self.AI_JobType
    if self.AI_JobType == 'scaled':
      print ' High   = ' + self.AI_High
      print ' Low    = ' + self.AI_Low
    else:
      print ' Method = ' + self.AI_Simple
    print ' Header file(s) '
    print self.AI_Headers
    print ' Footer file(s) '
    print self.AI_Footers

  def print_Iter(self):
    print ' Mode     = ' + self.Mode
    print ' Stage    = ' + self.Stage
    print ' Iter     = ' + str(self.Iter)
    print ' MaxIter  = ' + str(self.MaxIter)
    print ' Pts2add  = ' + str(self.Pts2add)
    print ' PtsAdded = ' + str(self.PtsAdded)
    print ' CvgceChk = ' + str(self.CvgceChk)
    print ' NumData  = ' + str(self.NumData)
    print ' DoCalc   = ' + self.AI_DoCalc
    print ' svdtol   = ' + str(self.svdtol)

  def print_dynamics(self):
    print ' Dynamics = ' + self.Dyn_Sample
    print ' Dynamics = ' + self.Dyn_Cvgce
    print ' Last Sampled Coordinates:'
    for i in self.Chosen:
      print i,

  def print_job_specific(self):
    print ' Molecule = ' + self.Molecule
    print ' Charge   = ' + str(self.AI_Charge)
    print ' Spin     = ' + str(self.AI_Spin)

  def print_chosen(self):
    for i in range(0,len(self.Chosen)):
      print i,self.Chosen[i]


  def print_all(self):
    self.print_job_specific()
    self.print_dynamics()
    self.print_Iter()
    self.print_AI()

