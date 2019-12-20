#!/usr/bin/python
#======================================
# gaussian09 module of Grow2.2 package
# modified by Meredith Jordan March 03
#======================================

# note that data strings are defined in the module g09_dat.py
# to add/modify ab initio methods, edit that file
# comfiles are built up from headers, coordinates and footers

#==========================================================================
# NOTE - all functions assume the state object has been passed to them as s
#==========================================================================

import os
import shutil
import string
import util
import g09_dat

#==========================================================================
# a function to establish data structures for g09 methods
# called once on startup/restart
#==========================================================================

def setup(s):
  ' Function to setup for a gaussian calculations '
  print '    g09 setup \n' 
  # should we check here that methods exist?
  s.AI_Headers['scf'] = []
  # build a sequence of ab initio header's for scf calcs
  for i in range(0,len(g09_dat.scf)):
    hdr='%chk=' + s.AI_Scratch + s.Molecule + '.chk \n'
    if s.AI_Rwf != 'default':
      hdr += '%rwf=' + s.AI_Rwf + '\n'
    hdr+='%mem=' + s.AI_Memory + '\n'
    if s.AI_NProc != 'default':
      hdr+= '%NProcShared=' + s.AI_NProc
    hdr+=g09_dat.scf[i]
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
    hdr+=g09_dat.methods[s.AI_Simple]
    hdr+='\n Frequency calculation for ' + s.Molecule + '\n\n'
    hdr+= ' ' + str(s.AI_Charge) + ' ' + str(s.AI_Spin) + '\n'
    s.AI_Headers['simple']=hdr

  elif s.AI_JobType == 'scaled':
   # need 3 types of frequency calculation
   # first the High Accuracy calculation at Small basis
    hdr='%chk=' + s.AI_Scratch + s.Molecule + '.chk \n'
    if s.AI_Rwf != 'default':
      hdr += '%rwf=' + s.AI_Rwf + '\n'
    hdr+='%mem=' + s.AI_Memory + '\n'
    if s.AI_NProc != 'default':
      hdr += '%NProcShared=' + s.AI+NProc
    hdr+=g09_dat.methods[s.AI_High]
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
    hdr+=g09_dat.methods[s.AI_Low]
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
    hdr+=g09_dat.methods[s.AI_Low]
    hdr+='\n Lower level Large basis Frequency calculation for ' + s.Molecule + '\n\n'
    hdr+= ' ' + str(s.AI_Charge) + ' ' + str(s.AI_Spin) + '\n'
    s.AI_Headers['LowLarge']=hdr


#==========================================================================
# main function for running Gaussian03 jobs
#==========================================================================

def calc(s):
  ' Function to run a gaussian calculation '
  # the trick used here is that 'simple' is used for the size in unscaled jobs
  print '    g09_calc'
  # two main branches...
  if s.AI_JobType == 'simple':   
    # do the SCF calculation 
    [spin_cont,spin_val] = scf_stability('simple',s)
    if(spin_cont == 0):
      # just the one frequency calc to perform
      print '    g09 beginning frequency calculation '
      frequency_calc('simple',s.AI_Simple,'simple',s)
      shutil.copy2('freq.dat', s.Molecule + '.simple.dat')
    return [spin_cont,spin_val]
  # otherwise do High-Small, Low-Large, and Low-Small freq calcs
  elif s.AI_JobType == 'scaled':
    # if this is a restarted job, check to see if the temporary files
    # already exist... if they do check their dates are sensible...
    # and if they are, then skip that step this time.
    # remove temporary files
    util.Rmf('freq.small.dat')
    util.Rmf('freq.large.dat')
    util.Rmf('freq.high.dat')
    # do the small scf 
    scf_stability('small',s)
    # do the large scf 
    scf_stability('large',s)
    # start with the low-small freq    
    frequency_calc('LowSmall',s.AI_Low,'small',s)
    shutil.copy2('freq.dat','freq.small.dat')
    # then the low-large freq    
    frequency_calc('LowLarge',s.AI_Low,'large',s)
    shutil.copy2('freq.dat','freq.large.dat')
    # finally the high-small freq    
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
  # interrogate the dictionary g09_dat.available
  availability = ''
  for k in g09_dat.available:
    if g09_dat.available[k].count(method) == 1:
      availability = k
      break
  # cleanup in advance and get an scf checkpoint from somewhere
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
    util.DieError('MethodError:',' Method ' + method +' not found in g09_dat.available[]',s)

 
#====================================
# function to run the stability jobs
#====================================
def scf_stability(size,s):
  ' Function to run SCF stability jobs'
  # note that size may be 'simple', 'small', or 'large'
  logfile = s.Molecule + '.log'
  print '    g09 scf ' + size 
  # run the sequence of scf jobs
  for j in range(0,len(g09_dat.scf)):
    # build the com file
    method = s.AI_Headers['scf'][j]
    comfile = build_comfile(method,size,s)
    # run the gaussian calculation without watching exit status
    os.system('g09 <' + comfile + ' > ' + logfile)
    # check for normal termination and put the checkpoint file somewhere
    if normal_termination(logfile,s):
      [contaminated,spin_val] = testspin(s.AI_Spin,logfile,s)
      if contaminated==1:
        return [1,spin_val]
        #util.DieError('SpinError','UHF wavefunction is spin contaminated',s)
      print '    g09 scf ' + size + ': calc ' + str(j+1) + ' converged '
      shutil.copy2(s.AI_Scratch + s.Molecule + '.chk',s.AI_Scratch + s.Molecule + '.scf.' + size + '.chk')
      break
    else:
      print '    g09 scf ' + size + ': calc ' + str(j+1) + ' FAILED '
      if (j+1) == len(g09_dat.scf):
        util.DieError('SCF','Wavefunction did not converge ',s)
  return [0,spin_val]

