#!/usr/bin/python2
#======================================
# gaussian09 module of Grow2.2 package
# modified by Meredith Jordan Match 03
# g03 -> g16 Keiran Rowell August 17
#======================================

# note that data strings are defined in the module g16_dat.py
# to add/modify ab initio methods, edit that file
# comfiles are built up from headers, coordinates and footers

#==========================================================================
# NOTE - all functions assume the state object has been passed to them as s
#==========================================================================

import os
import shutil
import string
import util
import g16_dat

#==========================================================================
# a function to establish data structures for g16 methods
# called once on startup/restart
#==========================================================================

def setup(s):
  ' Function to setup for a gaussian calculations '
  print '    g16 setup \n' 
  # should we check here that methods exist?
  s.AI_Headers['scf'] = []

  # build a sequence of ab initio header's for scf calcs
  # there are 4 'default' headers for the scf calculation
  # using various options of the HOMO & LUMO guessed orbitals

  for i in range(0,len(g16_dat.scf)):
    hdr='%chk=' + s.AI_Scratch + s.Molecule + '.chk \n'
    if s.AI_Rwf != 'default':
      hdr += '%rwf=' + s.AI_Rwf + '\n'
    hdr+='%mem=' + s.AI_Memory
    hdr+=g16_dat.scf[i]
    hdr+='\n Stability job for ' + s.Molecule + '\n\n'
    hdr+= ' ' + str(s.AI_Charge) + ' ' + str(s.AI_Spin) + '\n'
    s.AI_Headers['scf'].append(hdr)

  # now, add some correlated headers

  if s.AI_JobType == 'simple':

    # only need one type of frequency calculation

    hdr='%chk=' + s.AI_Scratch + s.Molecule + '.chk \n'
    if s.AI_Rwf != 'default':
      hdr += '%rwf=' + s.AI_Rwf + '\n'
    hdr+='%mem=' + s.AI_Memory + '\n'
    if s.AI_NProc != 'default':
      hdr+= '%NProcShared=' + s.AI_NProc
    hdr+=g16_dat.methods[s.AI_Simple]
    hdr+='\n Frequency calculation for ' + s.Molecule + '\n\n'
    hdr+= ' ' + str(s.AI_Charge) + ' ' + str(s.AI_Spin) + '\n'
    s.AI_Headers['simple']=hdr

    # header for energy checks 
    # (used in the steepest descents minimization to 
    #  find the bottom of any hole in the PES

    hdr='%chk=' + s.AI_Scratch + s.Molecule + 'en.chk \n'
    if s.AI_Rwf != 'default':
      hdr += '%rwf=' + s.AI_Rwf + '\n'
    hdr+='%mem=' + s.AI_Memory + '\n'
    if s.AI_NProc != 'default':
      hdr+= '%NProcShared=' + s.AI_NProc
    hdr+=g16_dat.methods[s.AI_Simple + 'scf']
    hdr+='\n Energy calculation for ' + s.Molecule +  '\n\n'
    hdr+= ' ' + str(s.AI_Charge) + ' ' + str(s.AI_Spin) + '\n'
    s.AI_Headers['en']=hdr

    # header for the singlet energy check
    #  (only do the singlet/triplet energy check for job type 'simple')

    hdr='%chk=' + s.AI_Scratch + s.Molecule + '.chk \n'
    if s.AI_Rwf != 'default':
      hdr += '%rwf=' + s.AI_Rwf + '\n'
    hdr+='%mem=' + s.AI_Memory + '\n'
    if s.AI_NProc != 'default':
      hdr+= '%NProcShared=' + s.AI_NProc
    hdr+=g16_dat.methods['sp']
    hdr+='\n Single point energy calc for singlet ' + s.Molecule + '\n\n'
    hdr+= ' ' + str(s.AI_Charge) + ' ' + str(s.AI_Spin) + '\n'
    s.AI_Headers['sp1']=hdr

    # header for the triplet energy check

    hdr='%chk=' + s.AI_Scratch + s.Molecule + '.chk \n'
    if s.AI_Rwf != 'default':
      hdr += '%rwf=' + s.AI_Rwf + '\n'
    hdr+='%mem=' + s.AI_Memory + '\n'
    if s.AI_NProc != 'default':
      hdr+= '%NProcShared=' + s.AI_NProc
    hdr+=g16_dat.methods['sp']
    hdr+='\n Single point energy calc for triplet ' + s.Molecule + '\n\n'
    hdr+= ' ' + str(s.AI_Charge) + ' 3' + '\n'
    s.AI_Headers['sp3']=hdr

  elif s.AI_JobType == 'scaled':

   # need 3 types of frequency calculation
   # first the High Accuracy calculation at Small basis

    hdr='%chk=' + s.AI_Scratch + s.Molecule + '.chk \n'
    if s.AI_Rwf != 'default':
      hdr += '%rwf=' + s.AI_Rwf + '\n'
    hdr+='%mem=' + s.AI_Memory + '\n'
    if s.AI_NProc != 'default':
      hdr += '%NProcShared=' + s.AI+NProc
    hdr+=g16_dat.methods[s.AI_High]
    hdr+='\n High level Small basis Frequency calculation for ' + s.Molecule + '\n\n'
    hdr+= ' ' + str(s.AI_Charge) + ' ' + str(s.AI_Spin) + '\n'
    s.AI_Headers['HighSmall']=hdr

   # then the Low Accuracy calculation at Large basis

    hdr='%chk=' + s.AI_Scratch + s.Molecule + '.chk \n'
    if s.AI_Rwf != 'default':
      hdr += '%rwf=' + s.AI_Rwf + '\n'
    hdr+='%mem=' + s.AI_Memory + '\n'
    if s.AI_NProc != 'default':
      hdr += '%NProcShared=' + s.AI_NProc
    hdr+=g16_dat.methods[s.AI_Low]
    hdr+='\n Lower level Small basis Frequency calculation for ' + s.Molecule + '\n\n'
    hdr+= ' ' + str(s.AI_Charge) + ' ' + str(s.AI_Spin) + '\n'
    s.AI_Headers['LowSmall']=hdr

   # then the Low Accuracy calculation at Small basis

    hdr='%chk=' + s.AI_Scratch + s.Molecule + '.chk \n'
    if s.AI_Rwf != 'default':
      hdr += '%rwf=' + s.AI_Rwf + '\n'
    hdr+='%mem=' + s.AI_Memory + '\n'
    if s.AI_NProc != 'default':
      hdr += '%NProcShared=' + s.AI_NProc
    hdr+=g16_dat.methods[s.AI_Low]
    hdr+='\n Lower level Large basis Frequency calculation for ' + s.Molecule + '\n\n'
    hdr+= ' ' + str(s.AI_Charge) + ' ' + str(s.AI_Spin) + '\n'
    s.AI_Headers['LowLarge']=hdr


