#!/bin/bash
START_TIME=$(date +%s)

# Usage: ./test.sh <nEvents> <mGluino> <jobID> <ctau>
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
  echo "Usage: $0 <nEvents> <mGluino> <jobID> <ctau>"
  exit 1
fi

NEVT=$1
MGLU=$2
JOBID=$3
CTAU=$4
SEED=$((JOBID + CTAU))

mkdir -p ctau_AOD_logs/MGLU${MGLU}/ctau${CTAU}/

bash make_frag_file.sh $NEVT $MGLU $CTAU

FRAGNAME=SMS-T1tbs_RPV_Neve${NEVT}_mGluino${MGLU}_ctau${CTAU}_Run3-fragment.py
FRAGPATH=/afs/cern.ch/user/c/changi/Configuration/GenProduction/python/$FRAGNAME

DIGI_PU_INPUT="/store/mc/Run3Summer21PrePremix/Neutrino_E-10_gun/PREMIX/Summer23_130X_mcRun3_2023_realistic_v13-v1/50001/f0088073-96de-46c0-9f21-ebd9adddb077.root"

export SCRAM_ARCH=el8_amd64_gcc11
source /cvmfs/cms.cern.ch/cmsset_default.sh
cmsrel CMSSW_13_0_13
cd CMSSW_13_0_13/src
eval `scramv1 runtime -sh`

mkdir -p Configuration/GenProduction/python
cp $FRAGPATH Configuration/GenProduction/python/

scram b
export PYTHONPATH=${PWD}/../..:${PYTHONPATH}

# Step 1: LHE �~F~R GEN �~F~R SIM
cmsDriver.py Configuration/GenProduction/python/SMS-T1tbs_RPV_Neve${NEVT}_mGluino${MGLU}_ctau${CTAU}_Run3-fragment.py  \
  --python_filename step1_cfg.py \
  --eventcontent RAWSIM,LHE \
  --datatier GEN-SIM,LHE \
  --fileout file:LHE-GEN-SIM_job${JOBID}.root \
  --conditions 130X_mcRun3_2023_realistic_v14 \
  --beamspot Realistic25ns13p6TeVEarly2023Collision \
  --step LHE,GEN,SIM \
  --geometry DB:Extended \
  --era Run3 \
  --mc --no_exec -n $NEVT \
  --customise_commands "process.RandomNumberGeneratorService.externalLHEProducer.initialSeed = ${SEED}"

cmsRun step1_cfg.py

# Step 2: DIGI + HLT with Pileup
cmsDriver.py --python_filename step2_cfg.py \
  --eventcontent PREMIXRAW \
  --datatier GEN-SIM-RAW \
  --fileout file:DIGI-PU_job${JOBID}.root \
  --pileup_input "dbs:/Neutrino_E-10_gun/Run3Summer21PrePremix-Summer23_130X_mcRun3_2023_realistic_v13-v1/PREMIX" \
  --conditions 130X_mcRun3_2023_realistic_v14 \
  --step DIGI,DATAMIX,L1,DIGI2RAW,HLT:2023v12 \
  --procModifiers premix_stage2 \
  --geometry DB:Extended \
  --filein file:LHE-GEN-SIM_job${JOBID}.root \
  --datamix PreMix \
  --era Run3 \
  --runUnscheduled \
  --customise_commands "process.source.inputCommands = cms.untracked.vstring( \
    'keep *', \
    'drop *_kt4GenJets_*_*', \
    'drop *_kt6GenJets_*_*', \
    'drop *_iterativeCone5GenJets_*_*', \
    'drop *_ak4GenJets_*_*', \
    'drop *_ak7GenJets_*_*', \
    'drop *_ak8GenJets_*_*', \
    'drop *_ak4GenJetsNoNu_*_*', \
    'drop *_ak8GenJetsNoNu_*_*', \
    'drop *_genCandidatesForMET_*_*', \
    'drop *_genMetCalo_*_*', \
    'drop *_genMetCaloAndNonPrompt_*_*', \
    'drop *_genMetTrue_*_*', \
g   'drop *_genMetIC5GenJs_*_*')" \
  --no_exec --mc -n -1

sed -i '/process.mixData.input.fileNames =/c\process.mixData.input.fileNames = cms.untracked.vstring(["'"$DIGI_PU_INPUT"'"])' step2_cfg.py

cmsRun step2_cfg.py

# Step 3: AOD
cmsDriver.py step3 \
  --python_filename step3_cfg.py \
  --eventcontent AODSIM \
  --datatier AODSIM \
  --filein file:DIGI-PU_job${JOBID}.root \
  --fileout file:test_step2_AODSIM_job${JOBID}.root \
  --conditions 130X_mcRun3_2023_realistic_v14 \
  --step RAW2DIGI,L1Reco,RECO,RECOSIM \
  --geometry DB:Extended \
  --era Run3 --mc --no_exec -n -1

cmsRun step3_cfg.py

mkdir -p /eos/project/c/changi-rpv/vertex_nEv100/MGLU${MGLU}/ctau${CTAU}/
cp test_step2_AODSIM_job${JOBID}.root step2_cfg.py /eos/project/c/changi-rpv/vertex_nEv100/MGLU${MGLU}/ctau${CTAU}/

# mkdir -p /eos/project/c/changi-rpv/vertex_nEv100/logs/MGLU${MGLU}/

# mv /afs/cern.ch/user/c/changi/ctau_AOD_logs/MGLU${MGLU}/ctau${CTAU}/ /eos/project/c/changi-rpv/vertex_nEv100/logs/MGLU${MGLU}/

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
echo "Total time elapsed: $(($ELAPSED / 60)) min $(($ELAPSED % 60)) sec"
