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
        self.oAixm = AixmAirspaces4_5.AixmAirspaces(oLog)
        self.resetZone()
        self.oDebug = dict()
        self.circleClockWise:str = None
        self.circleCenter:str = None
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
            self.oZone.sClass = "D"
            self.oZone.sType = aLine[1]
        elif aLine[1] in ["CTR1", "CTR2"]:
            self.oZone.sClass = "D"
            self.oZone.sType = "CTR"
        elif aLine[1] in ["CTA", "AWY"]:
            self.oZone.sClass = "A"
            self.oZone.sType = aLine[1]
        elif aLine[1] in ["R", "P", "ZIT", "TMZ", "RMZ"]:
            self.oZone.sClass = ""
            self.oZone.sType = aLine[1]
        elif aLine[1] in ["Q"]:
            self.oZone.sClass = ""
            self.oZone.sType = "D"                              #D [Danger Area.]
        elif aLine[1] in ["W", "VV"]:
            self.oZone.sClass = ""
            self.oZone.sType = "W"                              #W [Warning Area.]
            self.oZone.sCodeActivity = "GLIDER"
        elif aLine[1] in ["GP"]:
            self.oZone.sClass = ""
            self.oZone.sType = "PROTECT"                        #PROTECT [Airspace protected from specific air traffic.]
            self.oZone.sCodeActivity = "FAUNA"                  #pour création d'un Parc-Naturel
            self.oZone.codeId = aLine[1].upper()
        elif aLine[1] in ["ZSM", "MZS", "Bird", "Rapace"]:      #ZSM [Zone-Sensibilité-Majeur] / MSZ [Major-Sensibility-Zone]
            self.oZone.sClass = ""
            self.oZone.sType = "PROTECT"                        #PROTECT [Airspace protected from specific air traffic.]
            self.oZone.sCodeActivity = None                     #pour création d'une ZSM [Zone-Sensibilité-Majeur]
            self.oZone.codeId = aLine[1].upper()
        else:
            self.oLog.critical("parseClass error {}".format(aLine), outConsole=False)
        return

    #Sample of line: 'AN Parc du Jura (partie Sud)'
    def parseName(self, aLine:list) -> None:
        self.oZone.sName = " ".join(aLine[1:])

        if aLine[1] in ["CTR", "CTR1", "CTR2", "TMA", "CTA", "R", "P", "LTA", "W", "VV", "ZSM", "MSZ", "GP", "Bird", "Rapace", "ZIT", "RMZ", "TMZ", "TMZ/RMZ", "RMZ/TMZ", "AWY"]:
            self.oZone.sName = " ".join(aLine[2:])

            if aLine[1]==self.oZone.sType:
                True    #Ne rien faire
            elif aLine[1] in ["CTR", "TMA", "LTA"]:
                self.oZone.sClass = "D"
                self.oZone.sType = aLine[1]
            elif aLine[1] in ["CTR1", "CTR2"]:
                self.oZone.sClass = "D"
                self.oZone.sType = "CTR"
            elif aLine[1] in ["CTA", "AWY"]:
                self.oZone.sClass = "A"
                self.oZone.sType = aLine[1]
            elif aLine[1] in ["R", "P", "ZIT", "RMZ", "TMZ", "TMZ/RMZ", "RMZ/TMZ"]:
                self.oZone.sClass = ""
                self.oZone.sType = aLine[1]
            elif aLine[1] in ["W", "VV"]:
                self.oZone.sClass = ""
                self.oZone.sType = "W"                          #W [Warning Area.]
                self.oZone.sCodeActivity = "GLIDER"
            elif aLine[1] in ["GP"]:
                self.oZone.sClass = ""
                self.oZone.sType = "PROTECT"                    #PROTECT [Airspace protected from specific air traffic.]
                self.oZone.sCodeActivity = "FAUNA"
                self.oZone.codeId = aLine[1].upper()
            elif aLine[1] in ["ZSM", "MSZ", "GP", "Bird", "Rapace"]:
                self.oZone.sClass = ""
                self.oZone.sType = "ZSM"                        #ZSM [Zone-Sensibilité-Majeur] / MSZ [Major-Sensibility-Zone]
                self.oZone.codeId = aLine[1].upper()
            else:
                self.oLog.warning("parseName warning {}".format(aLine), outConsole=False)
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
        #                                               #No needs for read GUId=TMA16161
        #self.oZone.AseUid_mid                          #No needs for read UId=1560993
        sId:str = aLine[3].split("=")[1]                #Get value of Id=TMA16161
        if sId.lower().find("(identifiant-lpo)")<0:     #Ne pas intégrer l'exemple pour tests - '(Identifiant-LPO){0123456789}'
            self.oZone.codeId = sId                     #Store value of Id=TMA16161
        return

    #Sample of line: '*ADescr Réserve naturelle nationale de la Haute-Chaîne du Jura (published on 27/10/2020)'
    def parseADescr(self, aLine:list) -> None:
        self.oZone.sDesc =  " ".join(aLine[1:])
        return

    #Sample of line: '*AActiv [HX] Décollage ou survol possible ...'
    def parseAActiv(self, aLine:list) -> None:
        self.oZone.sCodeWorkHr = bpaTools.getContentOf(aLine[1], "[", "]")
        if len(aLine)>2 and aLine[2]:
            self.oZone.sRmkWorkHr = " ".join(aLine[2:])
        return

    #Sample of line: '*ADecla Yes'
    def parseADecla(self, aLine:list) -> None:
        if aLine[1].lower()=="yes" and (not self.oZone.sCodeWorkHr):
            self.oZone.sCodeWorkHr = "HX"
        return

    #Samples of source line:
    #   '*ATimes {"1": ["UTC(01/01->31/12)", "ANY(00:00->23:59)"]}'
    #   '*ATimes {"1": ["UTC(01/01->01/10)", "ANY(00:00->23:59)"], "2": ["UTC(01/12->31/12)", "ANY(00:00->23:59)"]}'
    #   '*ATimes {"1": ["UTC(01/01->31/12)", "MON to FRI(08:30->16:00)"]}'
    #   '*ATimes {"1": ["UTC(EDLST->SDLST)", "MON to FRI(07:00->21:00)"], "2": ["UTC(SDLST->EDLST)", "MON to FRI(06:00->22:00)"]}'
    #   '*ATimes {"1": ["UTC(01/01->31/12)", "ANY(SR/30/E->SS/30/L)"]}'
    def parseATimes(self, sLine:str) -> None:
        sDict:str = bpaTools.getContentOf(sLine, "{", "}", True)
        oATimes:dict = json.loads(sDict)
        self.oZone.addTimeSheduler(oATimes)
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

    #Generic function for parse the current line
    def parseLine(self, sSrcLine:str) -> None:
        sLine:str = sSrcLine.replace(","," ")    #Cleaning
        sLine = sLine.replace("\t"," ")         #Cleaning
        sLine = sLine.replace("  "," ")         #Cleaning
        if sLine == "":
            return
        aLine = sLine.split(" ")                #Tokenize
        if "" in aLine:
            aLine = list(filter(None, aLine))

        #### Header - Traitement des entêtes de zones
        if aLine[0] == "AC":
            if self.oZone.bBorderInProcess:
                self.resetZone()              #Reset current object
            self.parseClass(aLine)
            return

        elif aLine[0] == "AN":
            if self.oZone.bBorderInProcess:
                self.resetZone()              #Reset current object
            self.parseName(aLine)
            return

        elif aLine[0] in ["AH", "AL"]:
            if self.oZone.bBorderInProcess:
                self.resetZone()              #Reset current object
            self.parseAlt(aLine)
            return

        elif aLine[0] == "*AUID":
            self.parseAUID(aLine)
            return

        elif aLine[0] == "*ADescr":
            self.parseADescr(aLine)
            return

        elif aLine[0] == "*AActiv":
            self.parseAActiv(aLine)
            return

        elif aLine[0] == "*ADecla":
            self.parseADecla(aLine)
            return

        elif aLine[0] == "*ATimes":
            self.parseATimes(sSrcLine)
            return

        elif aLine[0] == "*ASeeNOTAM":
            self.parseASeeNOTAM(aLine)
            return

        elif aLine[0] in ["SP","SB","AT","AY","*AH2","*AL2","*AAlt","*AMzh","*AExSAT","*AExSUN","*AExHOL"]:
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
            if aLine[0] in ["AC","AN","AH","AL", "*AUID","*ADescr","*AActiv","*ADecla","*ATimes", "SP","SB","AT","AY","*AH2","*AL2","*AAlt","*AMzh","*AExSAT","*AExSUN","*AExHOL"]:
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
                self.oZone.makeArc(self.circleCenter, aLine, self.circleClockWise)
                self.circleClockWise = "+"      #Reset the default value

            else:
                self.oLog.critical("Type of line error: {0} - Airspace={1}".format(sSrcLine, self.oZone.getDesc()), outConsole=False)

        except Exception as e:
            self.oLog.critical("Error: {0} - {1} - Airspace={2}".format(str(e), sSrcLine, self.oZone.getDesc()), outConsole=False)
            #pass

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


