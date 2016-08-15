## How to brew it

One should be able to run this code with just a couple commands:
* ```./run.py --all --proof [--june]``` - to produce the histograms (saved into a root file).
* ```./plot.py [--june, --mini]``` - to make plots out of those histograms.

## Main ingredients

* **myAna.C**: Selector to run over the data. It loops over events
and makes plots for each Silicon Pad, utilizing the HistManager tool.

* **run.py**: The script to start the *myAna*. It has some options:
  - ```-r RUNNUM```: specify a run number to run over: ```./run.py -r 3777```  
  - ```--june```: run over June's data (by default it assumes April's
data. Some JSON files are different wrt April and June).  
This option must be consistent with ```-r```. That is, the run number
should belong to June's data, e.g.  
```./run.py -r 4211 --june```  
  -```--all```: run over all the runs (April's Tb by default. Use
```--june``` to run over June's TB)  
  - ```--proof``` - finally, you can run this with PROOF!  
This is the way to go when running over full dataset: ```./run.py --all --proof```  

* **plot.py** - makes the plots from the final histogram. It also has various options:
  * ```-f FNAME``` - provide the input root file (produced by *run.py*)  
  * ```--june```   - plot the June's data. By default, it assumes April's data. Must be consistent with *FNAME* provided.
  * ```--hv HV2``` - specify which HV setting data to plot. Possible options: *600* and *800*. By default, it runs both.
  * ```--beam BEAM``` - specify the beam data to plot. Options: *ELE*, *PION*, by default plots both.
  * ```--fit```   - make some fits.
  * ```--mini``` - don't make all the plots, just those under ```if opt.mini``` in the code. This option is for testing new things.
  * ```--allruns```   - Make plots for each run separately (must be saved in the *FNAME*)  
  * ```-v```   - verbosity to print more stuff. You don't want that...  

* **resPlot.py** - takes as input the Root files which contain the
  Graphs with final time resolution measurement (produced by *plot.py*) and makes the plots.

* **makeJson.py** - reads the csv run summary data and creates json
  files.

