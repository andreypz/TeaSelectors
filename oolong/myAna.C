#define myAna_cxx
#include "myAna.h"
//#include <TH2.h>
//#include <TStyle.h>

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <iostream>

namespace pt = boost::property_tree;

pt::ptree TB_RUNS_DATA;

/**/
// ToDo: Much better would be to implement these settings into a json file.
// Take initial data from here:
// https://docs.google.com/spreadsheets/d/19FfZoQwFF7ZfK7Ujjwe6YZRQvfTXdvQ-N_XqVxKlUvg/edit?pref=2&pli=1#gid=712039595

/// April's settings:
const Char_t TB = 1;
map<UInt_t, string> PadsMap = {
  {0, "Trigger"},
  {1, "SiPad6"}, {2, "SiPad5"}, {3, "SiPad4"},
  {4, "SiPad1"}, {5, "SiPad2"}, {6, "SiPad3"}};
enum class PadsEnum {SiPad1 = 4, SiPad2 = 5, SiPad3=6, SiPad4=3, SiPad5=2, SiPad6=1};

map<UInt_t, Float_t> ADCperMIP ={
  // Set 1 (120 um)
  {14, 18.0}, {15, 18.0}, // SiPad 1 and 2 (closest to beam, non-irradiated)
  {16, 13.0}, {13, 12.5}, // 3 and 4
  {12, 11.3}, {11,  8.9},  // 5 and 6 (further from beam)
  // Set 2 (200 um)
  {24, 34.0}, {25, 34.0}, // SiPad 1 and 2 (closest to beam)
  {26, 27.5}, {23, 27.9}, // 3 and 4
  {22, 21.1}, {21, 16.3},  // 5 and 6 (further from beam)
  // Set 3 (300 um)
  {34, 40.0}, {35, 40.0}, // SiPad 1 and 2 (closest to beam)
  {36, 36.4}, {33, 35.6}, // 3 and 4
  {32, 36.3}, {31, 30.2}  // 5 and 6 (further from beam)
};

const UInt_t ped_offset = 140;
const Float_t trig_offset = 134.5;
const UInt_t nMIPs = 15;
const Float_t wc_cut_x[4] = {0, -3.351, -3.351, -3.351};
const Float_t wc_cut_y[4] = {0, -0.706, -0.706, -0.706};
const UInt_t runs[2] = {3650,3800};
/**/

/// Junes's settings:
/*
const Char_t TB = 2;
map<UInt_t, string> PadsMap = {
  {0, "Trigger"},
  {1, "SiPad1"}, {2, "SiPad2"}, {3, "SiPad3"},
  {4, "SiPad4"}, {5, "SiPad5"}, {6, "SiPad6"}};
enum class PadsEnum {SiPad1 = 1, SiPad2 = 2, SiPad3=3, SiPad4=4, SiPad5=5, SiPad6=6};

map<UInt_t, Float_t> ADCperMIP ={
  // Set 1 (120 um)
  {11, 18.0}, {12, 18.0}, // SiPad 1 and 2 (closest to beam, non-irradiated)
  {13, 15.1}, {14, 15.6}, // 3 and 4
  {15, 11.3}, {16,  9.8},  // 5 and 6 (further from beam)
  // Set 2 (200 um)
  {21, 34.0}, {22, 34.0}, // SiPad 1 and 2 (closest to beam)
  {23, 26.2}, {24, 19.8}, // 3 and 4
  {25, 21.6}, {26, 18.3},  // 5 and 6 (further from beam)
  // Set 3 (300 um)
  {31, 40.0}, {32, 40.0}, // SiPad 1 and 2 (closest to beam)
  {33, 37.3}, {34, 32.5}, // 3 and 4
  {35, 34.1}, {36, 27.0}  // 5 and 6 (further from beam)
};

const UInt_t ped_offset = 3610;
const Float_t trig_offset = 111.5;
const UInt_t nMIPs = 15;
const Float_t wc_cut_x[4] = {0, -3.351, -3.351, -3.351};
const Float_t wc_cut_y[4] = {0, -0.706, -0.706, -0.706};
const UInt_t runs[2] = {4170,4320};
*/
// END of settings

void myAna::Begin(TTree * /*tree*/)
{
   TString option = GetOption();

}

