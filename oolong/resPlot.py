#!/usr/bin/env python

# This script will take the TGraphs from the input files and plot them

import argparse
parser =  argparse.ArgumentParser(description='Ploting my plots', usage="./resPlot --fP f1.root --fN f2.root")
parser.add_argument("--fApr",  dest="fApr", type=str, default='fApr.root', help='there is no help')
parser.add_argument("--fJun",  dest="fJun", type=str, default='fJun.root', help='there is no help')
parser.add_argument("--log",  dest="log", action="store_true", default=False , help='Do logX')


opt = parser.parse_args()

from ROOT import *
gROOT.SetBatch()
gROOT.ProcessLine(".L ../sugar-n-milk/tdrstyle.C")
setTDRStyle()
gROOT.ForceStyle()


fApr = TFile(opt.fApr, 'open')
fJun = TFile(opt.fJun, 'open')

# There were two HV setting in the April's data: 600 and 800 V
HV_Apr='800'
g120N = fApr.Get('Sigma_GROUP_0_ELE_SENSOR_N120_irrHV_'+HV_Apr)
g200N = fApr.Get('Sigma_GROUP_0_ELE_SENSOR_N200_irrHV_'+HV_Apr)
g300N = fApr.Get('Sigma_GROUP_0_ELE_SENSOR_N300_irrHV_'+HV_Apr)

g120N.SetMarkerStyle(20)
g120N.SetMarkerColor(kRed+1)
g120N.SetLineStyle(2)
g200N.SetMarkerStyle(21)
g200N.SetMarkerColor(kRed)
g200N.SetLineStyle(3)
g300N.SetMarkerStyle(22)
g300N.SetMarkerColor(kRed+3)
g300N.SetLineStyle(4)

g120P = fJun.Get('Sigma_GROUP_0_ELE_SENSOR_P120_irrHV_800')
g200P = fJun.Get('Sigma_GROUP_0_ELE_SENSOR_P200_irrHV_800')
g300P = fJun.Get('Sigma_GROUP_0_ELE_SENSOR_P300_irrHV_800')

g120P.SetMarkerStyle(20)
g120P.SetMarkerColor(kBlue+1)
g120P.SetLineStyle(2)
g200P.SetMarkerStyle(21)
g200P.SetMarkerColor(kBlue)
g200P.SetLineStyle(3)
g300P.SetMarkerStyle(22)
g300P.SetMarkerColor(kBlue+3)
g300P.SetLineStyle(4)



c1 = TCanvas("c1","small canvas",600,600);
mg = TMultiGraph()
mg.SetTitle('')

drawOpt = 'PL E1'
#if opt.log: 
#    drawOpt = 'P E1'
mg.Add(g120N,drawOpt)
mg.Add(g200N,drawOpt)
mg.Add(g300N,drawOpt)
mg.Add(g120P,drawOpt)
mg.Add(g200P,drawOpt)
mg.Add(g300P,drawOpt)

mg.SetMinimum(0)
mg.SetMaximum(160)

if opt.log:
    lines = []
    for g in mg.GetListOfGraphs():
        x0,y0,x1,y1,x4,y4 = Double(0), Double(0), Double(0), Double(0), Double(0), Double(0)
        g.GetPoint(0,x0,y0)
        g.GetPoint(1,x1,y1)
        g.GetPoint(4,x4,y4)
        lines.append(TLine(x1, y0, x4, y0))
        lines[-1].SetLineColor(g.GetMarkerColor())
        lines[-1].SetLineWidth(2)
        lines[-1].SetLineStyle(9)
        g.RemovePoint(0)
        c1.SetLogx()
        #print g.GetName()
        #g.Print()
    # Here just remove a bad point (low stats):
    g120P.RemovePoint(3)
else:
    g120P.RemovePoint(4)

        
mg.Draw('A')
mg.GetXaxis().SetTitle('Radiation, n/cm^{2} #times 10^{15}')
mg.GetYaxis().SetTitle('Time resolution, ps')

if opt.log:
    for l in lines:
        l.Draw()

leg = TLegend(0.30,0.68,0.55,0.88)
leg.SetNColumns(2)
leg.AddEntry(g120N, 'N120', 'PL')
leg.AddEntry(g120P, 'P120', 'PL')
leg.AddEntry(g200N, 'N200', 'PL')
leg.AddEntry(g200P, 'P200', 'PL')
leg.AddEntry(g300N, 'N300', 'PL')
leg.AddEntry(g300P, 'P300', 'PL')
leg.SetTextFont(42)
leg.SetTextSize(0.04)
leg.SetFillColor(kWhite)
leg.Draw()

c1.SaveAs('sigma_graph.png')


c2 = TCanvas("c2","ratio canvas",600,700);
c2.cd()
pad1 = TPad("pad1","pad1",0,0.3,1,1);
pad2 = TPad("pad2","pad2",0,0,1,0.3);
pad1.SetBottomMargin(0)
pad1.Draw()
pad2.SetBottomMargin(0.25)
pad2.SetTopMargin(0)
pad2.Draw()


gPadsN = {}
gPadsP = {}
gStyle.SetOptFit(0)

for p in ['SiPad2','SiPad3','SiPad4','SiPad5','SiPad6']:
    for th in ['120','200','300']:
        if th=='200' and p=='SiPad2': continue # It does not exist for N-type
        
        ind=p+'_'+th
        gPadsN[ind] = fApr.Get(p+'_GROUP_0_ELE_SENSOR_N'+th+'_irrHV_800')
        gPadsP[ind] = fJun.Get(p+'_GROUP_0_ELE_SENSOR_P'+th+'_irrHV_800')
        pad1.cd()
        gPadsN[ind].Draw('e1p')
        gPadsP[ind].Draw('e1p same')
        gPadsN[ind].SetMaximum(0.3)
        gPadsN[ind].SetMinimum(0.01)
        gPadsN[ind].SetLineColor(kRed+3)
        gPadsP[ind].SetLineColor(kBlue+3)

        leg = TLegend(0.50,0.7,0.85,0.85)
        leg.AddEntry(gPadsN[ind], th+'N '+p, 'PL')
        leg.AddEntry(gPadsP[ind], th+'P '+p, 'PL')
        leg.SetTextFont(42)
        leg.SetTextSize(0.04)
        leg.SetFillColor(kWhite)
        leg.Draw()
        
        pad2.cd()
        r=gPadsP[ind].Clone()
        r.Divide(gPadsN[ind])
        r.Draw()
        r.GetFunction('f3').Delete()

        r.GetYaxis().SetTitle("Ratio")
        r.SetMaximum(1.5)
        r.SetMinimum(0.8)
        r.GetYaxis().SetNdivisions(206)
        r.GetYaxis().SetTitleOffset(0.4)
        r.SetTitleSize(0.1,"XYZ")
        r.SetLabelSize(0.1,"XY")
        r.SetLineColor(kBlack)
        r.Draw("e1p")
                                                    
        c2.SaveAs('PvsN/PvsN_plot_'+ind+'.png')
