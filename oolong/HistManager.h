#ifndef _HistManager_H
#define _HistManager_H

#include <map>
#include <string>
#include <iostream>
#include "TObject.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TProfile.h"
#include "TFile.h"


class HistManager : public TObject {

  public:

  // constructor
  HistManager(TFile* myFile);

  // destructor
  ~HistManager();

  // write histograms the theFile
  //void writeHists(TFile* theFile);

  void makeDirectory(std::string f);
  // fill 1D histogram 
  void fill1DHist(float x, std::string name, std::string title,
                  int bins, float xmin, float xmax, float weight, std::string folder);

  void fill1DHistUnevenBins(float x, std::string name, std::string title,
                  int bins, float *binEdges, float weight, std::string folder);


  // fill 2D histogram
  void fill2DHist(float x, float y, std::string name, std::string title,
                  int binsx, float xmin, float xmax,
                  int binsy, float ymin, float ymax, float weight, std::string folder);

  void fill2DHistUnevenBins(float x, float y, std::string name, std::string title,
                            int binsx, float *binEdgesx,
                            int binsy, float *binEdgesy, float weight, std::string folder);


  // make a profile histogram
  void fillProfile(float x, float y, std::string name, std::string title,
                   int binsx, float xmin, float xmax,
                   float ymin, float ymax, float weight, std::string folder);

  ClassDef(HistManager, 1);


  protected:

  private:

  TFile* theFile;

  // map to hold histograms
  std::map<std::string,TH1F*> the1DMap;
  std::map<std::string,TH2F*> the2DMap;
  std::map<std::string,TProfile*> theProfMap;


};

#endif