#==========================================================================
# main function for running Gaussian16 jobs
#==========================================================================

def calc(s):
  ' Function to run a gaussian calculation '

  # the trick used here is that 'simple' is used for the size in unscaled jobs

  print '    g16_calc'

  # two main branches...

  if s.AI_JobType == 'simple':   

    # do the SCF stability calculation 

    scf_stability('simple',s)

    # check the 'mp2' singlet and triplet energies
    # to ensure the singlet energy is lower than the
    # triplet energy
   
    if s.AI_Spin == 1:
      check_triplet('simple',s)    #-KR this was inteferring with non-singlet surfaces, hence the if statement

    # just the one frequency calc to perform

    print '    g16 beginning frequency calculation '
    frequency_calc('simple',s.AI_Simple,'simple',s)
    shutil.copy2('freq.dat', s.Molecule + '.simple.dat')

  # otherwise do High-Small, Low-Large, and Low-Small freq calcs

  elif s.AI_JobType == 'scaled':

    # if this is a restarted job, check to see if the temporary files
    # already exist... if they do check their dates are sensible...
    # and if they are, then skip that step this time.
    # remove temporary files

    util.Rmf('freq.small.dat')
    util.Rmf('freq.large.dat')
    util.Rmf('freq.high.dat')

    # do the small scf stability job

    scf_stability('small',s)

    # do the large scf stability job

    scf_stability('large',s)

    # at this point only do the singlet/triplet energy
    # check for the 'simple' calculation type

    # go straight to start with low-small freq job

    frequency_calc('LowSmall',s.AI_Low,'small',s)
    shutil.copy2('freq.dat','freq.small.dat')

    # then the low-large freq job

    frequency_calc('LowLarge',s.AI_Low,'large',s)
    shutil.copy2('freq.dat','freq.large.dat')

    # finally the high-small freq job

    frequency_calc('HighSmall',s.AI_High,'small',s)
    shutil.copy2('freq.dat','freq.high.dat')

    # combine the three frequency results to get a scaled data point

    datfile = s.Molecule + '.scaled.dat'
    util.Run('basiscorr > ' + datfile,s)

