#!/usr/bin/python2
#======================================
# gaussian98 module of Grow2.0 package
#======================================

# note that data strings are defined in the module aces2_dat.py
# to add/modify ab initio methods, edit that file
# comfiles are built up from headers, coordinates and footers

#==========================================================================
# NOTE - all functions assume the state object has been passed to them as s
#==========================================================================

import os
import shutil
import string
import util
import aces2_dat

#==========================================================================
# a function to establish data structures for aces2 methods
# called once on startup/restart
#==========================================================================

def setup(s):
  ' Function to setup for aces2 calculations '
  print '    aces2 setup \n' 

  # interrogate the dictionary aces2_dat.scftype
  method=s.AI_Simple
  scftype = ''
  for k in aces2_dat.scftype:
    if aces2_dat.scftype[k].count(method) == 1:
      scftype = k
      break

  # creating the appropriate command strings depending on the scf calc 
  # required

  hdr='scf calculation for' + s.Molecule
  s.AI_Headers['scf']=hdr

  if scftype == 'rscf':
     s.AI_Command['scf'] = []
     for i in range(0,len(aces2_dat.rscf)):
	cmd=aces2_dat.rscf[i]
	cmd+='MEMORY_SIZE=' + s.AI_Memory + "," + '\n'
	cmd+='CHARGE=' + str(s.AI_Charge) + "," + '\n'
	cmd+='MULT=' + str(s.AI_Spin) + "," + '\n'
        cmd+='BASIS=' + s.AI_Basis + ")" + '\n\n'
        s.AI_Command['scf'].append(cmd)

  elif scftype == 'uscf':
     s.AI_Command['scf'] = []
     for i in range(0,len(aces2_dat.uscf)):
	cmd=aces2_dat.uscf[i]
	cmd+='MEMORY_SIZE=' + s.AI_Memory + "," + '\n'
	cmd+='CHARGE=' + str(s.AI_Charge) + "," + '\n'
	cmd+='MULT=' + str(s.AI_Spin) + "," + '\n'
        cmd+='BASIS=' + s.AI_Basis + ")" + '\n\n'
        s.AI_Command['scf'].append(cmd)

  elif scftype == 'roscf':
     s.AI_Command['scf'] = []
     for i in range(0,len(aces2_dat.roscf)):
	cmd=aces2_dat.roscf[i]
	cmd+='MEMORY_SIZE=' + s.AI_Memory + "," + '\n'
	cmd+='CHARGE=' + str(s.AI_Charge) + "," + '\n'
	cmd+='MULT=' + str(s.AI_Spin) + "," + '\n'
        cmd+='BASIS=' + s.AI_Basis + ")" + '\n\n'
        s.AI_Command['scf'].append(cmd)
  
  else:
     util.DieError('Method Error:','Method' + method + 'not found in aces2_dat.scftype[]', s)

  # now creating the command strings for the frequency jobs

  if s.AI_JobType == 'simple':
    # only need one type of frequency calculation
    cmd=aces2_dat.methods[s.AI_Simple]
    cmd+='MEMORY_SIZE=' + s.AI_Memory + "," + '\n'
    cmd+='CHARGE=' + str(s.AI_Charge) + "," + '\n'
    cmd+='MULT=' + str(s.AI_Spin) + "," + '\n'
    cmd+='BASIS=' + s.AI_Basis + ")" + '\n\n'
    s.AI_Command['simple']=cmd

    hdr='simple frequency calculation for' + s.Molecule
    s.AI_Headers['simple']=hdr

  elif s.AI_JobType == 'scaled':
   # need 3 types of frequency calculation
   # first the High Accuracy calculation at Small basis
    cmd=aces2_dat.methods[s.AI_High]
    cmd+='MEMORY_SIZE=' + s.AI_Memory + "," + '\n'
    cmd+='CHARGE=' + str(s.AI_Charge) + "," + '\n'
    cmd+='MULT=' + str(s.AI_Spin) + "," + '\n'
    cmd+='BASIS=' + s.AI_BasSmall + ")" + '\n\n'
    s.AI_Command['HighSmall']=cmd

    hdr='HighSmall frequency calculation for' + s.Molecule
    s.AI_Headers['HighSmall']=hdr

   # then the Low Accuracy calculation at Large basis
    cmd=aces2_dat.methods[s.AI_Low]
    cmd+='MEMORY_SIZE=' + s.AI_Memory + "," + '\n'
    cmd+='CHARGE=' + str(s.AI_Charge) + "," + '\n'
    cmd+='MULT=' + str(s.AI_Spin) + "," + '\n'
    cmd+='BASIS' + s.AI_BasLarge + ")" + '\n\n'
    s.AI_Command['LowLarge']=cmd

    hdr='LowLarge frequency calculation for' + s.Molecule
    s.AI_Headers['LowLarge']=hdr

   # then the Low Accuracy calculation at Small basis
    cmd=aces2_dat.methods[s.AI_Low]
    cmd+='MEMORY_SIZE=' + s.AI_Memory + "," + '\n'
    cmd+='CHARGE=' + str(s.AI_Charge) + "," + '\n'
    cmd+='MULT=' + str(s.AI_Spin) + "," + '\n'
    cmd+='BASIS=' + s.AI_BasSmall + ")" + '\n\n'
    s.AI_Command['LowSmall']=cmd

    hdr='LowSmall frequency calculation for' + s.Molecule
    s.AI_Headers['LowSmall']=hdr


