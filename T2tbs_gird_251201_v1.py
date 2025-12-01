# ref
# frag: https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_fragment/SUS-Run3Summer22EEFSGenPremix-00012/0
# MCM:  https://cms-pdmv-prod.web.cern.ch/mcm/requests?page=0&dataset_name=SMS-2Stop_mStop-1000_TuneCP5_13p6TeV_madgraph-pythia8

import FWCore.ParameterSet.Config as cms

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunesRun3ECM13p6TeV.PythiaCP5Settings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *

import math

mstop = 1000

externalLHEProducer = cms.EDProducer("ExternalLHEProducer",  # Load external LHE events via gridpack
    args = cms.vstring('/cvmfs/cms-griddata.cern.ch/phys_generator/gridpacks_tarball/pp/13p6TeV/madgraph/SMS-StopStop/SMS-StopStop_mStop-%i_slc7_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz' % mstop),
    nEvents = cms.untracked.uint32(20),  # Number of events to generate from the gridpack
    numberOfParameters = cms.uint32(1),  # Only one argument (gridpack path)
    outputFile = cms.string('cmsgrid_final.lhe'),  # Output LHE file name
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')  # Standard gridpack execution script
)

baseSLHATable="""
BLOCK MASS  # Mass Spectrum
# PDG code           mass       particle
   1000001     1.00000000E+05   # ~d_L
   2000001     1.00000000E+05   # ~d_R
   1000002     1.00000000E+05   # ~u_L
   2000002     1.00000000E+05   # ~u_R
   1000003     1.00000000E+05   # ~s_L
   2000003     1.00000000E+05   # ~s_R
   1000004     1.00000000E+05   # ~c_L
   2000004     1.00000000E+05   # ~c_R
   1000005     1.00000000E+05   # ~b_1
   2000005     1.00000000E+05   # ~b_2
   1000006     %MSTOP%   # ~t_1
   2000006     1.00000000E+05   # ~t_2
   1000011     1.00000000E+05   # ~e_L
   2000011     1.00000000E+05   # ~e_R
   1000012     1.00000000E+05   # ~nu_eL
   1000013     1.00000000E+05   # ~mu_L
   2000013     1.00000000E+05   # ~mu_R
   1000014     1.00000000E+05   # ~nu_muL
   1000015     1.00000000E+05   # ~tau_1
   2000015     1.00000000E+05   # ~tau_2
   1000016     1.00000000E+05   # ~nu_tauL
   1000021     2.00000000E+03   # ~g
   1000022     5.00000000E+02   # ~chi_10
   1000023     1.00000000E+05   # ~chi_20
   1000025     1.00000000E+05   # ~chi_30
   1000035     1.00000000E+05   # ~chi_40
   1000024     5.00000000E+02   # ~chi_1+
   1000037     1.00000000E+05   # ~chi_2+

# DECAY TABLE
#          PDG            Width
DECAY   1000001     0.00000000E+00   # sdown_L decays
DECAY   2000001     0.00000000E+00   # sdown_R decays
DECAY   1000002     0.00000000E+00   # sup_L decays
DECAY   2000002     0.00000000E+00   # sup_R decays
DECAY   1000003     0.00000000E+00   # sstrange_L decays
DECAY   2000003     0.00000000E+00   # sstrange_R decays
DECAY   1000004     0.00000000E+00   # scharm_L decays
DECAY   2000004     0.00000000E+00   # scharm_R decays
DECAY   1000005     0.00000000E+00   # sbottom1 decays
DECAY   1000006     1.0000000E+00    # stop1 decays
5.00000000E-01    2        6       1000022   # ~t_1 -> t + ~chi_10
5.00000000E-01    2        5       1000024   # ~t_1 -> b + ~chi_1+
DECAY   2000005     0.00000000E+00   # sbottom2 decays
DECAY   2000006     0.00000000E+00   # stop2 decays

DECAY   1000011     0.00000000E+00   # selectron_L decays
DECAY   2000011     0.00000000E+00   # selectron_R decays
DECAY   1000012     0.00000000E+00   # snu_elL decays
DECAY   1000013     0.00000000E+00   # smuon_L decays
DECAY   2000013     0.00000000E+00   # smuon_R decays
DECAY   1000014     0.00000000E+00   # snu_muL decays
DECAY   1000015     0.00000000E+00   # stau_1 decays
DECAY   2000015     0.00000000E+00   # stau_2 decays
DECAY   1000016     0.00000000E+00   # snu_tauL decays
DECAY   1000021     0.00000000E+00   # gluino decays
DECAY   1000022     1.00000000E+00   # neutralino1 decays
1.00000000E+00    3        6          3         5    # ~chi_10 -> t + s + b
DECAY   1000023     0.00000000E+00   # neutralino2 decays
DECAY   1000024     1.00000000E+00   # chargino1+ decays
1.00000000E+00    3       -3         -g         -5    # ~chi_1+ -> ~s + ~b + ~b
DECAY   1000025     0.00000000E+00   # neutralino3 decays
DECAY   1000035     0.00000000E+00   # neutralino4 decays
DECAY   1000037     0.00000000E+00   # chargino2+ decays
"""