void myAna::SlaveBegin(TTree * /*tree*/)
{
  // The SlaveBegin() function is called after the Begin() function.
  // When running with PROOF SlaveBegin() is called on each slave server.
  // The tree argument is deprecated (on PROOF 0 is passed).

  TString option = GetOption();

  string JSONPATH = "";
  cout<<"option = "<<option.Data()<<endl;
  TObjArray *args = (TObjArray*)option.Tokenize(" ");
  if (args->GetSize()>1)
    JSONPATH = (string)((TObjString*)args->At(0))->GetString();

  // Will count events passing by each pad separately.
  // Now, set them all to zero:
  for (size_t n=0; n<nC; n++){
    nEvents[static_cast<UInt_t>(PadsEnum::SiPad1)][n]=0;
    nEvents[static_cast<UInt_t>(PadsEnum::SiPad2)][n]=0;
    nEvents[static_cast<UInt_t>(PadsEnum::SiPad3)][n]=0;
    nEvents[static_cast<UInt_t>(PadsEnum::SiPad4)][n]=0;
    nEvents[static_cast<UInt_t>(PadsEnum::SiPad5)][n]=0;
    nEvents[static_cast<UInt_t>(PadsEnum::SiPad6)][n]=0;
    nEvents[0][n]=0;
  }

  pt::read_json(JSONPATH, TB_RUNS_DATA);

  fProofFile = new TProofOutputFile("TB_2016_myHistograms.root");
  fOutput->Add(fProofFile);
  // Open the file
  histoFile = fProofFile->OpenFile("RECREATE");

  TH1::SetDefaultSumw2(kTRUE);
  hists = new HistManager(histoFile);

}


