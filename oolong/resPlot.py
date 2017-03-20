#!/usr/bin/env python

# This script will take the TGraphs from the input files and plot them
import argparse
parser =  argparse.ArgumentParser(description='Ploting my plots', usage="./resPlot --fP f1.root --fN f2.root")
parser.add_argument("--scale", dest="scale", type=float, default=1.0, help='Scale down the P-type histograms')
parser.add_argument("--shift", dest="shift", type=float, default=0.0, help='Shift down the P-type histograms, ps')
parser.add_argument("--log",   dest="log",   action="store_true", default=False, help='Do logX')
parser.add_argument("--ratio", dest="ratio", action="store_true", default=False, help='Plot ratio of P to N')
parser.add_argument("--diff",  dest="diff",  action="store_true", default=False, help='Plot difference ot P to N')

opt = parser.parse_args()

from ROOT import *
gROOT.SetBatch()
gROOT.ProcessLine(".L ../sugar-n-milk/tdrstyle.C")
setTDRStyle()
gROOT.ForceStyle()



def getSigmaFinalFits(fRoo, siType='N', HV='800'):

    g120 = fRoo.Get('Sigma_GROUP_0_ELE_SENSOR_'+siType+'120_irrHV_'+HV)
    g200 = fRoo.Get('Sigma_GROUP_0_ELE_SENSOR_'+siType+'200_irrHV_'+HV)
    g300 = fRoo.Get('Sigma_GROUP_0_ELE_SENSOR_'+siType+'300_irrHV_'+HV)

    if siType=='N':
        g120.SetMarkerStyle(20)
        g120.SetMarkerColor(kRed+1)
        g120.SetLineStyle(2)
        g200.SetMarkerStyle(21)
        g200.SetMarkerColor(kRed)
        g200.SetLineStyle(3)
        g300.SetMarkerStyle(22)
        g300.SetMarkerColor(kRed+3)
        g300.SetLineStyle(4)

    if siType=='P':
        g120.SetMarkerStyle(20)
        g120.SetMarkerColor(kBlue+1)
        g120.SetLineStyle(2)
        g200.SetMarkerStyle(21)
        g200.SetMarkerColor(kBlue)
        g200.SetLineStyle(3)
        g300.SetMarkerStyle(22)
        g300.SetMarkerColor(kBlue+3)
        g300.SetLineStyle(4)

    return [g120, g200, g300]



def getSigmaSiPads(fRoo, siType='N', HV='800'):

    gPads = {}

    for p in ['SiPad2','SiPad3','SiPad4','SiPad5','SiPad6']:
        for th in ['120','200','300']:
            ind=p+'_'+th
            #print ind

            grName = p+'_GROUP_0_ELE_SENSOR_'+siType+th+'_irrHV_'+HV
            if fRoo.GetListOfKeys().Contains(grName):
                gPads[ind] = fRoo.Get(grName).Clone()

    return gPads

def diffGraphs(gr1, gr2):
    nPoints = gr1.GetN()
    print 'Number of points:', nPoints
    for i in xrange(0,nPoints):
        xVal0,xVal1 = Double(0),Double(0)
        yVal0,yVal1 = Double(0),Double(0)
        gr1.GetPoint(i, xVal0, yVal0)
        gr2.GetPoint(i, xVal1, yVal1)

        if xVal0!=xVal0:
            print 'Warning the x-values must always agree...'
            sys.exit(0)

        # print i, xVal0, yVal0, yVal1
        print i, 'Diff: %.4f' % (100*(yVal0-yVal1)/yVal0)

