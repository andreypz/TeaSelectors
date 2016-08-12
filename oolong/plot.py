#!/usr/bin/env python
import argparse
parser =  argparse.ArgumentParser(description='Ploting my plots', usage="./plot.py -f inputFileName")
parser.add_argument("-f",  dest="fname", type=str, default='TB_2016_myHistograms.root',
                    help="Filename with histograms")
parser.add_argument("-v", "--verbosity",  dest="verb", action="store_true", default=False,
                    help="Print out more stuff")
parser.add_argument("--fit",  dest="fit", action="store_true", default=False,
                    help="Perform the fits of some distributions")
parser.add_argument("--june",  dest="june", action="store_true", default=False,
                    help="Do plots for June's data (default is April)")
parser.add_argument("--mini",  dest="mini", action="store_true", default=False,
                    help="Only make a few plots for tests, not the whole thing)")
parser.add_argument("--hv",  dest="hv", nargs='+', default=['800','600'],
                    help="Specify which HV2 data we should run")
parser.add_argument("--beam",  dest="beam", nargs='+', default=['ELE','PION'],
                    help="Specify which BEAM data we should run")
parser.add_argument("--allruns",  dest="allruns", action="store_true", default=False,
                    help="Make the plots for each run (they shold be present in the input file)")

opt = parser.parse_args()
#print opt

import sys,os,json
from math import sqrt
from array import array
from ROOT import *
gROOT.SetBatch()
gROOT.ProcessLine(".L ../sugar-n-milk/tdrstyle.C")
gROOT.LoadMacro("../sugar-n-milk/CMS_lumi.C")
setTDRStyle()
gROOT.ForceStyle()
if not opt.verb:
  gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")


if opt.june:
  outDir = './Plots-TB-June/'
  jsonFile1 = './SiPadsConfig_June2016TB_v1.json'
  jsonFile2 = './RunSummaryTB_June2016.json'
else:
  outDir = './Plots-TB-April/'
  jsonFile1 = './SiPadsConfig_April2016TB_v1.json'
  jsonFile2 = './RunSummaryTB_April2016.json'

with open(jsonFile1, 'r') as fp:
  SiPad_DATA = json.load(fp)

allPads = SiPad_DATA['PADSMAP1']

with open(jsonFile2, 'r') as fp:
  TB_DATA = json.load(fp)

PadsCol = {"SiPad1":1, "SiPad2":47, "SiPad3":8, "SiPad4":9, "SiPad5":41, "SiPad6":46}

c1 = TCanvas("c1","small canvas",600,600);
c2 = TCanvas("c2","small canvas",800,600);


def createDir(myDir):
  if opt.verb: print 'Creating a new directory: ', myDir
  if not os.path.exists(myDir):
    try: os.makedirs(myDir)
    except OSError:
      if os.path.isdir(myDir): pass
      else: raise
  else:
    if opt.verb: print "\t OOps, it already exists"

def handleOverflowBins(hist):
  if hist == None:
    return
  nBins   = hist.GetNbinsX()
  lastBin = hist.GetBinContent(nBins)
  ovflBin = hist.GetBinContent(nBins+1);
  lastBinErr = hist.GetBinError(nBins);
  ovflBinErr = hist.GetBinError(nBins+1);
  firstBin    = hist.GetBinContent(1);
  undflBin    = hist.GetBinContent(0);
  firstBinErr = hist.GetBinError(1);
  undflBinErr = hist.GetBinError(0);
  hist.SetBinError(nBins, sqrt(pow(lastBinErr,2) + pow(ovflBinErr,2)) );
  hist.SetBinContent(1, firstBin+undflBin);
  hist.SetBinError(1, sqrt(pow(firstBinErr,2) + pow(undflBinErr,2)) );
  hist.SetBinContent(0,0);
  hist.SetBinContent(nBins+1,0);


