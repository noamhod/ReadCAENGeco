#!/usr/bin/env python
import ROOT
from ROOT import *
import datetime
import argparse

parser = argparse.ArgumentParser(description='Read CAEN')
parser.add_argument('-f', metavar='<file name>', required=True, help='The file name')
parser.add_argument('-c', metavar='<channels used>', required=True, help='e.g. 0-3 or 4-7')
parser.add_argument('-p', metavar='<print data>', required=False, help='Print the data y/[n]?')
parser.add_argument('-l', metavar='<label factor>', required=False, help='How many timestamp labels to skip?')
parser.add_argument('-t', metavar='<minimum time HH:MM>', required=False, help='Minimum time to read: HH:MM')
parser.add_argument('-s', metavar='<current axxis scales>', required=False, help='Current axis scale: 1e-3,1e-1:1e-4,1e-1:1e-5,2:1e-4,1e-2')
args = parser.parse_args()
doprint  = True if(args.p=="y") else False
channels = args.c
fnamein  = args.f
tmin     = ""
if(args.t is not None): tmin = args.t
scales   = []
if(args.s is not None): scales = args.s.split(":")
yscales = []
for scale in scales:
   minmax = scale.split(",")
   yscales.append([float(minmax[0]),float(minmax[1])])
fnameout = (args.f).replace(".log","")
labelf   = 200
if(args.l is not None): labelf = int(args.l)
channel_min = int(channels.split("-")[0])
channel_max = int(channels.split("-")[1])
if((channel_max-channel_min)!=3):
   print "this script is designed to work with exactly 4 channels, e.g. 0-3 or 4-7.\nPlease fix your -c parameter\n...Quitting"
   quit()
cmap = {channel_min:0, channel_min+1:1, channel_min+2:2, channel_max:3}
print "Channel mapping used:",cmap

ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(0);
ROOT.gStyle.SetOptStat(0);
ROOT.gStyle.SetPadBottomMargin(0.15)
ROOT.gStyle.SetPadLeftMargin(0.13)


data = {}

def deltaT(t,tmin):
   t = t[:-3]
   t1 = datetime.datetime.strptime(tmin, '%H:%M')
   t2 = datetime.datetime.strptime(t,    '%H:%M')
   return (t2-t1)


def ParseLine(line):
   words = line.split()
   ### example line for NTD1471 power supply:
   ### [2019-01-16T11:08:54]: [NTD1471] bd [0] ch [0] par [VMon] val [2900.2]; 
   ### [2019-01-16T11:08:58]: [NTD1471] bd [0] ch [3] par [IMonL] val [0.001]; <-- can be also IMonH
   ### example line for sy5527lc power supply:
   ### [2019-01-28T09:03:08]: [sy5527lc] bd [1] ch [4] par [VMon] val [23.78];
   ### [2019-01-28T09:03:15]: [sy5527lc] bd [1] ch [7] par [IMon] val [1.67485]; 
   timestampfull = words[0].replace("[","").replace("]:","")
   timestamp     = timestampfull.split("T")[1]
   channel       = int(words[5].replace("[","").replace("]",""))
   channel       = cmap[channel]
   parameter     = words[7].replace("[","").replace("]","")
   value         = float(words[9].replace("[","").replace("];",""))
   if("IMon" in parameter): parameter = "IMon"
   return timestamp,channel,parameter,value


def ReadData(fnamein):
   with open(fnamein,"r") as lines:
      for line in lines:
         line = line.replace("\n","")
         # print line
         timestamp,channel,parameter,value = ParseLine(line)
         # print "%s,  %s,  %s:  %g" %(timestamp,channel,parameter,value)
         if(parameter=="ChStatus"): continue
         if(tmin!="" and deltaT(timestamp,tmin).days<0): continue
         if(timestamp not in data.keys()):
            data.update({timestamp:{"VMon":[-1,-1,-1,-1], "IMon":[-1,-1,-1,-1]}})
         data[timestamp][parameter][channel] = value


def PrintData():
   keylist = data.keys()
   keylist.sort()
   for key in keylist:
      print key+" --> ",data[key]