#==========================================================================
# main function for running Aces2 jobs
#==========================================================================

def calc(s):
  ' Function to run an aces2 calculation '
  # the trick used here is that 'simple' is used for the size in unscaled jobs
  print '    aces2_calc'

  # two main branches...
  if s.AI_JobType == 'simple':   
    # do the SCF calculation 
    scf_stability('simple',s)
    # just the one frequency calc to perform
    print '    aces2 beginning frequency calculation '
    analytic_freq('simple','simple',s)
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
    # do the small scf 
    scf_stability('small',s)
    # do the large scf 
    scf_stability('large',s)
    # start with the low-small freq    
    analytic_freq('LowSmall','small',s)
    shutil.copy2('freq.dat','freq.small.dat')
    # then the low-large freq    
    analytic_freq('LowLarge','large',s)
    shutil.copy2('freq.dat','freq.large.dat')
    # finally the high-small freq    
    analytic_freq('HighSmall','small',s)
    shutil.copy2('freq.dat','freq.high.dat')
    # combine the three frequency results to get a scaled data point
    datfile = s.Molecule + '.scaled.dat'
    util.Run('basiscorr > ' + datfile,s)

 
#====================================
# function to run the stability jobs
#====================================
def scf_stability(size,s):
  ' Function to run SCF stability jobs'
  # note that size may be 'simple', 'small', or 'large'
  logfile = s.Molecule + '.log'
  print '    aces2 scf ' + size 

  # interrogate the dictionary aces2_dat.scftype
  method=s.AI_Simple
  scftype = ''
  for k in aces2_dat.scftype:
    if aces2_dat.scftype[k].count(method) == 1:
      scftype = k
      break

  # run the sequence of scf jobs
  if scftype == 'rscf':
    for j in range(0,len(aces2_dat.rscf)):
      # build the com file
      command_string = s.AI_Command['scf'][j]
      header_string = s.AI_Headers['scf']
      comfile = build_comfile(command_string,header_string,size,s)
      # run the ab initio calculation without watching exit status
      # (that's what the os.system call means)
      os.system('xaces2' + ' > ' + logfile)
      # check for normal termination and put the intermediate files somewhere
      if normal_termination(logfile,s):
        print '    aces2 scf ' + size + ': calc ' + str(j+1) + ' converged '
        shutil.copy2('JAINDX', 'JAINDX'+'.scf')
        shutil.copy2('JOBARC', 'JOBARC'+'.scf')
        break
      else:
        print '    aces2 scf ' + size + ': calc ' + str(j+1) + ' FAILED '
        if (j+1) == len(aces2_dat.rscf):
          util.DieError('SCF','Wavefunction did not converge ',s)
  elif scftype == 'uscf':
    for j in range(0,len(aces2_dat.uscf)):
      # build the com file
      command_string = s.AI_Command['scf'][j]
      header_string = s.AI_Headers['scf']
      comfile = build_comfile(command_string,header_string,size,s)
      # run the ab initio calculation without watching exit status
      # (that's what the os.system call means)
      os.system('xaces2' + ' > ' + logfile)
      # check for normal termination and put the intermediate files somewhere
      if normal_termination(logfile,s):
        print '    aces2 scf ' + size + ': calc ' + str(j+1) + ' converged '
        shutil.copy2('JAINDX', 'JAINDX'+'.scf')
        shutil.copy2('JOBARC', 'JOBARC'+'.scf')
        break
      else:
        print '    aces2 scf ' + size + ': calc ' + str(j+1) + ' FAILED '
        if (j+1) == len(aces2_dat.uscf):
          util.DieError('SCF','Wavefunction did not converge ',s)
  elif scftype == 'roscf':
    for j in range(0,len(aces2_dat.roscf)):
      # build the com file
      command_string = s.AI_Command['scf'][j]
      header_string = s.AI_Headers['scf']
      comfile = build_comfile(command_string,header_string,size,s)
      # run the ab initio calculation without watching exit status
      # (that's what the os.system call means)
      os.system('xaces2' + ' > ' + logfile)
      # check for normal termination and put the intermediate files somewhere
      if normal_termination(logfile,s):
        print '    aces2 scf ' + size + ': calc ' + str(j+1) + ' converged '
        shutil.copy2('JAINDX', 'JAINDX'+'.scf')
        shutil.copy2('JOBARC', 'JOBARC'+'.scf')
        break
      else:
        print '    aces2 scf ' + size + ': calc ' + str(j+1) + ' FAILED '
        if (j+1) == len(aces2_dat.roscf):
          util.DieError('SCF','Wavefunction did not converge ',s)