def justPlotAll(myF, inThisDir='Main'):
  if opt.verb: print 'myDir is =', inThisDir
  isDir = None
  if myF!=None and not myF.IsZombie():
    isDir = myF.cd(inThisDir)
    if not isDir: return
  else:
    print "\t Sorry can't draw anything, no files are provided!"
    return

  dirList = gDirectory.GetListOfKeys()
  # dirList.Print()

  path = outDir+inThisDir
  createDir(path)

  c0=c1
  c0.cd()


  histoName = None
  for k in dirList:
    # print '\t Item in the dir: ', k
    mainHist = k.ReadObj()
    histoName = mainHist.GetName()

    if inThisDir!="":
      h1 = myF.Get(inThisDir+"/"+histoName)
    else:
      h1 = myF.Get(histoName)

    handleOverflowBins(h1)

    hmin=0
    hmax=h1.GetMaximum()
    if 'WC_dx' in histoName:
      hmin = -5
      hmax = -1
    if 'WC_dy' in histoName:
      hmin = -3
      hmax = 1
    h1.SetMinimum(hmin)
    h1.SetMaximum(hmax)

    if h1.InheritsFrom("TH2"):
      h1.Draw("col")
    else:
      h1.Draw('e1')

    c0.SaveAs(path+"/"+histoName+'.png')


def onePerTag(myF, hName, tag):
  if opt.verb: print "\t Making plots for ->", hName
  c0=c1
  c0.cd()
  newName = hName+tag

  try:
    h1 = myF.Get(newName).Clone()
  except ReferenceError:
    return

  handleOverflowBins(h1)

  if h1.InheritsFrom("TH2"):
    h1.Draw("col")
  else:
    h1.Draw('e1')

  h1.SetMinimum(0)
  path = outDir+'onePerTag'+tag
  createDir(path)
  split = os.path.split(hName.rstrip("/"))
  c0.SaveAs(path+"/"+split[1]+'.png')

