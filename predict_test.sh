#!/bin/bash

weaver \
	--predict \
      	--data-test "/cms/nla49/Scouting/CMSSW_13_1_0_pre2/src/Run3ScoutingJetTagging/Analysis/test/QCD_ntuples/*" \
	--data-config /cms/nla49/Scouting/CMSSW_13_1_0_pre2/src/Run3ScoutingJetTagging/Training/AK4/flavour/data/flavour.yaml \
 	--network-config /cms/nla49/Scouting/CMSSW_13_1_0_pre2/src/Run3ScoutingJetTagging/Training/AK4/flavour/networks/flavour.py \
	--model-prefix /cms/nla49/Scouting/CMSSW_13_1_0_pre2/src/Run3ScoutingJetTagging/Training/AK4/flavour/output/ak4_flavour_20240325-122350_flavour_ranger_lr0.005_batch512/net_best_epoch_state.pt \
	--gpus '0,1' --batch-size 512 \
	--predict-output ${OUTPUT}/pred.root
