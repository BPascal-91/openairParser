#!/usr/bin/env python3

aixmParserLocalSrc  = "../../aixmParser/src/"
try:
    import bpaTools
except ImportError:
    ### Include local modules/librairies  ##
    import os, sys
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))
    import bpaTools

import OpenairReader


if __name__ == '__main__':
    ### Context applicatif
    callingContext      = "Paragliding-OpenAir-French-Files"        #Your app calling context
    linkContext         = "http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/"
    appName             = "openairParser"                           #or your app name
    appPath             = bpaTools.getFilePath(__file__)            #or your app path
    appVersion          = bpaTools.getVersionFile()                 #or your app version
    appId               = appName + " v" + appVersion
    outPath             = appPath + "../out/"
    logFile             = outPath + "_" + appName + ".log"

    bpaTools.createFolder(outPath)                                      #Init out folder
    oLog:bpaTools.Logger = bpaTools.Logger(appId,logFile,debugLevel=1)  #Init logger
    oLog.resetFile()                                                    #Clean du log

    ####  Source test file  ####
    sSrcPath:str = "../tst/"
    #sSrcFile = sSrcPath + "20191214_FFVP_BirdsProtect.txt"
    #sSrcFile = sSrcPath + "20200704_FFVP_ParcsNat_BPa.txt"
    #sSrcFile = sSrcPath + "20191213_FFVP_sample_AIRSPACE_FRANCE_TXT_1911.txt"
    #sSrcFile = sSrcPath + "20191213_FFVP_AIRSPACE_FRANCE_TXT_1911.txt"
    #sSrcFile = sSrcPath + "20191214_BPa_FR-BPa4XCsoar.txt"
    #sSrcFile = sSrcPath + "20190401_WPa_ParcCevennes.txt"
    #sSrcFile = sSrcPath + "20200704_RegisF_ParcsNat_ChampagneBourgogne.txt"
    #sSrcFile = sSrcPath + "20200805_PatrickB_ParcsNat_ChampagneBourgogne-BPa.txt"
    #sSrcFile = sSrcPath + "20200810_BPa_ParcsNat_ChampagneBourgogne.txt"
    #sSrcFile = sSrcPath + "20200729_SergeR_ParcNat_BaieDeSomme.txt"
    #sSrcFile = sSrcPath + "20200729_SergeR_ParcNat_Hourtin.txt"
    #sSrcFile = sSrcPath + "20201108_BPa_ZonesComplementaires.txt"
    #sSrcFile = sSrcPath + "20200510_BPa_FR-ZSM_Protection-des-rapaces.txt"
    #sSrcFile = sSrcPath + "20190510_FFVP_ParcBauges.txt"
    #sSrcFile = sSrcPath + "20191129_FFVL_ParcPassy.txt"
    #sSrcFile = sSrcPath + "20200120_FFVL_ParcAnnecyMaraisBoutDuLac.txt"
    #sSrcFile = sSrcPath + "20201204_FFVL_ZonesComplementaires.txt"
    #sSrcFile = sSrcPath + "20210101_sensitivearea_openair_BPa-ANSI.txt"
    #sSrcFile = sSrcPath + "20210104_FFVL_ParcBauges_BPa.txt"
    #sSrcFile = sSrcPath + "20210114_LTA-French1-HR_BPa-org.txt"
    sSrcFile = sSrcPath + "20210209_FFVL_ProtocolesParticuliers_BPa.txt"

    #Execution des traitements
    oParser = OpenairReader.OpenairReader(oLog)
    oParser.parseFile(sSrcFile)
    oParser.oAixm.parse2Aixm4_5(outPath, sSrcFile)

    #Clotures
    print()
    oLog.Report()
    oLog.closeFile()