def allPadsOnOnePlot(myF, hName, tag, fit=False, overHists=None):
  # print "\t Making plots for ->", hName


  isThisWaveform = 'Waveform' in hName
  isBadSet = ('N200' in tag and not opt.june)

  if 'PER-RUN' in hName: c0 = c2
  else: c0=c1
  c0.cd()


  h = {}
  hmaxima=[]
  for p, ch in allPads.iteritems():
    suffix = '_'+p+'_ch'+str(ch)
    #print 'pad', p,  suffix
    newName = hName+suffix+tag
    try:
      h[p]=(myF.Get(newName).Clone())
    except ReferenceError:
      if p=='SiPad1' or (p=='SiPad2' and isBadSet):
        if opt.verb: print '\t Well, this is the front pad Just skip it:', p
        continue
      else:
        print 'Looks like this hist does not exist:', newName
        print '\t *** --> This is no good.. <-- ***'
        return

    h[p].SetLineColor(PadsCol[p])
    h[p].SetLineWidth(2)
    norm = h[p].Integral()
    if norm!=0 and not h[p].InheritsFrom('TProfile'):
      h[p].Scale(1./norm)
    if not (p=='SiPad2' and isBadSet):
      hmaxima.append(h[p].GetMaximum())

  if h['SiPad3'].InheritsFrom('TProfile'):
    drawOpt = 'e1'
  else:
    drawOpt = 'hist'


  hmin = 0
  hmax = 1.1*max(hmaxima)
  #print hmaxima, hmax

  if isThisWaveform:
    hmin = -0.1
    hmax = 1.1
  if 'Pedestal_PerRun' in hName:
    if opt.june:
      hmin = 3600
      hmax = 3800
    else:
      hmin = 100
      hmax = 300
  if 'PedestalRMS_PerRun' in hName:
    hmax = 50

  leg = TLegend(0.75,0.72,0.92,0.90)

  h['SiPad3'].Draw(drawOpt)
  h['SiPad3'].SetMinimum(hmin)
  h['SiPad3'].SetMaximum(hmax)
  if not isBadSet: # Because in set2 this Pad is bad...
    h["SiPad2"].Draw(drawOpt+' sames')
  h["SiPad4"].Draw(drawOpt+' sames')
  h["SiPad5"].Draw(drawOpt+' sames')
  h["SiPad6"].Draw(drawOpt+' sames')

  try:
    h["SiPad1"].Draw(drawOpt+' sames')
    leg.AddEntry(h["SiPad1"],"SiPad1", "l")
  except:
    if opt.verb: print 'do nothing'

  #c0.Update()
  #gStyle.SetOptStat(1111)
  #gStyle.SetOptFit(1)
  if fit:
    n=0
    print 'Doing gauss fits for:', h
    for p,hi in sorted(h.iteritems()):
      if p=='SiPad2' and isBadSet: continue
      print p, hi
      m = hi.GetMean()
      r = hi.GetRMS()
      hi.Fit('gaus','Q','', m-3*r, m+3*r)
      f = hi.GetFunction('gaus')
      f.SetLineColor(PadsCol[p])
      f.SetLineStyle(kDashed)
      f.Draw('same')
      gPad.Update()
      #print pa, hi.GetListOfFunctions().FindObject("stats")
      st = hi.GetListOfFunctions().FindObject("stats")
      #l = st.GetListOfLines()
      #l.Remove(st.GetLineWith('Mean'))
      #l.Remove(st.GetLineWith('RMS'))
      #l.Remove(st.GetLineWith('Constant'))
      ##l.Remove(st.GetLineWith('Constant'))
      #l.Print()
      #raw_input()
      #st.SetName(pa)
      st.SetY1NDC(0.70-0.115*n)# //new y start position
      st.SetY2NDC(0.60-0.115*n)# //new y end position
      st.SetLineColor(PadsCol[p])
      n+=1

  if not isBadSet:
    leg.AddEntry(h["SiPad2"],"SiPad2", "l")
  leg.AddEntry(h['SiPad3'],"SiPad3", "l")
  leg.AddEntry(h['SiPad4'],"SiPad4", "l")
  leg.AddEntry(h['SiPad5'],"SiPad5", "l")
  leg.AddEntry(h['SiPad6'],"SiPad6", "l")
  leg.SetFillColor(kWhite)
  leg.Draw()

  if tag=='': tag='_PerRun'
  path = outDir+'AllInOne'+tag
  createDir(path)
  split = os.path.split(hName.rstrip("/"))


  drawLabel(tag)

  if isThisWaveform:
    c0.Update()
    l1=TLine(c0.GetUxmin(), 0, c0.GetUxmax(), 0);
    l2=TLine(0, c0.GetUymin(), 0, c0.GetUymax());
    l1.SetLineColor(kBlue)
    l1.SetLineStyle(kDashed)
    l1.Draw()
    l2.SetLineColor(kBlue)
    l2.SetLineStyle(kDashed)
    l2.Draw()


  if overHists!= None:
    # This is written for 'PER-RUN' cases, where I'd like to overlay
    # shade histograms to identofy certain runs: Pedestal Runs, 300 um set, etc
    # print 'Drawing overhists!'
    ovleg = TLegend(0.55,0.72,0.7,0.90)
    for ov in overHists:
      ov.Draw('same hist')
      ov.SetLineStyle(3)
      ov.SetLineWidth(0)
      if ov.GetName()=='300': ovCol = kRed
      if ov.GetName()=='200': ovCol = kOrange
      if ov.GetName()=='120': ovCol = kCyan
      if ov.GetName()=='Ped': ovCol = kBlue
      if ov.GetName()=='Pio': ovCol = kGreen
      ov.SetFillColorAlpha(ovCol, 0.2)

      ovleg.AddEntry(ov, ov.GetName()+' Runs','f')

    # Re-drawing legend
    leg.SetX1(0.8)
    leg.SetY1(0.64)
    leg.Draw()
    ovleg.Draw()

  c0.SaveAs(path+"/"+split[1]+tag+'.png')