#========================================
# function to run analytic frequency job
#========================================
def analytic_freq(job_key,size,s):
  ' Function to run an analytic frequency calculation '
  print '    aces2 analytic frequency ' + size 
  # build comfile, run the job
  logfile = s.Molecule + '.log'
  gradlogfile = s.Molecule + '.grad' + '.log'
  command_string = s.AI_Command[job_key]
  header_string = s.AI_Headers[job_key]
  comfile = build_comfile(command_string,header_string,size,s)
  # run gradient calculation first
  util.Run('xjoda' + ' > ' + gradlogfile,s)
  util.Run('xvmol' + ' >> ' + gradlogfile,s)
  util.Run('xvmol2ja' + ' >> ' + gradlogfile,s)
  util.Run('xvscf' + ' >> ' + gradlogfile,s)
  util.Run('xvtran' + ' >> ' + gradlogfile,s)
  util.Run('xintprc' + ' >> ' + gradlogfile,s)
  util.Run('xvcc' + ' >> ' + gradlogfile,s)
  util.Run('xlambda' + ' >> ' + gradlogfile,s)
  util.Run('xdens' + ' >> ' + gradlogfile,s)
  util.Run('xanti' + ' >> ' + gradlogfile,s)
  util.Run('xbcktrn' + ' >> ' + gradlogfile,s)
  util.Run('xvdint' + ' >> ' + gradlogfile,s)
  # run job while watching exit status 
  util.Run('xaces2' + ' > ' + logfile,s)
  # check for normal termination and spin contamination
  if normal_termination(logfile,s):
    print '    aces2 analytic frequency ' + size + ': completed successfully'