def PlotData():
   Nbins = len(data)
   hVMon = []
   hIMon = []
   hVMonGaps = []
   hIMonGaps = []
   for i in xrange(4):
      hVMon.append( TH1D("VMon"+str(i),"Chanel #"+str(i)+";;[V]",Nbins,0,Nbins) )
      hIMon.append( TH1D("IMon"+str(i),"Chanel #"+str(i)+";;[#muA]",Nbins,0,Nbins) )
      hVMon[i].SetLineColor(ROOT.kBlue)
      hIMon[i].SetLineColor(ROOT.kRed)
      hVMon[i].SetMarkerColor(ROOT.kBlue)
      hIMon[i].SetMarkerColor(ROOT.kRed)
      hVMon[i].SetMarkerStyle(20)
      hIMon[i].SetMarkerStyle(20)
      hVMon[i].SetMarkerSize(0.6)
      hIMon[i].SetMarkerSize(0.6)

      iMin = 1e-5 if(len(yscales)!=4) else yscales[i][0]
      iMax = 5    if(len(yscales)!=4) else yscales[i][1]
      hVMon[i].SetMaximum(3500.)
      hIMon[i].SetMaximum(iMax)
      hVMon[i].SetMinimum(0.)
      hIMon[i].SetMinimum(iMin)

      hVMonGaps.append( hVMon[i].Clone("VMonGaps"+str(i)) )
      hIMonGaps.append( hIMon[i].Clone("IMonGaps"+str(i)) )
      hVMonGaps[i].Reset()
      hIMonGaps[i].Reset()


   keylist = data.keys()
   keylist.sort()
   bin = 1
   nkey = 0
   imonav = [0,0,0,0]
   nimon = [0,0,0,0]
   for key in keylist:
      for i in xrange(4):
         if(nkey%labelf==0):
            hVMon[i].GetXaxis().SetBinLabel(bin,key[:-3])
            hIMon[i].GetXaxis().SetBinLabel(bin,key[:-3])
         vmon = data[key]["VMon"][i]
         imon = data[key]["IMon"][i]
         if(imon>=0):
            imonav[i] += imon
            nimon[i] += 1
         if(vmon>0):
	        hVMon[i].SetBinContent(bin,vmon)
	        hVMonGaps[i].SetBinContent(bin,vmon)
         else: hVMonGaps[i].SetBinContent(bin,hVMonGaps[i].GetBinContent(bin-1))
         if(imon==0):
            hIMon[i].SetBinContent(bin,1.e-7)
            hIMonGaps[i].SetBinContent(bin,1.e-7)
         elif(imon>0):
            hIMon[i].SetBinContent(bin,imon)
            hIMonGaps[i].SetBinContent(bin,imon)
         else: hIMonGaps[i].SetBinContent(bin,hIMonGaps[i].GetBinContent(bin-1))
      bin+=1
      nkey+=1

   for i in xrange(4):
      print "Channel %g: average IMon = %g [uA]" % (i, imonav[i]/nimon[i])

   cnv = TCanvas("cnv","",1000,1100)
   upperPad = TPad("upperPad", "upperPad", 0, 0.9, 1, 1);
   lowerPad = TPad("lowerPad", "lowerPad", 0, 0, 1, 0.9);
   upperPad.Draw()
   lowerPad.Draw()

   upperPad.cd()
   title = TText(.5,.7,fnamein.replace(".log",""))
   title.SetTextAlign(22)
   title.SetTextFont(43)
   title.SetTextSize(20)
   title.Draw()
   mapping = TText(.5,.3,"Original channels "+channels+" mapped to 0-3 here")
   mapping.SetTextAlign(22)
   mapping.SetTextFont(43)
   mapping.SetTextSize(20)
   mapping.Draw()

   # cnv = TCanvas("cnv","",1000,1000)
   lowerPad.Divide(2,2)
   pV = []
   pI = []
   leg = []
   for i in xrange(4):
      lowerPad.cd(i+1) ### important!
      pV.append( ROOT.TPad("base_padV"+str(i),"",0,0,1,1) )
      pI.append( ROOT.TPad("clear_padV"+str(i),"",0,0,1,1) )
      pI[i].SetFillColor(0)
      pI[i].SetFillStyle(4000)
      pI[i].SetFrameFillStyle(0)

      pV[i].Draw()
      pV[i].cd()
      pV[i].SetTicky(0)
      hVMon[i].Draw("p")
      hVMonGaps[i].Draw("hist same")
      hVMon[i].GetYaxis().SetTitleOffset(1.7)
      hVMonGaps[i].GetYaxis().SetTitleOffset(1.7)

      pI[i].Draw()
      pI[i].cd()
      pI[i].SetLogy()
      hIMon[i].Draw("p Y+")
      hIMonGaps[i].Draw("hist same Y+")
      hIMon[i].GetYaxis().SetTitleOffset(1.1)
      hIMonGaps[i].GetYaxis().SetTitleOffset(1.1)

      leg.append( TLegend(0.15,0.8,0.4,0.9) )
      leg[i].SetFillStyle(4000) #will be transparent
      leg[i].SetFillColor(0)
      leg[i].SetTextFont(42)
      leg[i].SetBorderSize(0)
      leg[i].AddEntry(hVMon[i],"VMon","lp")
      leg[i].AddEntry(hIMon[i],"IMon","lp")
      leg[i].Draw("same")

   cnv.Update()
   cnv.SaveAs(fnameout+".pdf")

   f = TFile(fnameout+".root","RECREATE")
   for i in xrange(4):
      hVMon[i].Write()
      hIMon[i].Write()
      hVMonGaps[i].Write()
      hIMonGaps[i].Write()
   f.Write()
   f.Close()


ReadData(fnamein)
if(doprint): PrintData()
PlotData()