def drawLabel(tag):
  label = TText()
  label.SetNDC()
  label.SetTextFont(1)
  label.SetTextColor(kBlue+3)
  label.SetTextSize(0.04)
  label.SetTextAlign(1)
  if 'GROUP_0' in tag:
    if tag[9:12]=="ELE":
      label.DrawText(0.20, 0.95, '  '.join(['Beam:'+tag[9:12],tag[13:24], tag[25:]]).replace('_',':'))
    else:
      label.DrawText(0.20, 0.95, '  '.join(['Beam:'+tag[9:13],tag[14:25], tag[26:]]).replace('_',':'))

  elif 'GROUP_1' in tag:
    label.DrawText(0.15, 0.95, '  '.join(['Beam:'+tag[9:12]+', '+tag[14:20], tag[21:32], tag[33:]]).replace('_',':'))
  else:
    label.DrawText(0.05, 0.95, tag)


def sigmaPlot(myF, hName, tag, doSigmaFit=False):
  if opt.verb: print "\t Making Sigma plots for ->", hName
  isBadSet = ('N200' in tag and not opt.june)

  c0=c1
  c0.cd()

  h = {}
  karambaMe, karambaSi = {}, {}
  constTerm, noiseTerm, noiseErr, constErr = {}, {}, {}, {}
  for p, ch in allPads.iteritems():
    #suffix = p+'_ch'+str(ch)
    suffix = '_'+p+'_ch'+str(ch)
    #print 'pad', p,  suffix
    newName = hName+suffix+tag
    try:
      h[p]=(myF.Get(newName).Clone())
    except ReferenceError:
      if p=='SiPad1':
        if opt.verb: print '\t Well, this is the front pad Just skip it:', p
        continue
      else:
        print 'Looks like this hist does not exist:', newName
        print '\t *** --> This is no good.. <-- ***'
        return

    path = outDir+'Projects'+tag
    createDir(path)

    if '_VS_nMIPs' in hName:
      varBins = [0,2,3,5,7,9,11,13,15,17,19,21,23,25,27,30,35,40,45,50,60]
      xBins = [int(400*x/60)+1 for x in varBins]
      xTitle = ';Number of MiPs'
      figName = '_VS_nMIPs'
    elif '_VS_SigOverNoise' in hName:
      varBins = [2,3,5,7,9,11,13,15,17,20,22,25,28,31,35,40,50,70,140]
      xBins = [int(400*(x-2)/138)+1 for x in varBins]
      xTitle = ';Signal/Noise'
      figName = '_VS_SigOverNoise'
    elif '_VS_sOvern_Pad1X_nMiPcut' in hName:
      varBins = [2,3,5,7,9,11,13,15,17,20,22,25,28,31,35,40,50,70,140]
      xBins = [int(400*(x-2)/138)+1 for x in varBins]
      xTitle = ';Effective S/N'
      figName = '_VS_sOvern_Pad1X_nMiPcut'
    elif '_VS_sOvern_Pad1X' in hName:
      varBins = [2,3,5,7,9,11,13,15,17,20,22,25,28,31,35,40,50,70,140]
      xBins = [int(400*(x-2)/138)+1 for x in varBins]
      xTitle = ';Effective S/N'
      figName = '_VS_sOvern_Pad1X'

    # xBins are bin-numbers of the varBins (see conversion above)
    # It assumes that the total number of bins on the axis is 400.
    # print 'varBins:\n \t', varBins
    # print 'xBins:\n \t', xBins

    karambaMe[p] = TH1D('Mean'+p,xTitle+";Mean of (t_{N} - t_{1}), ns", len(varBins)-1,array('d',varBins))
    karambaSi[p] = TH1D('Sigma'+p,xTitle+";#sigma(t_{N} - t_{1}), ns",  len(varBins)-1,array('d',varBins))

    for n in range(1,len(xBins)-1):
      proj = h[p].ProjectionY("", xBins[n], xBins[n+1]-1)

      # print n,'Doing bin:', xBins[n], xBins[n+1]
      # print ' \t which correspond to varBins:\n\t', varBins[n], varBins[n+1]
      if proj.GetEntries()<60:
        if opt.verb:
          print '\t WARNING: you have too few event to fit for tag:', tag
          print '\t\t  nEvents = ',proj.GetEntries(),'  pad = '+p+'  bins:', xBins[n], xBins[n+1]
          print '\t I must continue without this point...'
        continue

      m = proj.GetMean()
      r = proj.GetRMS()
      proj.Fit('gaus','Q','', m-3*r, m+3*r)
      f = proj.GetFunction('gaus')
      fMean = f.GetParameter(1)
      fMeanErr = f.GetParError(1)
      fSigma = f.GetParameter(2)
      fSigmaErr = f.GetParError(2)

      karambaMe[p].SetBinContent(n+1,fMean)
      karambaMe[p].SetBinError(n+1,fMeanErr)
      karambaSi[p].SetBinContent(n+1,fSigma)
      karambaSi[p].SetBinError(n+1,fSigmaErr)

      karambaMe[p].SetLineColor(PadsCol[p])
      karambaMe[p].SetLineWidth(2)
      karambaSi[p].SetLineColor(PadsCol[p])
      karambaSi[p].SetLineWidth(2)
      #print '\t My Fit result for mean: ', fMean, fMeanErr
      #print '\t  \t for sigma: ', fSigma, fSigmaErr

    if doSigmaFit:
      # print 'Doing sigma fit on ', hName, tag
      # print '\t pad =',p
      c0_2 = c1
        
      # Two parameters fit

      f2 = TF1 ('f2','sqrt([0]*[0]/(x*x) + [1]*[1])', 2,140.)
      f2.SetParameters(5, 0.001, 0.05)
      f2.SetParLimits(0, 0, 5)
      f2.SetParLimits(1, 0, 0.2)

      # Three parameters fit:

      f3 = TF1 ('f3','sqrt([0]*[0]/(x*x) + [1]*[1]/x + [2]*[2])', 2.,140.)
      f3.SetParameters(5, 0.001, 0.05)
      f3.SetParLimits(0, 0, 5)
      f3.SetParLimits(1, 0, 0.1)
      f3.SetParLimits(2, 0.005, 0.2)
      
      fToUse = f2
      ConstParInd = 1
        
      karambaSi[p].Fit(fToUse,'Q','',5,70)

      karambaSi[p].Draw()
      karambaSi[p].SetMaximum(0.4)
      karambaSi[p].SetMinimum(0.0)
      fToUse.Draw("same")
      c0_2.SaveAs(path+'/SJ_fit_SOverN'+figName+"_"+p+'.png')
      # c0_2.SaveAs(path+'/SJ_fit_SOverN_'+p+'.C')

      noiseTerm[p] = fToUse.GetParameter(0)
      noiseErr[p]  = fToUse.GetParError(0)
      constTerm[p] = fToUse.GetParameter(ConstParInd)
      constErr[p]  = fToUse.GetParError(ConstParInd)


  drawOpt= 'e1p'
  karambaMe['SiPad3'].Draw(drawOpt)
  if not isBadSet:
    karambaMe['SiPad2'].Draw(drawOpt+' same')
  karambaMe['SiPad4'].Draw(drawOpt+' same')
  karambaMe['SiPad5'].Draw(drawOpt+' same')
  karambaMe['SiPad6'].Draw(drawOpt+' same')
  karambaMe['SiPad3'].SetMinimum(-0.4)
  karambaMe['SiPad3'].SetMaximum(0.6)

  leg = TLegend(0.73,0.66,0.92,0.90)
  if not isBadSet:
    leg.AddEntry(karambaMe["SiPad2"],"SiPad2", "l")
  leg.AddEntry(karambaMe['SiPad3'],"SiPad3", "l")
  leg.AddEntry(karambaMe['SiPad4'],"SiPad4", "l")
  leg.AddEntry(karambaMe['SiPad5'],"SiPad5", "l")
  leg.AddEntry(karambaMe['SiPad6'],"SiPad6", "l")
  leg.SetFillColor(kWhite)
  leg.Draw()

  drawLabel(tag)
  c0.SaveAs(path+'/KarambaMe'+figName+'.png')


  karambaSi['SiPad3'].Draw(drawOpt)
  if not isBadSet:
    karambaSi['SiPad2'].Draw(drawOpt+' same')
  karambaSi['SiPad4'].Draw(drawOpt+' same')
  karambaSi['SiPad5'].Draw(drawOpt+' same')
  karambaSi['SiPad6'].Draw(drawOpt+' same')
  karambaSi['SiPad3'].SetMinimum(0.0)
  karambaSi['SiPad3'].SetMaximum(0.3)
  leg.Draw()

  drawLabel(tag)
  c0.SaveAs(path+'/KarambaSi'+figName+'.png')


  if doSigmaFit: return noiseTerm, noiseErr, constTerm, constErr