if __name__ == "__main__":

    # Get the graphs

    fN = TFile('syst_backupMar20_2par/fApr_default.root', 'read')
    fP = TFile('syst_backupMar20_2par/fJun_default.root', 'read')
    #fN = TFile('fApr_default.root', 'read')
    #fP = TFile('fJun_default.root', 'read')

    grN = getSigmaFinalFits(fN,'N')
    grP = getSigmaFinalFits(fP,'P')

    g120N = grN[0]
    g200N = grN[1]
    g300N = grN[2]
    g120P = grP[0]
    g200P = grP[1]
    g300P = grP[2]

    print '\n N120:'
    g120N.Print()
    print '\n N200:'
    g200N.Print()
    print '\n N300:'
    g300N.Print()


    print '\n P120:'
    g120P.Print()
    print '\n P200:'
    g200P.Print()
    print '\n P300:'
    g300P.Print()

    ## -----
    ## Draw the main result:

    c1 = TCanvas("c1","small canvas",600,600);
    mg = TMultiGraph()
    mg.SetTitle('')

    drawOpt = 'PL E1'
    if opt.log:
        drawOpt = 'P E1'
    mg.Add(g120N,drawOpt)
    mg.Add(g200N,drawOpt)
    mg.Add(g300N,drawOpt)
    mg.Add(g120P,drawOpt)
    mg.Add(g200P,drawOpt)
    mg.Add(g300P,drawOpt)

    mg.SetMinimum(0)
    mg.SetMaximum(60)

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
        # Here just remove th bad points (low stats):
        g120P.RemovePoint(3)
        g120P.RemovePoint(2)
        g120P.RemovePoint(1)

        g200P.RemovePoint(3)

        g300P.RemovePoint(3)

    else:
        g120P.RemovePoint(4)
        g120P.RemovePoint(3)
        g120P.RemovePoint(2)

        g200P.RemovePoint(4)

        g300P.RemovePoint(4)


    mg.Draw('A')
    mg.GetXaxis().SetTitle('Radiation dose, n/cm^{2} #times 10^{15}')
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

    if opt.log:
        leg2 = TLegend(0.57,0.74,0.77,0.84)
        leg2.SetHeader("Not rad.:")
        leg2.AddEntry(lines[4],'P-type', 'L')
        leg2.AddEntry(lines[1],'N-type', 'L')
        leg2.SetTextFont(42)
        leg2.SetTextSize(0.035)
        leg2.SetBorderSize(0)
        leg2.SetFillColor(kWhite)
        leg2.Draw()

    c1.SaveAs('sigma_graph.png')



    ## -------
    ## Making ratio and shifts for N-P comparisons

    if opt.ratio and opt.diff:
        c2 = TCanvas("c2","ratio canvas",600,800);
        c2.cd()
        pad1 = TPad("pad1","pad1",0,0.34,1,  1);
        pad2 = TPad("pad2","pad2",0,0.17,1,0.34);
        pad3 = TPad("pad3","pad3",0,0.0,1,0.17);
        pad1.SetBottomMargin(0.15)
        pad1.Draw()
        pad2.SetBottomMargin(0.07)
        pad2.SetTopMargin(0)
        pad2.Draw()
        pad3.SetBottomMargin(0.07)
        pad3.SetTopMargin(0)
        pad3.Draw()
    elif opt.ratio or opt.diff:
        c2 = TCanvas("c2","ratio canvas",600,700);
        c2.cd()
        pad1 = TPad("pad1","pad1",0,0.25,1,  1);
        pad2 = TPad("pad2","pad2",0,  0,1,0.25);
        pad1.SetBottomMargin(0.15)
        pad1.Draw()
        pad2.SetBottomMargin(0.07)
        pad2.SetTopMargin(0)
        pad2.Draw()
    else:
        c2=c1
        if not opt.log: c2.SetLogx(0)
        pad1 = c2.GetPad(0)


    gPadsN = getSigmaSiPads(fN, 'N')
    #print gPadsN

    gPadsP = getSigmaSiPads(fP, 'P')
    #print gPadsP


    gStyle.SetOptFit(0)

    for p in ['SiPad2','SiPad3','SiPad4','SiPad5','SiPad6']:
        for th in ['120','200','300']:
            if th=='200' and p=='SiPad2': continue # It does not exist for N-type

            ind=p+'_'+th

            pad1.cd()
            gPadsN[ind].Draw('e1p')
            gPadsP[ind].Draw('e1p same')
            gPadsN[ind].SetMaximum(0.3)
            gPadsN[ind].SetMinimum(0.01)
            gPadsN[ind].SetLineColor(kRed+3)
            gPadsP[ind].SetLineColor(kBlue+3)

            try:
                gPadsP[ind].GetFunction('f3').Delete()
                gPadsN[ind].GetFunction('f3').Delete()
            except ReferenceError:
                print 'f3 does not exist in the graph'
                
            # Scale P
            gPadsP[ind].Scale(1./opt.scale)

            # Shift P
            for b in range(1, gPadsP[ind].GetNbinsX()+1):
                # print 'bin:', b
                gPadsP[ind].SetBinContent(b, gPadsP[ind].GetBinContent(b) - opt.shift)


            leg = TLegend(0.50,0.7,0.85,0.85)
            leg.AddEntry(gPadsN[ind], th+'N '+p, 'PL')
            leg.AddEntry(gPadsP[ind], th+'P '+p, 'PL')
            leg.SetTextFont(42)
            leg.SetTextSize(0.04)
            leg.SetFillColor(kWhite)
            leg.Draw()

            if opt.ratio:
                pad2.cd()
                r=gPadsP[ind].Clone()
                r.Divide(gPadsN[ind])
                r.Draw()
                #r.GetFunction('f3').Delete()

                r.GetYaxis().SetTitle("Ratio: P/N")
                if opt.shift==0:
                    offset = 1.2/opt.scale
                else:
                    offset = 1
                r.SetMaximum(offset+0.29)
                r.SetMinimum(offset-0.29)
                r.GetYaxis().SetNdivisions(206)
                r.GetYaxis().SetTitleOffset(0.4)
                r.SetTitleSize(0.15,"XYZ")
                r.SetLabelSize(0.12,"Y")
                r.SetLabelSize(0,"X")
                r.SetLabelOffset(999,"X")

                r.SetLineColor(kBlack)
                r.Draw("e1p")
            if opt.diff:
                if opt.ratio:
                    pad3.cd()
                else:
                    pad2.cd()
                d=gPadsP[ind].Clone()
                d.Add(gPadsN[ind], -1)
                d.Draw()
                #d.GetFunction('f3').Delete()

                d.GetYaxis().SetTitle("Diff: P-N (ns)")
                if opt.scale==1.0:
                    offset = 0.020 - opt.shift
                else:
                    offset = opt.shift

                d.SetMaximum(offset + 0.016)
                d.SetMinimum(offset - 0.016)
                d.GetYaxis().SetNdivisions(206)
                d.GetYaxis().SetTitleOffset(0.4)
                d.SetTitleSize(0.15,"XYZ")
                d.SetLabelSize(0.12,"Y")
                d.SetLabelSize(0.0,"X")
                d.SetLabelOffset(999,"X")
                d.SetLineColor(kBlack)
                d.Draw("e1p")


            c2.SaveAs('PvsN/PvsN_plot_'+ind+'.png')



    # ---------------
    # Now, let's play with systematics

    grN0 = getSigmaFinalFits(fN,'N')
    grP0 = getSigmaFinalFits(fP,'P')


    #sysTag = 'Nev60'
    #sysTag = 'Nev300'
    sysTag = '1p5rms'
    #sysTag = '2rms'
    #sysTag = '4rms'
    #sysTag = 'Range2'
    #sysTag = 'Range3'

    fN1 = TFile('fApr_'+sysTag+'.root', 'read')
    fP1 = TFile('fJun_'+sysTag+'.root', 'read')
    grN1 = getSigmaFinalFits(fN1,'N')
    grP1 = getSigmaFinalFits(fP1,'P')


    '''
    print 'N-type:'
    for t in xrange(0,3):
        print '\t Thickness: ',t
        diffGraphs(grN0[t],grN1[t])

    print 'P-type:'
    for t in xrange(0,3):
        print '\t Thickness: ',t
        diffGraphs(grP0[t],grP1[t])
    '''
