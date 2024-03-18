weaver --data-train /cms/nla49/ScoutingAgain/CMSSW_13_1_0_pre2/src/Run3ScoutingJetTagging/Training/AK4/flavour/test.root \
 --data-config /cms/nla49/ScoutingAgain/CMSSW_13_1_0_pre2/src/Run3ScoutingJetTagging/Training/AK4/flavour/data/flavour_test.yaml \
 --network-config /cms/nla49/ScoutingAgain/CMSSW_13_1_0_pre2/src/Run3ScoutingJetTagging/Training/AK4/flavour/networks/flavour.py \
 --model-prefix 'output/ak4_flavour_{auto}/net' \
 --gpus 0,1 --batch-size 512 --start-lr 5e-3 --num-epochs 1 --optimizer ranger \
 --log logs/train.log