Bool_t myAna::Process(Long64_t entry)
{
  GetEntry(entry);
  for (size_t p=0; p<7; p++)
    nEvents[p][0]++;

  string RUN = Form("%i",runNumber);

  std::string BEAM   = TB_RUNS_DATA.get<std::string>(RUN+".BEAM");
  std::string ENERGY = TB_RUNS_DATA.get<std::string>(RUN+".ENERGY");
  std::string SENSOR = TB_RUNS_DATA.get<std::string>(RUN+".SENSOR");
  std::string HV1    = TB_RUNS_DATA.get<std::string>(RUN+".HV1");
  std::string HV2    = TB_RUNS_DATA.get<std::string>(RUN+".HV2");

  Char_t set = 0;
  if (SENSOR=="P120" || SENSOR=="N120") set = 1;
  else if (SENSOR=="P200" || SENSOR=="N200") set = 2;
  else if (SENSOR=="P300" || SENSOR=="N300") set = 3;
  else Abort(Form("Mission Abort! The set does not existe pas.  Sensor=%s", SENSOR.c_str()));
  //cout<<"\t Run number = **"<<RUN<<"**   BEAM ="<<BEAM<<endl;
  //Info("Process loop", "\t Run number = ** %s **   BEAM = %s", RUN.c_str(), BEAM.c_str());

  //TString msg = TString::Format("RUN: %s", RUN.c_str());
  //if (gProofServ) gProofServ->SendAsynMessage(msg);

  Float_t wc_dx = wc_recox[0]-wc_recox[1];
  Float_t wc_dy = wc_recoy[0]-wc_recoy[1];

  hists->fillProfile(runNumber, wc_dx, "WC_dx",";Run Number;Wire chambers x1-x2, mm",
		     runs[1]-runs[0], runs[0], runs[1], -10, 10, 1, "PER-RUN");
  hists->fillProfile(runNumber, wc_dy, "WC_dy",";Run Number;Wire chambers y1-y2, mm",
		     runs[1]-runs[0], runs[0], runs[1], 10, 10, 1, "PER-RUN");


  UInt_t front = static_cast<UInt_t>(PadsEnum::SiPad1);
  UInt_t back  = static_cast<UInt_t>(PadsEnum::SiPad6);

  for (size_t tagIndex=0; tagIndex<4; tagIndex++)
    {
      string tag = "_";
      if (tagIndex==1 && TB==2) continue; // Disable for June's Runs (only one energy is available)
      if (tagIndex==2) continue; // Disable for now, takes too long to run
      if (tagIndex==3) continue; // Disable for now, takes too long to run

      if (tagIndex==0) tag = "_GROUP_0_"+BEAM+"_SENSOR_"+SENSOR+"_irrHV_"+HV2;
      else if (tagIndex==1) tag = "_GROUP_1_"+BEAM+"_E"+ENERGY+"GEV_SENSOR_"+SENSOR+"_irrHV_"+HV2;
      else if (tagIndex==2 && BEAM!="NOBEAM") tag = "_GROUP_2_SENSOR_"+SENSOR+"_irrHV_"+HV2;
      else if (tagIndex==3) tag = "_RUN_"+RUN+"_"+BEAM+"_E"+ENERGY+"GEV_SENSOR_"+SENSOR+"_irrHV_"+HV2;

      if (tagIndex==1 && BEAM!="ELE") continue; // only do this for ELEctron runs, because of two energies

      
      hists->fill1DHist(t_at_threshold[0], "TrigDelay_Scintilator"+tag,
			";Time of Trigger (scintilator), ns; Events", 200, 150,180, 1, "Timing"+tag);

      for (size_t pad = 1; pad<7; pad++){

	string suffix = Form("%s_ch%i", PadsMap[pad].c_str(), (int)pad);

	Float_t aMiPcOr = 1.0; 
	if (TB==1 && HV2=="600" && (pad==1||pad==2||pad==3||pad==6))
	  aMiPcOr = 0.875;
	Float_t mipsInPad = wave_max[pad]/ADCperMIP[10*set+pad]/aMiPcOr;
	// ----
	// Pedestals
	// ----
	hists->fill1DHist(pedestal[pad], "Pedestal_"+suffix+tag,
			  ";Pedestal, ADC count; Events", 200, ped_offset,ped_offset+180, 1, "Other"+tag);
	hists->fill1DHist(pedestalRMS[pad], "PedestalRMS_"+suffix+tag,
			  ";Pedestal RMS (Noise), ADC count;Events", 200, 0,30, 1, "Other"+tag);

	if (tagIndex==0) {
	  //This one only do once (becasuse it's a plot Per run)
	  hists->fillProfile(runNumber, pedestal[pad], "Pedestal_PerRun_"+suffix,
			     ";Run Number;Pedestal, ADC count", runs[1]-runs[0], runs[0], runs[1], ped_offset-50, ped_offset+300, 1, "PER-RUN");
	  //and this one
	  hists->fillProfile(runNumber, pedestalRMS[pad], "PedestalRMS_PerRun_"+suffix,
			     ";Run Number;Pedestal RMS, ADC count", runs[1]-runs[0], runs[0], runs[1], 0, 60, 1, "PER-RUN");
	}
	const Float_t Scint = t_at_threshold[0]-trig_offset;
	// ---------------------
	// Count events here:
	//----------------------
	FillHistoCounts(0, suffix,tag);
	
	if (wave_max[front]/ADCperMIP[10*set+front] < 15){
	  FillHistoCounts(1, suffix,tag);

	  if (tagIndex==0 && mipsInPad > 5  && mipsInPad < 10){
	    hists->fill1DHist(runNumber, "Events_PerRun_Cut3_"+suffix,
			      ";Run Number;Events", runs[1]-runs[0], runs[0], runs[1], 1, "PER-RUN");
	    FillHistoCounts(3, suffix,tag);
	  }
	  if (tagIndex==0 && mipsInPad > 10 && mipsInPad < 15){
	    hists->fill1DHist(runNumber, "Events_PerRun_Cut4_"+suffix,
			      ";Run Number;Events", runs[1]-runs[0], runs[0], runs[1], 1, "PER-RUN");
	    FillHistoCounts(4, suffix,tag);
	  }
	  if (tagIndex==0 && mipsInPad > 15){
	    hists->fill1DHist(runNumber, "Events_PerRun_Cut5_"+suffix,
			      ";Run Number;Events", runs[1]-runs[0], runs[0], runs[1], 1, "PER-RUN");
	    FillHistoCounts(5, suffix,tag);
	  }
	}
	else {

	  FillHistoCounts(2, suffix,tag);
	  if (tagIndex==0 && mipsInPad > 5  && mipsInPad < 10){
	    hists->fill1DHist(runNumber, "Events_PerRun_Cut6_"+suffix,
			      ";Run Number;Events", runs[1]-runs[0], runs[0], runs[1], 1, "PER-RUN");
	    FillHistoCounts(6, suffix,tag);
	  }
	  if (tagIndex==0 && mipsInPad > 10 && mipsInPad < 15){
	    hists->fill1DHist(runNumber, "Events_PerRun_Cut7_"+suffix,
			      ";Run Number;Events", runs[1]-runs[0], runs[0], runs[1], 1, "PER-RUN");
	    FillHistoCounts(7, suffix,tag);
	  }
	  if (tagIndex==0 && mipsInPad > 15){
	    hists->fill1DHist(runNumber, "Events_PerRun_Cut8_"+suffix,
			      ";Run Number;Events", runs[1]-runs[0], runs[0], runs[1], 1, "PER-RUN");
	    FillHistoCounts(8, suffix,tag);
	  }
	}

	// All events are accouted for..
	
	
	// -------------------
	// NOW.
	// --- Only for good signals (#Mips > X)
	// ----------------------
	if (mipsInPad > nMIPs){


	  // Here let's just plot the time delay from trigger
	  hists->fill1DHist(t_max_frac50[pad]-Scint, "TrigDelay_frac50_"+suffix+tag,
			    ";Frac50 Time from trigger, ns;Events", 200, -2,4, 1,"Timing"+tag);

	  hists->fill1DHist(t_max[pad] - t_max_frac30[pad], "RisingEdge_30toMax_"+suffix+tag,
			    ";Rising edge from 30% to Max, ns;Events", 200, 0.7,1.7, 1,"Timing"+tag);

	  hists->fill1DHist(t_max_frac90[pad] - t_max_frac10[pad], "RisingEdge_10to90_"+suffix+tag,
			    ";Rising edge from 10% to 90%, ns;Events", 200, 0.7,1.7, 1,"Timing"+tag);

	  //hists->fill1DHist(t_max[pad], "TrigDelay_NoCorrection"+suffix,
	  //		";Time from trigger, ns;Events", 200, -20,60, 1,"Timing");

	  hists->fill1DHist(charge_integ[pad]/1000, "Charge_"+suffix+tag,
			    ";Integral of the pulse (Charge) #times 1000;Events", 200, 0, 15, 1,"Pulse"+tag);


	  if (tagIndex==0 && BEAM!="NOBEAM") {
	    // This stuff only needs to be done once!

	    // Here, let's see how much would the cut on wires change the results:
	    if (fabs(wc_dx-wc_cut_x[set]) < 1 && fabs(wc_dy-wc_cut_y[set]) < 1)
	      nEvents[pad][2]++;

	    hists->fill2DHist(wc_dx, wc_dy, "WC_dx_dy"+tag,
			      ";WC x1-x2, mm;WC y1-y2, mm;", 200, -10,10, 200, -10,10, 1,"Other"+tag);


	    // Do pedestals again, but this time only when there is signal.
	    hists->fillProfile(runNumber, pedestal[pad], "Pedestal_PerRun_WithSig_"+suffix,
			       ";Run Number;Pedestal, ADC count", runs[1]-runs[0], runs[0], runs[1], ped_offset-50, ped_offset+300, 1, "PER-RUN");
	    hists->fillProfile(runNumber, pedestalRMS[pad], "PedestalRMS_PerRun_WithSig_"+suffix,
			       ";Run Number;Pedestal RMS, ADC count", runs[1]-runs[0], runs[0], runs[1], 0, 60, 1, "PER-RUN");
	  }


	}


	for (size_t step=0; step<4; step++){

	  // ---
	  // Here let's make a profile of all the waveforms
	  // Do this for four different ranges on nMIPS:
	  // [ 3*pedeatalRMS -- 5 MIPS -- 10 MIPS -- 20 MIPS -- above]
	  // ---

	  // Note: if setps 0,1,2 are 'continued' it means they wont run.
	  // This is to speed up things, they take too long... Comment out those lines to include the plots
	  if (step==0) continue;
	  if (step==1) continue;
	  if (step==2) continue;
	  if (step==0 && (wave_max[pad] < 3*pedestalRMS[pad] || mipsInPad > 5)) continue;
	  if (step==1 && (mipsInPad < 5  || mipsInPad > 10)) continue;
	  if (step==2 && (mipsInPad < 10 || mipsInPad > 20)) continue;
	  if (step==3 && (mipsInPad < 20)) continue;

	  for (size_t w=0; w<50; w++){

	    hists->fillProfile(time_aroundmax[pad][w]*1E9 - t_max_frac50[pad], wave_aroundmax[pad][w]/wave_max[pad],
			       "Waveform_pulse_MIPrange_"+(string)Form("%zu_",step)+suffix+tag,
			       ";Time (zero at 50%), ns;Pulse shape, normalized at peak", 300, -2,5, -2, 2, 1, "Pulse"+tag);


	    hists->fillProfile(time_aroundmax[pad][w]*1E9 - t_max_frac50[pad], wave_aroundmax[pad][w]/wave_max[pad],
			       "Waveform_full_MIPrange_"+(string)Form("%zu_",step)+suffix+tag,
			       ";Time (zero at 50%), ns;Pulse shape, normalized at peak", 300, -20,30, -2, 2, 1, "Pulse"+tag);

	    // See what's up with the double peak structure
	    /*
	    if (t_max_frac50[pad]-Scint > 1)
	      hists->fillProfile(time_aroundmax[pad][w]*1E9 - t_max_frac50[pad], wave_aroundmax[pad][w]/wave_max[pad],
				 "Waveform_DoublePeak_MIPrange_"+(string)Form("%zu_",step)+suffix+tag,
				 ";Time (zero at 50%), ns;Pulse shape, normalized at peak", 300, -20,30, -2, 2, 1, "Pulse"+tag);
	    */

	  }


	}



	// ------
	// Can't rely on the Trigger for good timing study.
	// Instead let's use the first diod (SiPad1) as a reference ('front').
	// ----

	const Float_t refPad1 = t_max_frac50[front];

	// Only get the timing if both pads have high signals
	if (mipsInPad > nMIPs && wave_max[front]/ADCperMIP[10*set+front] > nMIPs && pad!=front){
	  // Only do this for time at 50% threshold for now

	  //hists->fill1DHist(t_at_threshold[pad] - refPad1, "Delay_from_Pad1_threshold_"+suffix+tag,
	  //";At Thresh Time from SiPad1 (frac50), ns;Events", 200, -0.6,0.6, 1,"Timing"+tag);
	  hists->fill1DHist(t_max_frac30[pad] - refPad1, "Delay_from_Pad1_frac30_"+suffix+tag,
			    ";Frac30 Time from SiPad1 (frac50), ns;Events", 200, -0.6,0.6, 1,"Timing"+tag);
	  hists->fill1DHist(t_max_frac50[pad] - refPad1, "Delay_from_Pad1_frac50_"+suffix+tag,
			    ";Frac50 Time from SiPad1 (frac50), ns;Events", 200, -0.6,0.6, 1,"Timing"+tag);

	  hists->fill1DHist(t_max_frac50[pad] - refPad1, "Delay_from_Pad1_frac50_wide_"+suffix+tag,
			    ";Frac50 Time from SiPad1 (frac50), ns;Events", 200, -10,10, 1,"Timing"+tag);

	  hists->fill1DHist(t_max[pad] - refPad1, "Delay_from_Pad1_peak_"+suffix+tag,
			    ";Peak Time from SiPad1 (frac50), ns;Events", 200, 0.3,1.6, 1,"Timing"+tag);

	}

	// Select good signal in Pad 1 and make 2D plots in other Pads
	if (wave_max[front]/ADCperMIP[10*set+front] > nMIPs && pad!=front){

	  hists->fill1DHist(mipsInPad, "nMIPs_"+suffix+tag,
			    ";Number of MiPs;Events", 400, 0,60, 1,"Other"+tag);

	  hists->fill1DHist(wave_max[pad]/pedestalRMS[pad], "Signal_over_noise_"+suffix+tag,
			    ";Signal/Noise;Events", 400, 2,160, 1,"Other"+tag);

	  hists->fill2DHist(mipsInPad, t_max_frac50[pad] - refPad1,
			    "2D_Delay_from_Pad1_frac50_VS_nMIPs_"+suffix+tag,
			    ";Number of MiPs;T_{padX} - T_{pad1}, ns", 400, 0,60, 200, -0.6,0.6, 1,"Timing"+tag);

	  hists->fill2DHist(wave_max[pad]/pedestalRMS[pad], t_max_frac50[pad] - refPad1,
			    "2D_Delay_from_Pad1_frac50_VS_SigOverNoise_"+suffix+tag,
			    ";Signal/Noise;T_{padX} - T_{pad1}, ns", 400, 2,160, 200, -0.6,0.6, 1,"Timing"+tag);
	}

      }


      // ----
      // Compare front vs back Pads
      // ---

      hists->fill2DHist(wave_max[front]/ADCperMIP[10*set+front], wave_max[back]/ADCperMIP[10*set+back], "2D_Mips_fron_back"+tag,
			";Front sensor apmplitude, MiPs;Back sensor apmplitude, MiPs", 200, 0,100, 200, 0,100, 1,"Other"+tag);

      if (wave_max[front]/ADCperMIP[10*set+front]>nMIPs && wave_max[back]/ADCperMIP[10*set+back]>nMIPs){

	hists->fill1DHist(t_max_frac50[back] - t_max_frac50[front], "FrontToBackPadsDelay"+tag,
			  ";Time delay, (Pad6 - Pad1), ns;Events", 100, -0.5,0.8, 1,"Timing"+tag);


	// Now, we have high signals in both front and back diodes,
	// lets look at wire chambers:
	if (tagIndex==0) { //only do this once

	  hists->fillProfile(runNumber, wc_dx, "WC_dx_sig",";Run Number;Wire chambers x1-x2, mm",
			     runs[1]-runs[0], runs[0], runs[1], -10, 10, 1, "PER-RUN");
	  hists->fillProfile(runNumber, wc_dy, "WC_dy_sig",";Run Number;Wire chambers y1-y2, mm",
			     runs[1]-runs[0], runs[0], runs[1], -10, 10, 1, "PER-RUN");
	}
	// And this one for all different setups:
	hists->fill2DHist(wc_dx, wc_dy, "WC_dx_dy_sig"+tag,
			  ";WC x1-x2, mm;WC y1-y2, mm;", 200, -10,10, 200, -10,10, 1,"Other"+tag);

      }
    }


  //if (nEvents[0]<20)
  //std::cout<<"We are processing ev number "<<nEvents[0]<<endl;

  return kTRUE;
}