#======================================================
# function to identify type of ab initio frequency job
#======================================================
def frequency_calc(job_key,method,size,s):
  ' Given the method and basis type, calculate the second derivatives \n\
    results are written to file molecule.freq.size.dat '

  # interrogate the dictionary g16_dat.available
  # to see whether nethod is available and
  # whether there are analytic forces or frequencies

  availability = ''
  for k in g16_dat.available:
    if g16_dat.available[k].count(method) == 1:
      availability = k
      break

  # cleanup in advance and get an scf checkpoint 
  # from somewhere

# util.Rmf('freq.dat')
  shutil.copy2(s.AI_Scratch + s.Molecule + '.scf.' + size + '.chk', s.AI_Scratch + s.Molecule + '.chk')

  # now choose the appropriate calculation 

  if availability == 'analytic frequencies':
    analytic_freq(job_key,size,s)
  elif availability == 'analytic gradients':
    numerical_freq_analytic_grad(job_key,size,s)
  elif availability == 'energies only':
    numerical_freq_energy_only(job_key,size,s)
  else:
    util.DieError('MethodError:',' Method ' + method +' not found in g16_dat.available[]',s)

 
#=======================================
# function to run the scf stability jobs
#=======================================
def scf_stability(size,s):
  ' Function to run SCF stability jobs'

  # note that size may be 'simple', 'small', or 'large'

  logfile = s.Molecule + '.log'
  print '    g16 scf ' + size 

  # run the sequence of scf jobs

  for j in range(0,len(g16_dat.scf)):

    # build the com file

    method = s.AI_Headers['scf'][j]
    comfile = build_comfile(method,size,s)

    # run the gaussian calculation without watching exit status

    os.system('g16 <' + comfile + ' > ' + logfile)

    # check for normal termination and put the checkpoint file somewhere

    if normal_termination(logfile,s):
      print '    g16 scf ' + size + ': calc ' + str(j+1) + ' converged '
      shutil.copy2(s.AI_Scratch + s.Molecule + '.chk',s.AI_Scratch + s.Molecule + '.scf.' + size + '.chk')

      # copy the chekpoint file to save.chk to reuse later

      os.system('cp ' + s.AI_Scratch + s.Molecule + '.chk save.chk')
      break
    else:
      print '    g16 scf ' + size + ': calc ' + str(j+1) + ' FAILED '
      if (j+1) == len(g16_dat.scf):
        util.DieError('SCF','Wavefunction did not converge ',s)


#============================================================
# function to check the singlet/triplet energy difference
#============================================================
def check_triplet(size,s):
  ' Function to run singlet and triplet single point energies'

  # note that although size may be 'simple', 'small', 
  # or 'large', we are only doing this, at present, for
  # the 'simple' calculation type

  logfile = s.Molecule + '.log'
  print '    g16 single point energies ' + size 

  # run the sequence of single point energies: 
  #  sp1 singlet, sp3 triplet

  # build the com file for single point singlet energy

  method = s.AI_Headers['sp1']
  comfile = build_comfile(method,size,s)

  # run the gaussian calculation without watching exit status

  os.system('g16 <' + comfile + ' > ' + logfile)

  # check for normal termination and put the checkpoint file somewhere

  if normal_termination(logfile,s):
    print '    g16 sp1 ' + size + ': calc converged '

    # get singlet energy, energy1, from the checkpoint file

    energy1=''
    fc = util.grab_contents('Test.FChk',s)
    for line in range(0,len(fc)):
      if string.find(fc[line],'Total Energy') != -1:
        energy1=fc[line].split()[3]