#========================================
# function to run analytic frequency job
#========================================
def analytic_freq(job_key,size,s):
  ' Function to run an analytic frequency calculation '
  print '    g09 analytic frequency ' + size 
  # build comfile, run the job
  logfile = s.Molecule + '.log'
  keyword_string = s.AI_Headers[job_key]
  comfile = build_comfile(keyword_string,size,s)
  util.Run('g09 <' + comfile + ' > ' + logfile,s)
  # check for normal termination and spin contamination
  if normal_termination(logfile,s):
    print '    g09 analytic frequency ' + size + ': completed successfully'
    [contaminated,spin_val] = testspin(s.AI_Spin,logfile,s)
    if contaminated == 1: 
      #shouldn't ever reach this as the spin contamination should be caught earlier than this
      util.DieError('SpinError','Correlated wavefunction is spin contaminated with <S**2> = '+str(spin_val) ,s)
  else:
    util.DieError(method,'Analytic frequency calculation failed',s)
  # get the energy and derivative data from the formatted checkpoint file "Test.FChk"
  fc = util.grab_contents('Test.FChk',s)
  energy=''
  natom=''
  for line in range(0,len(fc)):
    if string.find(fc[line],'Total Energy') != -1:
      energy = fc[line].split()[3] + '\n'
  for line in range(0,len(fc)):
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
  dat=file('freq.dat','w')
  dat.writelines(coord)
  dat.writelines(energy)
  dat.writelines(grad)
  dat.writelines(freq)
  dat.close()
  n = str(s.NumData)
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
  print '    g09 numerical frequency (gradients) ' + size 
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
    util.Run('g09 <' + comfile + ' > ' + logfile,s)
    # check for normal termination and spin contamination
    if normal_termination(logfile,s):
      print '    g09 gradient ' + size + ' : calc ',k
      [contaminated,spin_val] = testspin(s.AI_Spin,logfile,s)
      if contaminated==1:
        util.DieError('SpinError','Correlated wavefunction is spin contaminated with <S**2> = '+ str(spin_val),s)
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
  print '    g09 numerical frequency (energies) ' + size 
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
    util.Run('g09 <' + comfile + ' > ' + logfile,s)
    # check for normal termination and spin contamination 
    if normal_termination(logfile,s):
      print '    g09 energy ' + size + ' : calc ', k
      [contaminated,spin_val] = testspin(s.AI_Spin,logfile,s)
      if contaminated == 1:
        util.DieError('SpinError','Correlated wavefunction is spin contaminated with <S**2> = ' + str(spin_val) ,s)
    else:
      util.DieError(method,'Energy calculation failed',s)
    # extract energy and force
    fc = util.grab_contents('Test.FChk',s)
    Energy=''
    for line in fc:
      if string.find(line,'Total Energy') != -1:
        Energy = line.split()[3] + '\n'
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
  print '    g09_add_to_POT'
  # cleanup in advance
# util.Rmf('POT.temp')
  f = file('POT.temp','w')
  f.write(' --- data point #' + str(s.NumData) + '\n')
  f.close()
  # process cartesian derivative data into local internal coords
  datfile = s.Molecule + '.' + s.AI_JobType + '.dat' 
  output = os.popen('bfinvert < ' + datfile,'r')
  outlist = output.readlines()
  output.close()
  f = file('POT.temp','a')
  f.writelines(outlist)
  f.close()
  # add to POT file
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
  #command.append('#!/bin/sh \n g09 << +++ \n') 
  # add the keywords for this job, ie, use the actual string not a pointer
  command.append(method_string)
  # read in the coordinates from file cdata_ang, since gaussian expects coords in angstroms
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
def testspin(M,fchk,s):
  ' check that S**2 is close to M'
  # read in the contents of the gaussian fchk file
  fc = util.grab_contents(fchk,s)
  # now look for S**2
  S2=0
  expected_spin = 0.5*(M-1)*(0.5*(M-1)+1)
  for line in fc:
    if (string.find(line,'''S**2 before annihilation ''') != -1):
      S2 = float(string.split(line)[3].replace(',',''))  
  # compare
      print "Total Spin Squared value: " + str(S2) 
  if ( abs(expected_spin-S2) < 0.1 ):
    contaminated = 0
  else:
    contaminated = 1
  return [contaminated,S2]


#==========================================================================
# utility function to grab coordinates from a g09 log file
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
      while fc[line][0:3] != ' --':
        x = fc[line].split()
	sym = util.atomic_symbol(int(x[1]))
	atom = ' ' + sym + ', ' + x[3] + ', ' + x[4] + ', ' + x[5] + ' \n'
	geom.append(atom)
        line+=1
      coords.append(geom)
  return coords