void myAna::SlaveTerminate()
{
  // The SlaveTerminate() function is called after all entries or objects
  // have been processed. When running with PROOF SlaveTerminate() is called
  // on each slave server.

  cout<<" ** YIELDS **"<<endl;
  cout<<"n |"<<setw(10)<<" SiPad1| SiPad2| SiPad3| SiPad4| SiPad5| SiPad6 |"<<endl;
  for (UInt_t n=0; n<nC; n++){
    cout<< n<<" |"<<setw(6)
	<<nEvents[static_cast<UInt_t>(PadsEnum::SiPad1)][n]<<" |"<<setw(6)
	<<nEvents[static_cast<UInt_t>(PadsEnum::SiPad2)][n]<<" |"<<setw(6)
	<<nEvents[static_cast<UInt_t>(PadsEnum::SiPad3)][n]<<" |"<<setw(6)
	<<nEvents[static_cast<UInt_t>(PadsEnum::SiPad4)][n]<<" |"<<setw(6)
	<<nEvents[static_cast<UInt_t>(PadsEnum::SiPad5)][n]<<" |"<<setw(6)
	<<nEvents[static_cast<UInt_t>(PadsEnum::SiPad6)][n]<<" |"
	<<endl;

  }



  histoFile->cd();

  histoFile->Write();
  histoFile->Close();

  cout<<" ** Slave is terminating, my master ...bow x 3... **"<<endl;



}

void myAna::Terminate()
{
  //histoFile->cd();

  // histoFile->Write();
  //histoFile->Close();

  cout<<"\n ... Now Master is Terminating! Stay away from the monitor ..."<<endl;
}


void myAna::FillHistoCounts(UInt_t num, string suff, string tag)
{
  hists->fill1DHist(num, "nEvents"+suff+tag, ";Cut Number;Events passed", nC+1, 0,nC+1, 1, "Events"+tag);

}