model = "T2tt"
batch = 1
mcm_eff = 0.248

def matchParams(mass):
  if mass < 649: return 62., 0.274
  elif mass < 699: return 64., 0.269
  elif mass < 749: return 64., 0.269
  elif mass < 799: return 66., 0.259
  elif mass < 849: return 66., 0.261
  elif mass < 899: return 68., 0.257
  elif mass < 949: return 68., 0.252
  elif mass < 999: return 70., 0.250
  elif mass < 1049: return 70., 0.248
  elif mass < 1099: return 70., 0.248
  elif mass < 1149: return 70., 0.249
  elif mass < 1199: return 70., 0.242
  elif mass < 1249: return 70., 0.239
  elif mass < 1299: return 70., 0.242
  elif mass < 1349: return 70., 0.241
  elif mass < 1399: return 70., 0.237
  elif mass < 1449: return 70., 0.239
  elif mass < 1499: return 70., 0.241
  elif mass < 1549: return 70., 0.235
  elif mass < 1599: return 70., 0.239
  elif mass < 1649: return 70., 0.239
  elif mass < 1699: return 70., 0.237
  elif mass < 1749: return 70., 0.241
  elif mass < 1799: return 70., 0.237
  elif mass < 1849: return 70., 0.237
  elif mass < 1899: return 70., 0.240
  elif mass < 1949: return 70., 0.241
  elif mass < 1999: return 70., 0.244
  elif mass < 2049: return 70., 0.246
  elif mass < 2099: return 70., 0.249
  elif mass < 2149: return 70., 0.246
  elif mass < 2199: return 70., 0.246
  elif mass < 2249: return 70., 0.251
  elif mass < 2299: return 70., 0.249
  elif mass < 2349: return 70., 0.257
  elif mass < 2399: return 70., 0.257
  elif mass < 2449: return 70., 0.261
  elif mass < 2499: return 70., 0.264
  elif mass < 2549: return 70., 0.266
  ### Just for testing
  else: return 70., 0.243

def xsec(mass):
  if mass < 300: return 319925471928717.38*math.pow(mass, -4.10396285974583*math.exp(mass*0.0001317804474363))
  else: return 4855957031250000*math.pow(mass, -4.71716128867804*math.exp(mass*6.175277146619076e-05))

qcut, eff = matchParams(mstop)
baseSLHA = baseSLHATable.replace('%MSTOP%', '%e' % mstop)  # Replace gluino mass in SLHA

generator = cms.EDFilter("Pythia8ConcurrentHadronizerFilter",  # Run3-compatible Pythia8 hadronizer
  maxEventsToPrint = cms.untracked.int32(1),  # Print 1 event
  pythiaPylistVerbosity = cms.untracked.int32(1),  # Print Pythia event info
  filterEfficiency = cms.untracked.double(1.0),  # Matching efficiency
  pythiaHepMCVerbosity = cms.untracked.bool(False),
  comEnergy = cms.double(13600.),  # Run3 center-of-mass energy: 13.6 TeV
  PythiaParameters = cms.PSet(
    pythia8CommonSettingsBlock,  # Common settings
    pythia8CP5SettingsBlock,  # Run3 CP5 tune
    JetMatchingParameters = cms.vstring(  # MLM jet-parton matching
      'JetMatching:setMad = off',
      'JetMatching:scheme = 1',
      'JetMatching:merge = on',
      'JetMatching:jetAlgorithm = 2',
      'JetMatching:etaJetMax = 5.',
      'JetMatching:coneRadius = 1.',
      'JetMatching:slowJetPower = 1',
      'JetMatching:qCut = %e' % qcut,  # Merging scale
      'JetMatching:nQmatch = 5',  # 5-flavor scheme (matching includes b-quarks)
      'JetMatching:nJetMax = 2',  # Number of partons in ME
      'JetMatching:doShowerKt = off'
    ),
    parameterSets = cms.vstring('pythia8CommonSettings',
                                'pythia8CP5Settings',
                                'JetMatchingParameters')
  ),
  SLHATableForPythia8 = cms.string(baseSLHA)  # Inject SLHA block
)
~
