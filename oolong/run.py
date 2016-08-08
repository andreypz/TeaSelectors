#!/usr/bin/env python
from ROOT import *
import os,json

import argparse
parser =  argparse.ArgumentParser(description='Ploting my plots', usage="./run.py -r RUN")
parser.add_argument("-r",  dest="RUNS", type=int, nargs='+', help="Run Numbers to process")
parser.add_argument("--proof",  dest="proof", action="store_true", default=False,  help="Run this thing with PROOF!")
parser.add_argument("--all", dest="all", action="store_true", default=False, help="Run over all!")
parser.add_argument("--june", dest="june", action="store_true", default=False, help="Run over June's Data.")

opt = parser.parse_args()
#print opt

workingPath = os.getcwd()
#workingPath = '/afs/cern.ch/user/a/andrey/work/hgcal-tb/TeaSelectors/oolong/'

if opt.june:
    pp1 = workingPath+'/June2016_v2/'
    pp2 = "root://eoscms//eos/cms/store/group/upgrade/HGCAL/TimingTB_H2_Apr2016/June2016/recoTrees_v2/"
    jsonpath1 = workingPath+'/RunSummaryTB_June2016.json'
    jsonpath2 = workingPath+'/SiPadsConfig_June2016TB_v1.json'
else:
    pp1 = workingPath+'/April2016_v3/'
    pp2 = "root://eoscms//eos/cms/store/group/upgrade/HGCAL/TimingTB_H2_Apr2016/April2016/recoTrees_v3/"
    jsonpath1 = workingPath+'/RunSummaryTB_April2016.json'
    jsonpath2 = workingPath+'/SiPadsConfig_April2016TB_v1.json'


fChain = TChain("H4treeReco");

if opt.all:
    with open(jsonpath1, 'r') as fp:
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
        print 'Loading EOS file, for run', r 
        fChain.Add("%s/RECO_%i.root" % (pp2,r));
    
timer = TStopwatch()
timer.Start()

if opt.proof:
    gSystem.SetBuildDir("buildDir", kTRUE)
    gSystem.AddIncludePath(" -I"+workingPath+"/../sugar-n-milk/");
    plite = TProof.Open("workers=6")
    plite.Load(workingPath+"/buildDir/HistManager_cc.so")
    #plite.Load(workingPath+"/../sugar-n-milk/HistManager.cc+")
    fChain.SetProof()
    fChain.Process("myAna.C+",'%s %s' % (jsonpath1,jsonpath2))   
    fChain.SetProof(0)
    
else:
    gSystem.SetBuildDir("buildDir", kTRUE)
    gSystem.AddIncludePath(" -I"+workingPath+"/../sugar-n-milk/");
    #gSystem.Load("HistManager_cc.so")
    gROOT.LoadMacro("../sugar-n-milk/HistManager.cc+")
    fChain.Process("myAna.C+", '%s %s' % (jsonpath1,jsonpath2))

print "Done!", "CPU Time: ", timer.CpuTime(), "RealTime : ", timer.RealTime()