#       energy1=energy1.replace('D','e')  # python doesn't speak fortran
#     break
  else:
    print '    g16 check_triplet ' + size + ': calc FAILED '
    util.DieError('check_triplet','Singlet Wavefunction did not converge ',s)
  energy1=float(energy1)
  print '    Singlet Energy: ',energy1 

  # build the com file for single point triplet energy

# os.system('cp save.chk ' + s.Molecule + '.chk')
# method = s.AI_Headers['sp3']
# comfile = build_comfile(method,size,s)

  # run the gaussian calculation without watching exit status

# os.system('g16 <' + comfile + ' > ' + logfile)

  # check for normal termination and put the checkpoint file somewhere

# if normal_termination(logfile,s):
#   print '    g16 sp3 ' + size + ': calc converged '

    # get triplet energy, energy3, from the checkpoint file

#   energy3=''
#   fc = util.grab_contents('Test.FChk',s)
#   for line in range(0,len(fc)):
#     if string.find(fc[line],'Total Energy') != -1:
#       energy3=fc[line].split()[3]
#       energy3=energy3.replace('D','e')  # python doesn't speak fortran
#     break
# else:
#   print '    g16 check_triplet ' + size + ': calc FAILED '
#   util.DieError('check_triplet','Triplet wavefunction did not converge ',s)
# energy3=float(energy3)
# print '    Triplet Energy: ',energy3 

  # check singlet/triplet energy difference
  # giving a tolerance for the energy difference

# echeck=0.0
# echeck = energy1 - energy3
# print '    difference between singlet and triplet energies: ',echeck 

# if ( echeck > 0.00001 ):
#   print '   triplet energy is lower than singlet energy'
#   util.DieError('check_triplet','Triplet energy is lower than singlet energy',s)
  os.system('cp save.chk ' + s.AI_Scratch + s.Molecule + '.chk')

  # clean up

  util.Rmf('save.chk')

#========================================
# function to run analytic frequency job
#========================================
def analytic_freq(job_key,size,s):
  ' Function to run an analytic frequency calculation '
  print '    g16 analytic frequency ' + size 

  # build comfile, run the job

  logfile = s.Molecule + '.log'
  keyword_string = s.AI_Headers[job_key]
  comfile = build_comfile(keyword_string,size,s)
  util.Run('g16 <' + comfile + ' > ' + logfile,s)

  # check for normal termination and spin contamination

  if normal_termination(logfile,s):
    print '    g16 analytic frequency ' + size + ': completed successfully'
    contaminated = testspin(s.AI_Spin,logfile,s)
    if contaminated:
      util.DieError('SpinError','Correlated wavefunction is spin contaminated',s)
  else:
    util.DieError(method,'Analytic frequency calculation failed',s)

  # get the zero point energy from the logfile
  # if it is being used for the dynamics
  # NB commented out as is not in setup or state

  #if s.ZPE == '.true.':
  #  fc = util.grab_contents(logfile,s)
  #  s.ZPE_value = ''
  #  for line in range(0,len(fc)):
  #    if string.find(fc[line],'Zero-point corr') != -1:
  #      s.ZPE_value = fc[line].split()[2] + '\n'
  #  print '    Harmonic zpe (au): ' + s.ZPE_value 

  # get the energy and derivative data from the formatted 
  # checkpoint file "Test.FChk"

  energy=''
  natom=''
  fc = util.grab_contents('Test.FChk',s)
  for line in range(0,len(fc)):
    if string.find(fc[line],'Total Energy') != -1:
      energy = fc[line].split()[3] + '\n'
    if string.find(fc[line],'Total energy') != -1:
      energy = fc[line].split()[3] + '\n'
    if string.find(fc[line],'Number of atoms') != -1:
      natom = fc[line].split()[4]
  natom = int(natom)
  fc = util.grab_contents('fort.7',s)
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
  for line in range(0,len(fc)):
    coord += fc[line].split()[1] + '  ' + fc[line].split()[2] + '  ' + fc[line].split()[3] + '\n'

  # write the derivative information to a file for bfinvert to read
  #  NB commented out the ZPE correction to the PES

  dat=file('freq.dat','w')
  dat.write(' --- data point #' + str(s.NumData + 1) + '\n')
  dat.writelines(coord)
  dat.writelines(energy)
  dat.writelines(grad)
  dat.writelines(freq)
  dat.close()

  #if s.ZPE == '.true.':
  #  dat.writelines(str(s.ZPE_value))

  dat.close()
  n = str(s.NumData+1)

