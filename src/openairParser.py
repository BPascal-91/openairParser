#!/usr/bin/env python3

import sys
import bpaTools


### Context applicatif
bpaTools.ctrlPythonVersion()
__AppName__     = bpaTools.getFileName(__file__)
__AppPath__     = bpaTools.getFilePath(__file__)
__AppVers__     = bpaTools.getVersionFile()
___AppId___     = __AppName__ + " v" + __AppVers__
__OutPath__     = __AppPath__ + "../out/"
__LogFile__     = __OutPath__ + __AppName__ + ".log"
oLog = bpaTools.Logger(___AppId___,__LogFile__)

def syntaxe():
    print("Airspace and Terrain description language (OpenAir) Converter")
    print("Call: " + __AppName__ + " <[drive:][path]filename> [<Option(s)>]")
    print("With:")
    print("  <[drive:][path]filename>       Openair source file")
    print("")
    print("  <Option(s)> - Complementary Options:")
    print("     -h				Help syntax")
    print("     -CleanLog       Clean log file before exec")
    print("")
    print("  Samples: " + __AppName__ + " ../tst/20191213_FFVP_sample_AIRSPACE_FRANCE_TXT_1911.txt -CleanLog")
    print("")
    print("  Resources")
    print("     OpenAir files: http://soaringweb.org/Airspace/  -or-  http://xcglobe.com/cloudapi/browser  -or-  http://cunimb.net/openair2map.php")
    print("     AIXM output format: http://www.aixm.aero/")
    return

### Context d'excecution
if len(sys.argv)<2:
    #oLog.isDebug = True     # Write the debug-messages in the log file
    sSrcPath = "../tst/"
    sSrcFile = sSrcPath + "20191213_FFVP_sample_AIRSPACE_FRANCE_TXT_1911.txt"
    #------- appels standards ---
    sys.argv += [sSrcFile, "-CleanLog"]
    #sys.argv += ["-h"]


sSrcFile = sys.argv[1]                              #Nom de fichier
oOpts = bpaTools.getCommandLineOptions(sys.argv)    #Arguments en dictionnaire
oLog.writeCommandLine(sys.argv)                     #Trace le contexte d'execution


if "-h" in oOpts:
    syntaxe()                                       #Aide en ligne
    oLog.closeFile()
else:
    if "-CleanLog" in oOpts:
        oLog.resetFile()                            #Clean du log si demandé
    
    bpaTools.createFolder(__OutPath__)              #Init dossier de sortie
   
    #Execution des traitements
    # ../..

    print()
    oLog.Report()
    