#!/usr/bin/env python3

import json
import AixmAirspaces4_5

aixmParserLocalSrc  = "../../aixmParser/src/"
try:
    import bpaTools
except ImportError:
    ### Include local modules/librairies  ##
    import os, sys
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))
    import bpaTools


ft = 0.3048      #foot in meter


def cleanLine(line:str) -> str:
    ret = line.strip()
    ret = ret.replace("\n","")
    ret = ret.replace("  "," ")
    #if line[0] == "*":
    #    return ""
    #else:
    return ret


class OpenairReader:

    def __init__(self, oLog:bpaTools.Logger=None) -> None:
        bpaTools.initEvent(__file__, oLog)
        self.oLog = oLog                    #Log file
        self.oAixm:AixmAirspaces4_5.AixmAirspaces = AixmAirspaces4_5.AixmAirspaces(oLog)
        self.resetZone()
        self.oDebug = dict()
        self.circleClockWise:str = None
        self.circleCenter:str = None
        self.sFilterClass:list = None       #Set Class filter - samples: ["ZSM"] or ["ZSM","GP"]
        self.sFilterType:list = None        #Set Type  filter - samples: ["RMZ"] or ["RMZ","TMZ"]
        self.sFilterName:list = None        #Set Name  filter -associate with bFilterNameLike=True  - samples: ["LYON"] or ["LYON","CHAMBERY","ANNECY"]
        self.bFilterNameLike = True         #Set Name  filter -associate with bFilterNameLike=False - samples: ["R 30 A"] or ["R 30 A","R 331","ZIT 11 (CREYS MALVILLE)","ZIT 14 (Grenoble)"]
        self.bFilterClassFound:bool = True  #Default value
        self.bFilterTypeFound:bool = True  #Default value
        self.bFilterNameFound:bool = True  #Default value
        return

    def resetZone(self) -> None:
        self.oZone:AixmAirspaces4_5.AixmAse4_5 = self.oAixm.getFactoryAirspace()
        return

    #Sample of line: 'AC A'
    def parseClass(self, aLine:list) -> None:
        self.oZone.sType = ""
        if aLine[1] in ["A", "B", "C", "D", "E", "F", "G", "OTHER"]:
            self.oZone.sClass = aLine[1]
            self.oZone.sType = "CLASS"
        elif aLine[1] in ["CTR", "TMA", "LTA"]:
            self.oZone.sClass = "D"                             #Default value
            self.oZone.sType = aLine[1]
        elif aLine[1] in ["CTR1", "CTR2"]:
            self.oZone.sClass = "D"                             #Default value
            self.oZone.sType = "CTR"
        elif aLine[1] in ["CTA", "AWY"]:
            self.oZone.sClass = "A"                             #Default value
            self.oZone.sType = aLine[1]
        elif aLine[1] in ["R", "ZRT", "P", "ZIT", "CBA"]:
            self.oZone.sClass = ""
            self.oZone.sType = aLine[1]
        elif aLine[1] in ["TMZ", "RMZ"]:
            self.oZone.sClass = "G"
            self.oZone.sType = "RAS"
            self.oZone.sLocalType = aLine[1]
        elif aLine[1] in ["Q"]:
            self.oZone.sClass = ""
            self.oZone.sType = "D"                              #D [Danger Area.]
        elif aLine[1] in ["W", "VV"]:
            self.oZone.sClass = ""
            self.oZone.sType = "D-OTHER"
            self.oZone.sCodeActivity = "GLIDER"
        elif aLine[1] in ["GP"]:
            self.oZone.sClass = ""
            self.oZone.sType = "PROTECT"                        #PROTECT [Airspace protected from specific air traffic.]
            self.oZone.sCodeActivity = "FAUNA"                  #pour création d'un Parc-Naturel
            self.oZone.sId = aLine[1].upper()
        elif aLine[1] in ["ZSM", "MZS", "Bird", "Rapace"]:      #ZSM [Zone-Sensibilité-Majeur] / MSZ [Major-Sensibility-Zone]
            self.oZone.sClass = ""
            self.oZone.sType = "ZSM"                            #ZSM [Zone-Sensibilité-Majeur] / MSZ [Major-Sensibility-Zone]
            self.oZone.sCodeActivity = None                     #pour création d'une ZSM [Zone-Sensibilité-Majeur]
            self.oZone.sId = aLine[1].upper()
        elif aLine[1] in ["FFVL"]:                              #Protocoles particulier signés FFVL - Vol libre
            self.oZone.sClass = aLine[1]
            self.oZone.sType = aLine[1] + "-Prot"               #Indicateur protocole particulier
            self.oZone.sCodeActivity = "PARAGLIDER"
        elif aLine[1] in ["FFVP"]:                              #Protocoles particulier signés FFVP - Planeurs / Vol à voile
            self.oZone.sClass = aLine[1]
            self.oZone.sType = aLine[1] + "-Prot"               #Indicateur protocole particulier
            self.oZone.sCodeActivity = "GLIDER"
        else:
            self.oZone.sClass = ""             #Default value
            self.oZone.sType = aLine[1]
            self.oLog.warning("parseClass() default affected values {0}".format(aLine), outConsole=False)
        return

    #Sample of line: 'AN Parc du Jura (partie Sud)'
    def parseName(self, aLine:list, sLine:str) -> None:
        sLine = sLine[len(aLine[0])+1:]
        sLine = sLine.replace("\t"," ")             #Cleaning
        sLine = sLine.replace("  "," ")             #Cleaning
        sLine = sLine.replace(" (SeeNotam)", "")    #Cleaning
        sLine = sLine.replace(" / SeeNotam)", ")")  #Cleaning
        aTocken:list = ["App(", "Twr("]             #Cleaning ...
        for sTocken in aTocken:
            leftPos = sLine.find(sTocken)
            if leftPos>=0:
                rightPos = sLine.find(")", leftPos)
                if leftPos>=0 and rightPos>=0:
                    sLine = sLine[:leftPos] + sLine[rightPos+1:]
        sLine = sLine.strip()                       #Cleaning


        #Context and Cleaning
        aTocken:list = ["BIRD","FAUNA","NATURE","NO-NOISE","PARAGLIDER","HANGGLIDER","GLIDER","TOWING","BALLOON","SPORT","ULM","DROP","PARACHUTE","ACROBAT","MILOPS","AIRGUN","MISSILES","NAVAL","ANTIHAIL","ARTILERY","ASCENT","ATS","BLAST","SHOOT","EQUIPMENT","EXERCISE","FIRE","GAZ","IND-NUCLEAR","IND-OIL","JETCLIMB","LASER","PROCEDURE","REFUEL","TRG","VIP","VIP-PRES"]
        aEndSep:list = [")"," "]
        bFound:bool = False
        sContext:str = str(bpaTools.getContentOf(sLine, " (", ")"))                  #Extraire 1ere instance

        #Map 09/02/2021
        #if sLine.find("(GLIDER)")>=0:
        #    print()

        #Gestion du cas ou la frequence radio est précisé exp- "FFVP-Prot RMZ Selestat App(120.700) (GLIDER)"
        if bpaTools.isFloat(sContext):
            sContext:str = str(bpaTools.getContentOf(sLine, " (", ")", iNoInst=2))   #Extraire 2ieme instance
        sContext = "(" + sContext.lower() + ")"
        for sTocken in aTocken:
            for sEndSep in aEndSep:
                if sContext.find("(" + sTocken.lower() + sEndSep)>=0:
                    self.oZone.sCodeActivity = sTocken
                    sLine = sLine.replace("(" + sTocken + sEndSep, "")      #Cleaning
                    sLine = sLine.strip()                                   #Cleaning
                    bFound = True
                if bFound: break
            if bFound: break

        if aLine[1] in ["FFVL","FFVP","CTR", "CTR1", "CTR2", "TMA", "CTA", "R", "P", "Q", "LTA", "W", "VV", "ZSM", "MSZ", "PROTECT", "GP", "Bird", "Rapace", "RTBA", "ZIT", "ZRT", "RMZ", "TMZ", "TMZ/RMZ", "RMZ/TMZ", "PJE", "TRVL", "TRPLA", "AWY"]:
            sLine = sLine.replace(aLine[1] + " ", "")    #Cleaning

            if aLine[1]==self.oZone.sType:
                True    #Ne rien faire
            elif aLine[1] in ["FFVL","FFVP"]:                   #Protocole particulier
                #self.oZone.sClass                              #No change class!
                self.oZone.sType = aLine[1]
            elif aLine[1] in ["CTR", "TMA", "LTA", "CBA"]:
                #self.oZone.sClass = "D"                        #No change class!
                self.oZone.sType = aLine[1]
            elif aLine[1] in ["CTR1", "CTR2"]:
                #self.oZone.sClass = "D"                        #No change class!
                self.oZone.sType = "CTR"
            elif aLine[1] in ["CTA", "AWY"]:
                #self.oZone.sClass = "A"                        #No change class!
                self.oZone.sType = aLine[1]
            elif aLine[1] in ["P", "R", "RTBA", "ZIT", "RMZ", "TMZ", "TMZ/RMZ", "RMZ/TMZ"]:
                self.oZone.sClass = ""
                self.oZone.sType = aLine[1]
            elif aLine[1] in ["ZRT"]:
                self.oZone.sClass = "R"
                self.oZone.sType = aLine[1]
            elif aLine[1] in ["PROTECT"]:
                #self.oZone.sClass = "Q, W or ZSM"              #No change class!
                self.oZone.sType = aLine[1]
            elif aLine[1] in ["PJE", "TRVL", "TRPLA"]:
                #self.oZone.sClass                              #No change class!
                #self.oZone.sType                               #No change type !
                self.oZone.sLocalType = aLine[1]
            elif aLine[1] in ["W", "VV"]:
                self.oZone.sClass = ""
                self.oZone.sType = "W"                          #W [Warning Area.]
            elif aLine[1] in ["GP"]:
                self.oZone.sClass = ""
                self.oZone.sType = "PROTECT"                    #PROTECT [Airspace protected from specific air traffic.]
                self.oZone.sCodeActivity = "FAUNA"
                self.oZone.sId = aLine[1].upper()
            elif aLine[1] in ["ZSM", "MSZ", "Bird", "Rapace"]:
                self.oZone.sClass = ""
                self.oZone.sType = "ZSM"                        #ZSM [Zone-Sensibilité-Majeur] / MSZ [Major-Sensibility-Zone]
                self.oZone.sId = aLine[1].upper()
            else:
                self.oLog.warning("parseName warning {}".format(aLine), outConsole=False)

        self.oZone.sName = sLine
        return

    #Samples of line: 'AL SFC', 'AH 985FT AGL', 'AH 1000FT AMSL', 'AH FL075' ...
    def parseAlt(self, aLine:list) -> None:
        codeDistVer = valDistVer = uomDistVer = None

        if aLine[1].upper() == "FL":                    #aLine = ['AH','FL','195']
            codeDistVer = "STD"
            valDistVer = aLine[2]
            uomDistVer = aLine[1].upper()
        elif aLine[1][:2].upper() == "FL":                #aLine = ['AH','FL115']
            codeDistVer = "STD"
            valDistVer = aLine[1][2:]
            uomDistVer = aLine[1][:2].upper()
        elif aLine[1][-2:].upper() == "FT":             #aLine = ['AH','2500FT','AMSL']
            codeDistVer = "ALT"
            valDistVer = aLine[1][:-2]
            uomDistVer = aLine[1][-2:].upper()
        elif aLine[1][-1:].upper() == "F":              #aLine = ['AH','2500F','AMSL']
            codeDistVer = "ALT"
            valDistVer = aLine[1][:-1]
            uomDistVer = "FT"
        elif aLine[1][-1:].upper() == "M":              #aLine = ['AH','2500M','AMSL']
            codeDistVer = "ALT"
            valDistVer = int(int(aLine[1][:-1]) / ft)   #Convert meter 2 feet
            uomDistVer = "FT"
        elif aLine[1].upper() in ["SFC", "GND"]:        #aLine = ['AL','SFC'] or ['AL','GND']
            codeDistVer = "HEI"
            valDistVer = 0
            uomDistVer = "FT"
        elif aLine[1].upper() in ["UNL", "UNLIM"]:      #aLine = ['AL','UNL']
            codeDistVer = "STD"
            valDistVer = 999
            uomDistVer = "FL"
        else:
            if len(aLine)>2:
                if aLine[2].upper() == "FT":         #aLine = ['AH','4500','FT','AMSL']
                    codeDistVer = "ALT"
                    valDistVer = aLine[1]
                    uomDistVer = aLine[2].upper()
                elif aLine[2].upper() == "F":         #aLine = ['AH','4500','F','AMSL']
                    codeDistVer = "ALT"
                    valDistVer = aLine[1]
                    uomDistVer = "FT"
                elif aLine[2].upper() == "M":         #aLine = ['AH','4500','M','AMSL']
                    codeDistVer = "ALT"
                    valDistVer = int(int(aLine[1]) / ft)   #Convert meter 2 feet
                    uomDistVer = "FT"
                else:
                    self.oLog.critical("parseAlt error {}".format(aLine), outConsole=False)
            else:
                self.oLog.critical("parseAlt error {}".format(aLine), outConsole=False)

        if ("ASFC" in aLine) or ("AGL" in aLine):
            codeDistVer = "HEI"

        if aLine[0] == "AH":
            self.oZone.sUpper = " ".join(aLine[1:])
            self.oZone.codeDistVerUpper = codeDistVer
            self.oZone.valDistVerUpper = valDistVer
            self.oZone.uomDistVerUpper = uomDistVer
        elif aLine[0] == "AL":
            self.oZone.sLower = " ".join(aLine[1:])
            self.oZone.codeDistVerLower = codeDistVer
            self.oZone.valDistVerLower = valDistVer
            self.oZone.uomDistVerLower = uomDistVer
        return

    #Sample of line: '*AUID GUId=TMA16161 UId=1560993 Id=TMA16161'
    def parseAUID(self, aLine:list) -> None:
        oIds:dict = {}
        for o in aLine[1:]:
            aO = o.split("=")
            oIds.update({aO[0]:aO[1]})
        sGUId:str = oIds.get("GUId", None)
        if sGUId!="!":
            self.oZone.sGUId = sGUId
        sUId:str = oIds.get("UId", None)
        if sUId!="!":
            self.oZone.sUId = sUId
        sId:str = oIds.get("Id", None)
        if sId.lower().find("(identifiant-lpo)")<0:      #Ne pas intégrer l'exemple pour tests - '(Identifiant-LPO){0123456789}'
            self.oZone.sId = sId
        return

    #Sample of line: '*AActiv [HX] Décollage ou survol possible ...'
    def parseAActiv(self, aLine:list, sLine:str) -> None:
        self.oZone.sCodeWorkHr = bpaTools.getContentOf(sLine, "[", "]")
        if len(aLine)>2 and aLine[2]:
            self.oZone.sRmkWorkHr = sLine[sLine.find("]")+1:].strip()
        return

    #Sample of line: '*ADecla Yes'
    def parseADecla(self, aLine:list) -> None:
        if aLine[1].lower()=="yes" and (not self.oZone.sCodeWorkHr):
            self.oZone.sCodeWorkHr = "HX"
        return

    #Sample of line: '*ASeeNOTAM Yes'
    def parseASeeNOTAM(self, aLine:list) -> None:
        if aLine[1].lower()=="yes":
            sMsg:str = "See NOTAM"
            if not self.oZone.sRmkWorkHr:
                self.oZone.sRmkWorkHr = sMsg
            elif self.oZone.sRmkWorkHr.lower().find("notam")<0:
                self.oZone.sRmkWorkHr += " / " + sMsg
        return

    #Samples of source line:
    #   '*ATimes {"1": ["UTC(01/01->31/12)", "ANY(00:00->23:59)"]}'
    #   '*ATimes {"1": ["UTC(01/01->01/10)", "ANY(00:00->23:59)"], "2": ["UTC(01/12->31/12)", "ANY(00:00->23:59)"]}'
    #   '*ATimes {"1": ["UTC(01/01->31/12)", "MON to FRI(08:30->16:00)"]}'
    #   '*ATimes {"1": ["UTC(EDLST->SDLST)", "MON to FRI(07:00->21:00)"], "2": ["UTC(SDLST->EDLST)", "MON to FRI(06:00->22:00)"]}'
    #   '*ATimes {"1": ["UTC(01/01->31/12)", "ANY(SR/30/E->SS/30/L)"]}'
    def parseATimes(self, aLine:list, sLine:str) -> None:
        sDict:str = bpaTools.getContentOf(sLine, "{", "}", bRetSep=True)
        oATimes:dict = json.loads(sDict)
        self.oZone.addTimeSheduler(oATimes)
        return

    #Generic function for parse the current line
    def parseLine(self, sSrcLine:str) -> None:
        sLine:str = sSrcLine.replace(","," ")   #Cleaning
        sLine = sLine.replace("\t"," ")         #Cleaning
        sLine = sLine.replace("  "," ")         #Cleaning
        if sLine == "":
            return
        aLine = sLine.split(" ")                #Tokenize
        if "" in aLine:
            aLine = list(filter(None, aLine))

        #### Header - Traitement des entêtes de zones
        if aLine[0] == "AC":
            if self.sFilterClass:           #Gestion du filtrage
                if aLine[1] in self.sFilterClass:
                    self.bFilterClassFound = True
                else:
                    self.bFilterClassFound = False
                    return                  #Break
            if self.oZone.bBorderInProcess:
                self.resetZone()            #Reset current object
            self.parseClass(aLine)
            return

        elif not self.bFilterClassFound:    #Gestion du filtrage
            return                          #Interruption des traitements si la zone n'est pas conforme au filtrage

        elif aLine[0] == "AN":
            if self.sFilterName:            #Gestion du filtrage
                self.bFilterNameFound = False
                for sTocken in self.sFilterName:
                    self.bFilterNameFound = self.bFilterNameFound or bool(sSrcLine.lower().find(sTocken.lower())>=0)
                if not self.bFilterNameFound:
                    return                  #Break
            if self.oZone.bBorderInProcess:
                self.resetZone()            #Reset current object
            self.parseName(aLine, sSrcLine)
            return

        elif not self.bFilterNameFound:     #Gestion du filtrage
            return                          #Interruption des traitements si la zone n'est pas conforme au filtrage

        if self.sFilterType and self.oZone.sType:    #Gestion du filtrage
            if self.oZone.sType in self.sFilterType:
                self.bFilterTypeFound = True
            else:
                self.bFilterTypeFound = False
                return                      #Interruption des traitements si la zone n'est pas conforme au filtrage

        if aLine[0] in ["AH", "AL"]:
            if self.oZone.bBorderInProcess:
                self.resetZone()            #Reset current object
            self.parseAlt(aLine)
            return

        elif aLine[0] == "*AUID":
            self.parseAUID(aLine)
            return

        elif aLine[0] == "*ADescr":
            self.oZone.sDesc = sSrcLine[len(aLine[0])+1:]
            return

        elif aLine[0] == "*AActiv":
            self.parseAActiv(aLine, sSrcLine)
            return

        elif aLine[0] == "*ADecla":
            self.parseADecla(aLine)
            return

        elif aLine[0] == "*ASeeNOTAM":
            self.parseASeeNOTAM(aLine)
            return

        elif aLine[0] == "*AMhz":
            self.oZone.sMhz = sSrcLine[len(aLine[0])+1:]
            return

        elif aLine[0] == "*ATimes":
            self.parseATimes(aLine, sSrcLine)
            return

        elif aLine[0] in ["SP","SB","AT","AY","*AH2","*AL2","*AAlt","*AExSAT","*AExSUN","*AExHOL"]:
            return    #Pas besoin de récupération...

        elif sLine[0] == "*":
            return    #Pas besoin de récupération...

        else:
            if not self.oZone.isCorrectHeader():
                self.oLog.critical("Header error before line {}".format(sSrcLine), outConsole=False)
                return

        #### Airspace - Enregistrement de la zone
        if self.oZone.getID() == None:
            self.oZone.bBorderInProcess = True
            self.oAixm.addAirspace(self.oZone)
            #self.oLog.info("{}".format(self.oZone.getAllProperties()), outConsole=True)

        #### Border - Traitement des bordures géographiques de zones
        try:
            if aLine[0] in ["AC","AN","AH","AL","*AUID","*ADescr","*AActiv","*ADecla","*ASeeNOTAM","*AMhz","*ATimes", "SP","SB","AT","AY","*AH2","*AL2","*AAlt","*AExSAT","*AExSUN","*AExHOL"]:
                None    #Traité plus haut dans la parties 'header'

            elif aLine[0] == "DP":              #DP = Polygon pointC - sample 'DP 44:54:52 N 005:02:35 E'
                self.oZone.makePoint(aLine)

            elif aLine[0] == "V":               #V = Variable assignment
                #V x=n;     Variable assignment.
                #  D={+|-}         : sets direction for: DA and DB records
                #                  : '-' means counterclockwise direction; '+' is the default
                #  X=coordinate    : sets the center for the following records: DA, DB, and DC
                #  W=number        : sets the width of an airway in nm (NYI)
                #  Z=number        : sets zoom level at which the element becomes visible
                if aLine[1] == "D=+":           #sample 'V D=+'
                    self.circleClockWise = "+"
                elif aLine[1] == "D=-":         #sample 'V D=-'
                    self.circleClockWise = "-"
                elif aLine[1][0:2] == "X=":     #sample 'V X=48:36:03 N 003:49:00 W'
                    self.circleCenter = aLine
                else:
                    self.oLog.critical("Type of line error: {0} - Airspace={1}".format(sSrcLine, self.oZone.getDesc()), outConsole=False)

            elif aLine[0] == "DC":              #DC radius; draw a circle (center taken from the previous V X=...; radius in nm; sample 'DC 3'
                self.oZone.makeCircle(self.circleCenter, aLine[1])
                self.circleClockWise = "+"      #Reset the default value

            elif aLine[0] == "DB":              #Just an Arc; sample 'DB 44:54:52 N 005:02:35 E,44:55:20 N 004:54:10 E'
                if "" in aLine:
                    aLine = list(filter(None, aLine))
                self.oZone.makeArc(self.circleCenter, sSrcLine, self.circleClockWise)
                self.circleClockWise = "+"      #Reset the default value

            else:
                self.oLog.critical("Type of line error: {0} - Airspace={1}".format(sSrcLine, self.oZone.getDesc()), outConsole=False)

        except Exception as e:
            self.oLog.critical("Error: {0} - {1} - Airspace={2}".format(str(e), sSrcLine, self.oZone.getDesc()), outConsole=False)
            #pass

        return

    def setFilters(self, sFilterClass:list=None, sFilterType:list=None, sFilterName:list=None, bFilterNameLike:bool=True) -> None:
        self.sFilterClass = sFilterClass
        self.sFilterType = sFilterType
        self.sFilterName = sFilterName
        self.bFilterNameLike = bFilterNameLike
        return

    def parseFile(self, sSrcFile:str) -> None:
        #Execution des traitements
        fopen = open(sSrcFile, "rt", encoding="cp1252", errors="ignore")     #old "utf-8"
        lines = fopen.readlines()
        sMsg = "Parsing openair file - {}".format(sSrcFile)
        self.oLog.info("Debug object {}".format(sMsg), outConsole=True)
        barre = bpaTools.ProgressBar(len(lines), 20, title=sMsg)
        idx = 0
        for line in lines:
            idx+=1
            lig = cleanLine(line)
            self.parseLine(lig)
            barre.update(idx)

        barre.reset()
        print()
        self.oLog.info("--> {} Openair parsing zones".format(len(self.oAixm.oAirspaces)), outConsole=True)

        if self.oLog.isDebug:
            self.oLog.debug("Debug object {}".format(self.oDebug.keys()), outConsole=False)
        return