# keep a running record of the data point information

#  util.Run('cp fort.7 add' + n + '.derivs',s)
#  util.Run('cp ' + s.Molecule + '.log add' + n + '.log',s)
#  util.Run('cp cdata_bohr add' + n + '_bohr',s)
  util.Run('cp freq.dat add' + n + '.freq.dat',s)
#  util.Run('cp Test.FChk add' + n + '.fchk',s)

#=================================================================
# function to run numerical frequency job from analytic gradients
#=================================================================
def numerical_freq_analytic_grad(job_key,size,s):
  ' Function to run a numerical frequency calculation using analytic gradients'

  # preparations

  print '    g16 numerical frequency (gradients) ' + size 
  logfile = s.Molecule + '.log'
  keyword_string = s.AI_Headers[job_key]

  # make displaced geometries, note that CARTVECS is in bohr

  util.Rmf('grad.geoms')
  util.Run('diffsteps < CARTVECS > grad.geoms',s)
  fc = util.grab_contents('grad.geoms',s)

  # diffsteps puts one atom per line, use this to find natom, nint

  line=1  # fc[0] is the first line and we want to skip it
  while string.find(fc[line],'coordinates') == -1:
    line+=1
  Natom = line-1       # undo final increment
  Nint = 3*Natom - 6
  Ngrad = 2*Nint + 1

  # now we know how many line of grad.geoms to read, although we count from zero

  Nlines = Ngrad*(Natom+1) - 1
  geoms=[]
  for line in range(0,Nlines):
    if string.find(fc[line],'coordinates') != -1:
      line+=1
      tmp=[]
      while fc[line][:2] != '  ':
        tmp.append(fc[line])
        line+=1
      geoms.append(tmp)

  # quick check

  if len(geoms) != Ngrad: 
    util.DieError('Freq:',' Ngrad = ' + str(Ngrad) + ' len(geoms) = ',str(len(geoms)),s)  

  # loop over displaced geometries  

  util.Rmf(s.Molecule + '.numfreq.dat')
  numfreq=file(s.Molecule +'.numfreq.dat','w')
  numfreq.write(' Gradients for numerical frequencies of ' + s.Molecule + '\n')
  for k in range(0,len(geoms)):

    # cleanup in advance

    util.Rmf('cdata_ang')
    util.Rmf('cdata_bohr')
    util.Rmf('fort.7')
    util.Rmf('Test.FChk')

    # write out coordinates and convert to angstroms

    coords = file('cdata_bohr','w')
    coords.writelines(geoms[k])
    coords.close()
    util.Run('Bohr2Ang < cdata_bohr > cdata_ang',s)

    # build comfile and run gradient calculation

    comfile = build_comfile(keyword_string,size,s)
    util.Run('g16 <' + comfile + ' > ' + logfile,s)

    # check for normal termination and spin contamination

    if normal_termination(logfile,s):
      print '    g16 gradient ' + size + ' : calc ',k
      contaminated = testspin(s.AI_Spin,logfile,s)
      if contaminated:
        util.DieError('SpinError','Correlated wavefunction is spin contaminated',s)
    else:
      util.DieError(method,'Gradient calculation failed',s)

    # extract energy from Test.FChk...

    fc = util.grab_contents('Test.FChk',s)
    Energy=''
    for line in range(0,len(fc)):
      if string.find(fc[line],'Total Energy') != -1:
        Energy = fc[line].split()[3] + '\n'
	break

    #... and forces from fort.7

    fc = util.grab_contents('fort.7',s)
    Forces=''
    for line in range(0,len(fc)):
      if string.find(fc[line],'Forces:') != -1:
        line += 1
	for x in range(line,line+Natom):
          Forces+=fc[x]
        break

    # change the signs because fort.7 contains forces and we want gradients

    dVdX=Forces.split()
    for k in range(0,len(dVdX)):
      dVdX[k] = dVdX[k].replace('D','e')   # python doesn't speak fortran
      dVdX[k] = str(float(dVdX[k])*(-1))

    # now we rearrange the gradients into natom lines of 3 numbers

    grad=''
    while len(dVdX) != 0:
      grad += '  ' + dVdX.pop(0) + '  ' + dVdX.pop(0) + '  ' + dVdX.pop(0) + ' \n'

    # add the energies and gradients at this displaced geometry to the file

    numfreq.write(Energy)
    numfreq.writelines(grad)

  # would like to save state here...
  # now combine the results into an array of second derivatives

  numfreq.close()
  util.Run('grad2freq < ' + s.Molecule + '.numfreq.dat > freq.dat',s)


