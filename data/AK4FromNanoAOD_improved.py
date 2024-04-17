import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.run3scouting_cff import *
from FWCore.ParameterSet.VarParsing import VarParsing
from splitter import get_file_and_parents

params = VarParsing('analysis')

params.register('fileNum',
		0,
    		VarParsing.multiplicity.singleton,
    		VarParsing.varType.int,
   		 "file number in list of files"

params.register('inputTextFile',
		'',
    		VarParsing.multiplicity.singleton,
    		VarParsing.varType.string,
   		"Input text file of files"
)

process = cms.Process("LL")
params.parseArguments()

process.load("PhysicsTools.NanoAOD.run3scouting_cff")
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 5000

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(10))
process.source = cms.Source("PoolSource",
	fileNames = cms.untracked.vstring(file_name),
        secondaryFileNames = cms.untracked.vstring(*parent_files)
)
process.TFileService = cms.Service("TFileService",
    fileName = cms.string('/cms/nla49/Scouting/CMSSW_13_1_0_pre2/src/Run3ScoutingJetTagging/Analysis/test/data_ntuples/ntuple_' + str(params.fileName) + '.root')
)


# Create scouting jets
process.scoutingPFCands = scoutingPFCands.clone(CHS=cms.bool(True))
process.ak4JetTask = cms.Task(process.ak4ScoutingJets)

# Create SoftDrop pruned GEN jets
process.load('PhysicsTools.NanoAOD.jetMC_cff')
process.genJetSequence = cms.Sequence(
   process.patJetPartonsNano+
   process.genJetFlavourAssociation
)

# Create ParticleNet ntuple
process.tree = cms.EDAnalyzer("AK4JetFromNanoAODNtupleProducer",
      isQCD = cms.untracked.bool(False),
      gen_jets = cms.InputTag( "genJetFlavourAssociation" ),
      pf_candidates = cms.InputTag( "scoutingPFCands" ),
      jets = cms.InputTag( "ak4ScoutingJets" ),
      normchi2_value_map = cms.InputTag("scoutingPFCands", "normchi2"),
      dz_value_map = cms.InputTag("scoutingPFCands", "dz"),
      dxy_value_map = cms.InputTag("scoutingPFCands", "dxy"),
      dzsig_value_map = cms.InputTag("scoutingPFCands", "dzsig"),
      dxysig_value_map = cms.InputTag("scoutingPFCands", "dxysig"),
      lostInnerHits_value_map = cms.InputTag("scoutingPFCands", "lostInnerHits"),
      quality_value_map = cms.InputTag("scoutingPFCands", "quality"),
      trkPt_value_map = cms.InputTag("scoutingPFCands", "trkPt"),
      trkEta_value_map = cms.InputTag("scoutingPFCands", "trkEta"),
      trkPhi_value_map = cms.InputTag("scoutingPFCands", "trkPhi"),
      msd_value_map = cms.InputTag("ak8ScoutingJetsSoftDropMass"),
      n2b1_value_map = cms.InputTag("ak8ScoutingJetEcfNbeta1:ecfN2"),
)

process.nanoSequenceScouting = cms.Sequence(cms.Task(process.scoutingPFCands,process.ak4JetTask))

process.p = cms.Path(process.nanoSequenceScouting*process.genJetSequence*process.tree)
