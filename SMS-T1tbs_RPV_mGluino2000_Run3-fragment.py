import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunesRun3ECM13p6TeV.PythiaCP5Settings_cfi import *
import math

mglu = 2000

externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring('/cvmfs/cms.cern.ch/phys_generator/gridpacks/RunIII/13p6TeV/slc7_amd64_gcc10/MadGraph5_aMCatNLO/SUSY_SMS/SMS-GlGl/SMS-GlGl_mGl-%i_slc7_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz' % mglu),
    nEvents = cms.untracked.uint32(100),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)

baseSLHATable = """
BLOCK MODSEL
    1    0   # Model
BLOCK MASS
        25     1.00000000E+03
        6      1.72500000E+02
   1000021     %MGLU%
# ... 이하 생략된 MASS 항목은 동일하게 유지 ...
DECAY   1000021     1.0000000E+00
     1.00000000E+00    3       6         5     3     # ~g -> t b s
"""

model = "T1tbs"
mcm_eff = 0.235

def xsec(mass):
    return 4.563e+17 * math.pow(mass, -4.761 * math.exp(5.848e-05 * mass))

def matchParams(mass):
    if   mass < 799: return 118., 0.235
    elif mass < 999: return 128., 0.235
    elif mass < 1199: return 140., 0.235
    elif mass < 1399: return 143., 0.245
    elif mass < 1499: return 147., 0.255
    elif mass < 1799: return 150., 0.267
    elif mass < 2099: return 156., 0.290
    else: return 160., 0.315

qcut, matcheff = matchParams(mglu)
baseSLHA = baseSLHATable.replace('%MGLU%', '%e' % mglu)

generator = cms.EDFilter("Pythia8ConcurrentHadronizerFilter",
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1.0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(13600.),
    SLHATableForPythia8 = cms.string(baseSLHA),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        JetMatchingParameters = cms.vstring(
            'JetMatching:setMad = off',
            'JetMatching:scheme = 1',
            'JetMatching:merge = on',
            'JetMatching:jetAlgorithm = 2',
            'JetMatching:etaJetMax = 5.',
            'JetMatching:coneRadius = 1.',
            'JetMatching:slowJetPower = 1',
            'JetMatching:qCut = %e' % qcut,
            'JetMatching:nQmatch = 5',
            'JetMatching:nJetMax = 2',
            'JetMatching:doShowerKt = off'
        ),
        parameterSets = cms.vstring(
            'pythia8CommonSettings',
            'pythia8CP5Settings',
            'JetMatchingParameters'
        )
    )
)

# ✅ generatorSmeared alias for HepMCProduct
generatorSmeared = cms.EDAlias(
    generator = cms.VPSet(
        cms.PSet(type = cms.string('HepMCProduct'))
    )
)