#=============================================================
# function to run numerical frequency job from energies only
#=============================================================
def numerical_freq_energy_only(job_key,size,s):
  ' Function to run a numerical frequency calculation using energies only'

  # preparation 

  print '    g16 numerical frequency (energies) ' + size 
  logfile = s.Molecule + '.log'
  keyword_string = s.AI_Headers[job_key]

  # make displaced geometries, note that CARTVECS is in bohr

  util.Rmf('en.geoms')
  util.Run('diffsteps < CARTVECS > en.geoms',s)

  # read in displaced geometries into a list of lists

  fc = util.grab_contents('en.geoms',s)
  geoms=[]
  for line in range(0,len(fc)):
    if string.find(fc[line],'coordinates') != -1:
      line+=1
      tmp=[]
      while fc[line][:2] != '  ':
        tmp.append(fc[line])
        line+=1
      geoms.append(tmp)

  # loop over displaced geometries

  util.Rmf('s.Molecule.numfreq.dat')
  numfreq = file(s.Molecule + '.numfreq.dat','w')
  numfreq.write(' Energies for numerical frequencies of ' + s.Molecule + '\n')
  for k in range(0,len(geoms)):

    # cleanup in advance

#   util.Rmf('cdata_ang')
#   util.Rmf('cdata_bohr')
#   util.Rmf('Test.FChk')

    # write out coordinates and convert to angstroms

    coords = file('cdata_bohr','w')
    coords.writelines(geoms[k])
    coords.close()
    util.Run('Bohr2Ang < cdata_bohr > cdata_ang',s)

    # build comfile and run gradient calculation

    comfile = build_comfile(keyword_string,size,s)
    util.Run('g16 <' + comfile + ' > ' + logfile,s)

    # check for normal termination and spin contamination 

    if normal_termination(logfile,s):
      print '    g16 energy ' + size + ' : calc ', k
      contaminated = testspin(s.AI_Spin,logfile,s)
      if contaminated:
        util.DieError('SpinError','Correlated wavefunction is spin contaminated',s)
    else:
      util.DieError(method,'Energy calculation failed',s)

    # extract energy and force

    fc = util.grab_contents('Test.FChk',s)
    Energy=''
    for line in fc:
      if string.find(line,'Total Energy') != -1:
        Energy = fc[line].split()[3] + '\n'
        break

    # add the energy at this displaced geometry to the file

    numfreq.write(Energy)

  # would like to save state here...
  # now combine the results into an array of second derivatives

  numfreq.close()
  util.Run('en2freq < ' + s.Molecule + '.numfreq.dat > freq.dat',s)


#==========================================================================
# munge the results of a frequency calc to produce POT data
#==========================================================================
def add_to_POT(s):
  print '    g16_add_to_POT'

  # cleanup in advance

# util.Rmf('POT.temp')
  f = file('POT.temp','w')
  f.write(' --- data point #' + str(s.NumData+1) + '\n')
  f.close()

  # process cartesian derivative data into local internal coords

  datfile = s.Molecule + '.' + s.AI_JobType + '.dat' 
  output = os.popen('bfinvert < ' + datfile,'r')
  outlist = output.readlines()
  output.close()
  f = file('POT.temp','a')
  f.writelines(outlist)

  # add harmonic zero-point energy to the end of the file
  # if it is being used for the dynamics
  # NB commented out

  #if s.ZPE == '.true.':
  #  f.writelines(str(s.ZPE_value))

  f.close()

  # append new data to end of the POT file

  util.Run('cat POT.temp >> POT',s)


