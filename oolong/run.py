#!/usr/bin/env python
from ROOT import *
#gROOT.SetMacroPath(".:../src/:../interface/");
import os,json

import argparse
parser =  argparse.ArgumentParser(description='Ploting my plots', usage="./run.py -r RUN")
parser.add_argument("-r",  dest="RUNS", type=int, nargs='+', help="Run Numbers to process")
parser.add_argument("--proof",  dest="proof", action="store_true", default=False,  help="Run this thing with PROOF!")
parser.add_argument("--all", dest="all", action="store_true", default=False, help="Run over all!")
parser.add_argument("--june", dest="june", action="store_true", default=False, help="Run over June's Data.")

opt = parser.parse_args()
#print opt
if opt.june:
    pp1 = '/afs/cern.ch/user/a/andrey/work/hgcal-tb/tb-ana/June2016_v2/'
    pp2 = "root://eoscms//eos/cms/store/group/upgrade/HGCAL/TimingTB_H2_Apr2016/June2016/recoTrees_v2/"
    jsonpath = '/afs/cern.ch/user/a/andrey/work/hgcal-tb/tb-ana/RunSummaryTB_June2016.json'
else:
    pp1 = '/afs/cern.ch/user/a/andrey/work/hgcal-tb/tb-ana/April2016_v3/'
    pp2 = "root://eoscms//eos/cms/store/group/upgrade/HGCAL/TimingTB_H2_Apr2016/April2016/recoTrees_v3/"
    jsonpath = '/afs/cern.ch/user/a/andrey/work/hgcal-tb/tb-ana/RunSummaryTB_April2016.json'


gSystem.Load("HistManager_cc.so")
#gROOT.LoadMacro("HistManager.cc+")

fChain = TChain("H4treeReco");

if opt.all:
    with open(jsonpath, 'r') as fp:
        TB_DATA = json.load(fp)        
    myRUNS = [int(i) for i in TB_DATA.keys()]
else:
    myRUNS = opt.RUNS

#print 'Runs in the chain:', myRUNS
for r in myRUNS:
    # print 'Adding the file for run=',r
    localFile =  '%s/RECO_%i.root'%(pp1,r)
    if os.path.exists(localFile):
        print 'Loading Local file, for run', r 
        fChain.Add(localFile);
    else:
        print 'EOS file, run', r 
        fChain.Add("%s/RECO_%i.root" % (pp2,r));
    
timer = TStopwatch()
timer.Start()

if opt.proof:
    plite = TProof.Open("workers=6")
    plite.Load("HistManager.cc+")
    fChain.SetProof()
    fChain.Process("myAna.C+", jsonpath)   
    fChain.SetProof(0)
    
else: 
    fChain.Process("myAna.C+", jsonpath)

print "Done!", "CPU Time: ", timer.CpuTime(), "RealTime : ", timer.RealTime()
