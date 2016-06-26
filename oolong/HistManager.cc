#include "HistManager.h"

HistManager::HistManager(TFile* myFile){
  theFile = myFile;
  //theFile -> Print();

}


HistManager::~HistManager(){
}

/*
  void HistManager::writeHists(TFile* myFile){

    myFile->cd();
    std::map<std::string,TH1F*>::const_iterator mapit1;
    std::map<std::string,TH2F*>::const_iterator mapit2;
    std::map<std::string,TProfile*>::const_iterator mapit3;
    for (mapit1 = the1DMap.begin(); mapit1 != the1DMap.end(); ++mapit1){
    (*mapit1).second->Write();
    }
    for (mapit2 = the2DMap.begin(); mapit2 != the2DMap.end(); ++mapit2){
    (*mapit2).second->Write();
    }
    for (mapit3 = theProfMap.begin(); mapit3 != theProfMap.end(); ++mapit3){
    (*mapit3).second->Write();
    }
    myFile->cd();
    myFile->Close();

    }
*/
void HistManager:: makeDirectory(std::string folder){
  //If the requested folder doesn't exist, we should create it first:
  if (!theFile->GetDirectory(folder.c_str()))
    theFile->mkdir(folder.c_str(), folder.c_str());

}

void HistManager::fill1DHist(float x, std::string name, std::string title,
			     int bins, float xmin, float xmax, float weight, std::string folder){

  std::map<std::string,TH1F*>::iterator it;
  it = the1DMap.find(name);
  //cout<<"fill 1d  "<<name<<endl;
  if (it == the1DMap.end()){

    //If the requested folder doesn't exist, we should create it first:
    HistManager::makeDirectory(folder);
    //theFile->ls();
    //cout<<"  ** Before the cd into a directory"<<endl;
    theFile->cd(folder.c_str());
    //cout<<"  ****** After the cd into a directory"<<endl;
    //theFile->ls();
    the1DMap[name] = new TH1F(name.c_str(),title.c_str(),bins,xmin,xmax);
    theFile->cd();
  }

  the1DMap[name]->Fill(x,weight);

}

void HistManager::fill1DHistUnevenBins(float x, std::string name, std::string title,
				       int bins, float *binEdges, float weight, std::string folder){
  std::map<std::string,TH1F*>::iterator it;
  it = the1DMap.find(name);
  if (it == the1DMap.end()){
    HistManager::makeDirectory(folder);
    theFile->cd(folder.c_str());
    the1DMap[name] = new TH1F(name.c_str(),title.c_str(),bins,binEdges);
    theFile->cd();
  }

  the1DMap[name]->Fill(x,weight);
}


void HistManager::fill2DHist(float x, float y, std::string name, std::string title,
			     int binsx, float xmin, float xmax,
			     int binsy, float ymin, float ymax, float weight, std::string folder){

  std::map<std::string,TH2F*>::iterator it;
  it = the2DMap.find(name);
  if (it == the2DMap.end()){
    HistManager::makeDirectory(folder);
    theFile->cd(folder.c_str());
    the2DMap[name] = new TH2F(name.c_str(),title.c_str(),binsx,xmin,xmax,binsy,ymin,ymax);
    theFile->cd();
  }

  the2DMap[name]->Fill(x,y,weight);
}

void HistManager::fill2DHistUnevenBins(float x, float y, std::string name, std::string title,
				       int binsx, float *binEdgesx,
				       int binsy, float *binEdgesy, float weight,  std::string folder){

  std::map<std::string,TH2F*>::iterator it;
  it = the2DMap.find(name);
  if (it == the2DMap.end()){
    HistManager::makeDirectory(folder);
    theFile->cd(folder.c_str());
    the2DMap[name] = new TH2F(name.c_str(),title.c_str(),binsx,binEdgesx,binsy,binEdgesy);
    theFile->cd();
  }

  the2DMap[name]->Fill(x,y,weight);
}


void HistManager::fillProfile(float x, float y, std::string name, std::string title,
			      int binsx, float xmin, float xmax,
			      float ymin, float ymax, float weight,  std::string folder){

  std::map<std::string,TProfile*>::iterator it;
  it = theProfMap.find(name);
  if (it == theProfMap.end()){
    HistManager::makeDirectory(folder);
    theFile->cd(folder.c_str());
    theProfMap[name] = new TProfile(name.c_str(),title.c_str(),binsx,xmin,xmax,ymin,ymax);
    theFile->cd();
  }

  theProfMap[name]->Fill(x,y,weight);

}