#==========================================================================
# function to construct a com file from the various pieces, including 
# current coords which are taken from a file called 'cdata'
#==========================================================================
def build_comfile(method_string,size,s):
  ' Function to build the kth gaussian com file '

  # build the command file as a list of strings

  command = []

  # use a here document so that the shell expands the $scratch symbol properly

  #command.append('#!/bin/sh \n g16 << +++ \n') 
  # add the keywords for this job, ie, use the actual string not a pointer

  command.append(method_string)

  # read in the coordinates from file cdata_ang, since gaussian 
  # expects coords in angstroms

  fc = util.grab_contents('cdata_ang',s)

  # append the coordinates to the comfile sequence

  for line in fc:
    command.append(line)

  # append appropriate footer containing basis set specification

  command.append('\n')
  command.append(s.AI_Footers[size])

  # close the here document and append some blank lines just to be safe

  command.append('\n+++\n\n')

  # name the comfile, and remove any old versions

  target = s.Molecule + '.com'
  util.Rmf(target)

  # write the new comfile

  f = file(target,'w')
  f.writelines(command)
  f.close()

  # make it executable and return the name of the comfile

  #os.chmod(target,484)
  return target

#==========================================================================
# utility function used to see if gaussian did its thang
#==========================================================================
def normal_termination(logfile,s):
  ' utility function used to see if gaussian did its thang '

  # read in the contents of the logfile

  fc = util.grab_contents(logfile,s)

  # set return flag to 0

  success=0
  for line in fc:
    if (string.find(line,'Normal termination of Gaussian') != -1):
      success=1
      break
  return success

#==========================================================================
# utility function to check for spin contamination 
#==========================================================================
def testspin(M,logfile,s):
  ' check that S**2 is close to M'

  # read in the contents of the gaussian logfile

  fc = util.grab_contents(logfile,s)

  # now look for S**2, noting that in some singlet calculations it is not reported

  S2=0.00

  # determine the pure spin state value

  expected_spin = 0.5*(M-1)*(0.5*(M-1)+1)

  # extract spin from the gaussian logfile for
  # unrestricted wavefunctions (ie starting letter is "u")

  check=s.AI_Simple[0]

  if (check == 'u'):
    if (s.AI_Simple == 'ccsd(t)' or s.AI_Simple == 'CCSD(T)'):
      for line in range(len(fc)):
        if (string.find(fc[line],' spins ') != -1):
          line = line + 2
          S2 = float(string.split(fc[line])[1]) 
          break
    else:  
      for line in range(len(fc)):
        if (string.find(fc[line],' before annihilation ') != -1):
          S2 = float(string.split(fc[line])[3][:-1])  # removing trailing comma
          break

  # and restricted wavefunctions

  else:
    for line in range(len(fc)):
      if (string.find(fc[line],' S**2   = ') != -1):
        S2 = float(string.split(fc[line])[2]) 
        break

  # compare spins - with a tolerance of 0.1

  if ( abs(expected_spin-S2) < 0.1 ):
    contaminated = 0
  else:
    contaminated = 1
    print 'S**2 ', S2, ' expected ', expected_spin
  return contaminated

#==========================================================================
# utility function to grab coordinates from a g16 log file
#==========================================================================
def coords_from_logfile(fname,s):
  ' grab all the coordinates from a log file '
  fc = util.grab_contents(fname,s)

  # look for the 'input orientation'

  coords=[]
  for line in range(0,len(fc)):
    geom=[]
    if string.find(fc[line],'Input orientation:') != -1:
      line+=5
      while fc[line][0:3] != ' --': #This caused issues when the --- didn't have a space. Maybe chance to just see if fc[line].split()[1] is not a number? -KR
        x = fc[line].split()
	sym = util.atomic_symbol(int(x[1]))
	atom = ' ' + sym + ', ' + x[3] + ', ' + x[4] + ', ' + x[5] + ' \n'
	geom.append(atom)
        line+=1
      coords.append(geom)

  return coords