def effPlot(myF, tag):
  if opt.verb: print "\t Making Eff plots for ->"
  isBadSet = ('N200' in tag and not opt.june)

  c0=c1
  c0.cd()

  h = {}

  effPlot1 = TH1F('effPlot1',';SiPad Number;Efficiency', 6,0.5,6.5)
  effPlot2 = TH1F('effPlot2',';SiPad Number;Efficiency', 6,0.5,6.5)
  effPlot3 = TH1F('effPlot3',';SiPad Number;Efficiency', 6,0.5,6.5)
  effPlot4 = TH1F('effPlot4',';SiPad Number;Efficiency', 6,0.5,6.5)

  for p, ch in allPads.iteritems():
    suffix = p+'_ch'+str(ch)
    newName = 'Events'+tag+'/nEvents'+suffix+tag
    try:
      h[p]=(myF.Get(newName).Clone())
    except ReferenceError:
      print 'Looks like this hist does not exist:', newName
      print '\t *** --> This is no good.. <-- ***'
      return

    eff = h[p].GetBinContent(3)/h[p].GetBinContent(1)
    effPlot1.SetBinContent(int(p[5]),eff)

    eff = h[p].GetBinContent(7)/h[p].GetBinContent(3)
    effPlot2.SetBinContent(int(p[5]),eff)

    eff = h[p].GetBinContent(8)/h[p].GetBinContent(3)
    effPlot3.SetBinContent(int(p[5]),eff)

    eff = h[p].GetBinContent(9)/h[p].GetBinContent(3)
    effPlot4.SetBinContent(int(p[5]),eff)

    if eff==0 and p!='SiPad1':
      print p, 'eff= ', eff, 'Warning'


  path = outDir+'Efficiency'+tag
  createDir(path)

  effPlot1.Draw('p')
  effPlot2.Draw('p same')
  effPlot3.Draw('p same')
  effPlot4.Draw('p same')
  effPlot1.SetMarkerStyle(20)
  effPlot2.SetMarkerStyle(21)
  effPlot3.SetMarkerStyle(22)
  effPlot4.SetMarkerStyle(23)
  effPlot1.SetMarkerColor(kBlue+1)
  effPlot2.SetMarkerColor(kRed+1)
  effPlot3.SetMarkerColor(kGreen+1)
  effPlot4.SetMarkerColor(kCyan+1)

  effPlot1.SetMinimum(0)
  if opt.june:
    effPlot1.SetMaximum(1.0)
  else:
    effPlot1.SetMaximum(1.0)

  leg = TLegend(0.5,0.6,0.92,0.90)
  leg.AddEntry(effPlot1,"0. Pad 1 > 15 MiPs", "p")
  leg.AddEntry(effPlot2,"#0 &&  5 < Pad N < 10 MiPs /#0", "p")
  leg.AddEntry(effPlot3,"#0 && 10 < Pad N < 15 MiPs /#0", "p")
  leg.AddEntry(effPlot4,"#0 &&  Pad N > 15 MiPs /#0", "p")
  leg.SetFillColor(kWhite)
  leg.Draw()

  drawLabel(tag)
  c0.SaveAs(path+'/effPlot.png')


