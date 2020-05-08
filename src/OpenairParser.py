#!/usr/bin/env python3

import sys
import bpaTools
import OpenairReader

### Context applicatif
bpaTools.ctrlPythonVersion()
__AppName__:str     = bpaTools.getFileName(__file__)
__AppPath__:str     = bpaTools.getFilePath(__file__)
__AppVers__:str     = bpaTools.getVersionFile()
___AppId___:str     = __AppName__ + " v" + __AppVers__
__OutPath__:str     = __AppPath__ + "../out/"
__LogFile__:str     = __OutPath__ + __AppName__ + ".log"
oLog = bpaTools.Logger(___AppId___,__LogFile__)

### Context d'excecution
if len(sys.argv)<2:
    ##oLog.isDebug = True     # Write the debug-messages in the log filezzz
    sSrcPath = "../tst/"
    sSrcFile = sSrcPath + "20191213_FFVP_sample_AIRSPACE_FRANCE_TXT_1911.txt"
    #sSrcFile = sSrcPath + "20191213_FFVP_AIRSPACE_FRANCE_TXT_1911.txt"
    #sSrcFile = sSrcPath + "20191214_BPa_FR-BPa4XCsoar.txt"
    #sSrcFile = sSrcPath + "20190401_WPa_ParcCevennes.txt"
    #sSrcFile = sSrcPath + "20191210_BPa_ZonesComplementaires.txt"
    #sSrcFile = sSrcPath + "20191213_BPa_FR-ZSM_Protection-des-rapaces.txt"
    #------- appels standards ---
    sys.argv += [sSrcFile, "-CleanLog"]
    #sys.argv += ["-h"]


def syntaxe() -> None:
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


    
####  Traitements  #####
sSrcFile:str = sys.argv[1]                              #Nom de fichier
oOpts:dict = bpaTools.getCommandLineOptions(sys.argv)   #Arguments en dictionnaire
oLog.writeCommandLine(sys.argv)                         #Trace le contexte d'execution


if "-h" in oOpts:
    syntaxe()                                       #Aide en ligne
    oLog.closeFile()
else:
    if "-CleanLog" in oOpts:
        oLog.resetFile()                            #Clean du log si demandé
    
    bpaTools.createFolder(__OutPath__)              #Init dossier de sortie
   
    #Execution des traitements
    oParser = OpenairReader.OpenairReader(oLog)
    oParser.parseFile(sSrcFile)
    oParser.oAixm.parse2Aixm4_5(__OutPath__, sSrcFile)

    #Clotures
    print()
    oLog.Report()
    oLog.closeFile()

