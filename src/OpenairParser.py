#!/usr/bin/env python3

import sys
import OpenairReader

aixmParserLocalSrc  = "../../aixmParser/src/"
try:
    import bpaTools
except ImportError:
    ### Include local modules/librairies  ##
    import os  #, sys
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))
    import bpaTools


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


if __name__ == '__main__':
    ### Context applicatif
    bpaTools.ctrlPythonVersion()
    __AppName__:str     = bpaTools.getFileName(__file__)
    __AppPath__:str     = bpaTools.getFilePath(__file__)
    __AppVers__:str     = bpaTools.getVersionFile()
    ___AppId___:str     = __AppName__ + " v" + __AppVers__
    __OutPath__:str     = __AppPath__ + "../out/"
    __LogFile__:str     = __OutPath__ + "_" + __AppName__ + ".log"
    oLog = bpaTools.Logger(___AppId___,__LogFile__)

    ### Context d'excecution
    if len(sys.argv)<2:
        ##oLog.isDebug = True     # Write the debug-messages in the log filezzz
        sSrcPath = "../tst/"
        sSrcFile = sSrcPath + "20210114_LTA-French1-HR_BPa-org.txt"
        #------- appels standards ---
        sys.argv += [sSrcFile, "-CleanLog"]
        #sys.argv += ["-h"]

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