# temporarily leaving out spin contamination testing
#    contaminated = testspin(s.AI_Spin,logfile,s)
#    if contaminated:
#      util.DieError('SpinError','Correlated wavefunction is spin contaminated',s)
  else:
    util.DieError(method,'Analytic frequency calculation failed',s)

  # get the energy data from the gradient calculation log file
  fc = util.grab_contents(gradlogfile,s)
  energy=''
  for line in range(0,len(fc)):
    if string.find(fc[line],'    energy') !=-1:
      energy = fc[line].split()[3] + '\n'

  # get the coordinates (in bohr) and gradient data from the 'GRD' file
  fc = util.grab_contents('GRD',s)
  geom= ''
  grad= ''
  natom=fc[0].split()[0]
  natom=int(natom)
  for line in range(1,natom+1):
    geom += fc[line].split()[1] + '  ' + fc[line].split()[2] + '  ' + fc[line].split()[3] + '\n'
  for line in range(natom+1,2*natom+1):
    grad += fc[line].split()[1] + '  ' + fc[line].split()[2] + '  ' + fc[line].split()[3] + '\n'
  natom3=3*natom

  # get the second derivative information
  fc = util.grab_contents('FCM',s)
  ForceConst=[]
  freq= '' 
  for line in range(1,len(fc)):
    ForceConst += fc[line].split()
  for i in range(0,natom3):
    for j in range(0,i+1):
      freq += ForceConst[i*(natom3)+j] + '\n'

  # write the derivative information to a file for bfinvert to read
  dat=file('freq.dat','w')
  dat.writelines(geom)
  dat.writelines(energy)
  dat.writelines(grad)
  dat.writelines(freq)
  dat.close()
 

#==========================================================================
# munge the results of a frequency calc to produce POT data
#==========================================================================
def add_to_POT(s):
  print '    aces2_add_to_POT'
  # cleanup in advance
  util.Rmf('POT.temp')
  f = file('POT.temp','w')
  f.write(' --- data point #' + str(s.NumData) + '\n')
  f.close
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
def build_comfile(command_string,header_string,size,s):
  ' Function to build the kth gaussian com file '
  # build the command file as a list of strings
  command = []
  # add the title line
  command.append(header_string)
  # add a blank line
  command.append('\n')
  # read in the coordinates from file cdata_bohr
  fc = util.grab_contents('cdata_bohr',s)
  # append the coordinates to the comfile sequence
  for line in fc:
     command.append(line)
  # add the command string for this job (actual string, not a pointer)
  command.append(command_string)
  # name the comfile (must be called ZMAT), and remove any old versions
  target = 'ZMAT'
  util.Rmf(target)
  # write the new comfile
  f = file(target,'w')
  f.writelines(command)
  f.close()
  # return the name of the comfile
  return target

#==========================================================================
# utility function used to see if aces2 did its thang
#==========================================================================
def normal_termination(logfile,s):
  ' utility function used to see if aces2 did its thang '
  # read in the contents of the logfile
  fc = util.grab_contents(logfile,s)
  # set return flag to 0
  success=0
  for line in fc:
    if (string.find(line,'The ACES2 program has completed successfully') != -1):
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
  # now look for S**2
  S2=-1
  for line in fc:
    if (string.find(line,' annihilation ') != -1):
      S2 = float(string.split(line)[3][:-1])  # removing trailing comma
  # compare 
  if ( abs(M-S2) < 0.1 ):
    success = 1
  else:
    success = 0
  return success


#==========================================================================
# utility function to grab coordinates from an aces2 log file
#==========================================================================
def coords_from_logfile(fname,s):
  ' grab all the coordinates from a log file '
  fc = util.grab_contents(fname,s)
  # look for the 'standard orientation'
  coords=[]
  for line in range(0,len(fc)):
    geom=[]
    if string.find(fc[line],'Cartesian coordinates corresponding') != -1:
      line+=6
      while fc[line][0:3] != ' --':
        x = fc[line].split()
	atom = ' ' + x[0] + ', ' + x[2] + ', ' + x[3] + ', ' + x[4] + ' \n'
	geom.append(atom)
        line+=1
      coords.append(geom)
  return coords