if __name__ == "__main__":
  print "This is the __main__ part"
  f = TFile(opt.fname,'OPEN')

  # Which plots to make:
  tags = []

  import shutil
  try:
    shutil.rmtree(outDir)
  except OSError:
    print outDir, 'probably does not exist. moving on...'


  if opt.allruns:
    for r, param in TB_DATA.iteritems():
      if opt.verb: print r, param
      # if r in ['3777','3778','3776']:
      if param['BEAM'] in opt.beam and param['HV2'] in opt.hv:
        tags.append("_RUN_"+r+"_"+param['BEAM']+"_E"+param['ENERGY']+"GEV_SENSOR_"+param['SENSOR']+"_irrHV_"+param['HV2'])

  for s in ['120','200','300']:
    for b in opt.beam:
      for hv in opt.hv:
        if opt.verb: print s, b, hv
        if opt.june:
          T='P'
        else:
          T='N'

        if opt.june and hv=='600': continue # Only taken with 800V
        tags.append("_GROUP_0_"+b+"_SENSOR_"+T+s+"_irrHV_"+hv)

        continue
        if opt.june: continue
        if b=='ELE': tags.append("_GROUP_1_"+b+"_E150GEV_SENSOR_"+T+s+"_irrHV_"+hv)
        #if b=='PION' and s=='N200' and hv=='600': continue
        if b=='ELE' and s!='300':
          tags.append("_GROUP_1_"+b+"_E100GEV_SENSOR_"+T+s+"_irrHV_"+hv)

        #tags.append("_GROUP_2_SENSOR_"+s+"_irrHV_"+hv)

  for tag in tags:
    if opt.mini: continue
    
    print '\t -> Making plots for tag:', tag

    #justPlotAll(f,'Main'+tag)
    #justPlotAll(f,'Timing'+tag)
    #justPlotAll(f,'Profiles'+tag)
    #justPlotAll(f,'Other'+tag)

    allPadsOnOnePlot(f,'Timing'+tag+'/Delay_from_Pad1_frac50',tag, fit=opt.fit)
    #allPadsOnOnePlot(f,'Timing'+tag+'/Delay_from_Pad1_frac30',tag)
    allPadsOnOnePlot(f,'Timing'+tag+'/Delay_from_Pad1_peak',tag, fit=opt.fit)
    #allPadsOnOnePlot(f,'Timing'+tag+'/Delay_from_Pad1_threshold',tag)

    allPadsOnOnePlot(f,'Timing'+tag+'/TrigDelay_frac50',tag)
    allPadsOnOnePlot(f,'Timing'+tag+'/RisingEdge_30toMax',tag)
    allPadsOnOnePlot(f,'Timing'+tag+'/RisingEdge_10to90',tag)

    for reg in ['3']:
      allPadsOnOnePlot(f,'Pulse'+tag+'/Waveform_pulse_MIPrange_'+reg,tag)
      allPadsOnOnePlot(f,'Pulse'+tag+'/Waveform_full_MIPrange_'+reg,tag)
      #allPadsOnOnePlot(f,'Pulse'+tag+'/Waveform_DoublePeak_MIPrange_'+reg,tag)


    allPadsOnOnePlot(f,'Other'+tag+'/nMIPs',tag)
    allPadsOnOnePlot(f,'Other'+tag+'/Signal_over_noise',tag)

    allPadsOnOnePlot(f,'Other'+tag+'/Pedestal',tag, fit=opt.fit)
    allPadsOnOnePlot(f,'Other'+tag+'/PedestalRMS',tag, fit=opt.fit)
    allPadsOnOnePlot(f,'Pulse'+tag+'/Charge',tag)

    onePerTag(f, 'Other'+tag+'/WC_dx_dy',tag)
    onePerTag(f, 'Other'+tag+'/WC_dx_dy_sig',tag)
    onePerTag(f, 'Timing'+tag+'/FrontToBackPadsDelay',tag)

    onePerTag(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_SigOverNoiseSiPad3_ch6',tag)
    onePerTag(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_nMIPSSiPad3_ch6',tag)

    # Sigma plots (without fits):
    sigmaPlot(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_nMIPs',tag)
    sigmaPlot(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_SigOverNoise',tag)
    sigmaPlot(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_sOvern_Pad1X',tag)
    sigmaPlot(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_sOvern_Pad1X_nMiPcut',tag)


    if 'GROUP_0' in tag:
      effPlot(f, tag)


  if not opt.mini:
    justPlotAll(f,'PER-RUN')


    runs = [SiPad_DATA['BeginRun'], SiPad_DATA['EndRun']]
    hPed = TH1F('Ped','Ped', runs[1]-runs[0], runs[0], runs[1])
    hPio = TH1F('Pio','Pio', runs[1]-runs[0], runs[0], runs[1])
    h300 = TH1F('300','300', runs[1]-runs[0], runs[0], runs[1])
    h200 = TH1F('200','200', runs[1]-runs[0], runs[0], runs[1])
    h120 = TH1F('120','120', runs[1]-runs[0], runs[0], runs[1])

    for i in TB_DATA:
      # print i
      if TB_DATA[str(i)]['ENERGY'] == 'ped':
        hPed.Fill(int(i),5000)
      elif TB_DATA[i]['BEAM'] == 'PION':
        hPio.Fill(int(i),5000)
      elif TB_DATA[i]['SENSOR'][1:] == '300':
        h300.Fill(int(i),5000)
      elif TB_DATA[i]['SENSOR'][1:] == '200':
        h200.Fill(int(i),5000)
      elif TB_DATA[i]['SENSOR'][1:] == '120':
        h120.Fill(int(i),5000)

    allPadsOnOnePlot(f,'PER-RUN'+'/Pedestal_PerRun','',overHists=[h300,h200,h120,hPed,hPio])
    allPadsOnOnePlot(f,'PER-RUN'+'/PedestalRMS_PerRun','',overHists=[h300,h200,h120,hPed,hPio])
    allPadsOnOnePlot(f,'PER-RUN'+'/Pedestal_PerRun_WithSig','',overHists=[h300,h200,h120,hPed,hPio])
    allPadsOnOnePlot(f,'PER-RUN'+'/PedestalRMS_PerRun_WithSig','',overHists=[h300,h200,h120,hPed,hPio])


  if opt.mini:
    b={}
    fitData = {}
    #ind = tag.find('SENSOR')
    print "\t Only doing test plots (--mini)\n First, let's remove the directory: ", outDir
    for tag in tags:
      print '\t -> Making plots for tag:', tag
      if 'GROUP_0_ELE_' not in tag: continue

      # sigmaPlots with fits:
      sigmaPlot(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_SigOverNoise',tag)
      b[tag] = sigmaPlot(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_sOvern_Pad1X',tag, doSigmaFit=True)

    for tag in tags:
      print '\t Fit results for tag=',tag
      # print b[tag][0], b[tag][1]

      for p in ['SiPad2','SiPad3','SiPad4','SiPad5','SiPad6']:
        try:
          print "%s, %.3f +/- %.3f \t %.3f +/- %.3f" % (p, b[tag][0][p], b[tag][1][p], b[tag][2][p], b[tag][3][p])
        except KeyError:
          print 'Key error exception for pad:', p

