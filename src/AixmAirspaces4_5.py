#!/usr/bin/env python3

import math
from pyproj import Proj, transform
from lxml import etree

aixmParserLocalSrc  = "../../aixmParser/src/"
try:
    import bpaTools
except ImportError:
    ### Include local modules/librairies  ##
    import os, sys
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))
    import bpaTools


pWGS = Proj("epsg:4326")            # EPSG:4326 = WGS84 / Geodetic coordinate system for World  :: Deprecated format --> Proj(init="epsg:4326")
nm = 1852                           # Nautic Mile to meters


def getCoordonnees(sLine:str, bSecondPoint:bool=False) -> (str,str):
    sLat:str = None
    sLon:str = None
    aLat = ["N","S"]
    aLon = ["E","W","O"]
    aHead = ["DP", "DB", "V X="]

    try:
        """ #Old source
        if aLine[0] == "V" and aLine[1][:2] == "X=":
            #Openair format - V X=48:36:03 N 003:49:00 W
            aLine[1] = aLine[1][2:]     #Cleaning start coords

        if aLine[0] in ["DP", "DB", "V"]:
            #Openair format - DP 47:36:04 N 000:25:56 W
            #Openair format - DP 47:36:04 N 000:25:56W
            #Openair format - DP 47:36:04N 000:25:56 W
            #Openair format - DP 47:36:04N 000:25:56W
            #Openair format - DP 04:53:56.605 N 052:15:37.871 W
            #Openair format - V X=48:36:03 N 003:49:00 W
            #Openair format - V X=48:36:03 N 003:49:00W
            #Openair format - V X=48:36:03N 003:49:00 W
            #Openair format - V X=48:36:03N 003:49:00W
            #Openair format - DB 44:54:52N 005:02:35 E, 44:55:20N 004:54:10 E
            #Openair format - DB 44:54:52N 005:02:35 E, 44:55:20N 004:54:10E
            #Openair format - DB 44:54:52N 005:02:35E, 44:55:20N 004:54:10 E
            #Openair format - DB 44:54:52N 005:02:35E, 44:55:20N 004:54:10E


            if len(aLine[1])>1 and aLine[1][-1].upper() in aLat:
                sLat = aLine[1]
            elif aLine[2].upper() in aLat:
                sLat = aLine[1]+aLine[2]

            if len(aLine[2])>1 and aLine[2][-1].upper() in aLon:
                sLon = aLine[2]
            if sLon==None and len(aLine) > 2:
                if aLine[3][-1].upper() in aLon:
                    if len(aLine[3])==1:
                        sLon = aLine[2]+aLine[3]
                    else:
                        sLon = aLine[3]
            if sLon==None and len(aLine) > 3:
                if aLine[4].upper() in aLon:
                    if len(aLine[4])==1:
                        sLon = aLine[3]+aLine[4]
                    else:
                        sLon = aLine[4]
            """

        if   isinstance(sLine, str):
            aLine:list = sLine.split(" ")
            sCleanLine:str = sLine[len(aLine[0])+1:]        #Suppression de l'entete ["DP", "DB", "V"]
        elif isinstance(sLine, list):
            aLine:list = sLine
            sCleanLine:str = " ".join(aLine[1:])            #Suppression de l'entete ["DP", "DB", "V"]

        if any(sCleanLine[:len(sTocken)]==sTocken for sTocken in aHead):
            raise Exception("Header error")

        sCleanLine = sCleanLine.replace(" ", "")            #Suppression des espaces non significatif
        sCleanLine = sCleanLine.replace("X=", "")           #Eventuelle suppression de fin d'entete centre d'arc ou de cercle
        aCoords = sCleanLine.split(",")

        if bSecondPoint:
            if len(aCoords)<2:
                raise Exception("Format error")
            sCoods:str = str(aCoords[1])
        else:
            sCoods:str = str(aCoords[0])

        sLat:str = ""
        sLon:str = ""
        bParseLon:bool = False
        for sChar in sCoods:
            if sChar in aLat:                       #aLat = ["N","S"]
                sLat += sChar
                bParseLon = True
                continue
            if sChar in aLon:                       #aLon = ["E","W","O"]
                if sChar == "O":    sChar="W"
            if bParseLon:
                sLon += sChar
            else:
                sLat += sChar

        #NEW - Native cleanning (without D.d convertion)
        sLat, sLon = bpaTools.geoStr2coords(sLat, sLon, outFrmt="dms")
        return sLat, sLon

    except Exception as e:
        sHeader = "[" + bpaTools.getFileName(__file__) + "." + getCoordonnees.__name__ + "()] "
        sMsg = "/!\ Parsing Line Error - {}".format(sLine)
        raise Exception(sHeader + sMsg + " / " + str(e))


#########   Cirlce of Airspace border  ########
class AixmCircle4_5:
    def __init__(self) -> None:
        self.openairType:str = None
        self.geoLatCen:str = None       #<geoLatCen>422605.8454N</geoLatCen>
        self.geoLongCen:str = None      #<geoLongCen>0160951.2347E</geoLongCen>
        self.codeDatum:str = "WGE"      #Const
        self.valRadius:str = None       #<valRadius>5.0121</valRadius>
        self.uomRadius:str = "NM"       #Const
        #self.valCrc                    #Don't check values... <valCrc>0E7C2798</valCrc>
        return

    def loadCircle(self, aCenter:list, fRadius:float) -> bool:
        #aCenter = 'V X=48:36:03 N 003:49:00 W'
        try:
            self.openairType = "Circle"
            lat, lon = getCoordonnees(aCenter)
            self.geoLatCen = lat
            self.geoLongCen = lon
            self.valRadius = fRadius
            return True
        except:
            raise


#########   Vector of Airspace border  ########
class AixmAvx4_5:
    def __init__(self) -> None:
        self.openairType:str = None
        #self.GbrUid:str = None             #None
        self.codeType:str = None
        self.geoLat:str = None              #<geoLat>422605.8454N</geoLat>
        self.geoLong:str = None             #<geoLong>0160951.2347E</geoLong>
        self.codeDatum:str = "WGE"          #Const
        self.geoLatArc:str = None
        self.geoLongArc:str = None
        self.valRadiusArc:str = None
        self.uomRadiusArc:str = "NM"        #Const
	    #self.valCrc:str = None             #Don't check values...  <valCrc>0E7C2798</valCrc>
        #self.txtRmk :str = None            #No data...
        return

    def loadPoint(self, aLine:list) -> bool:
        #aLine = DP 47:36:04 N 000:25:56 W
        try:
            self.openairType = "Point"
            self.codeType = "GRC"           #Great Circle' or 'Rhumb Line' segment
            lat, lon = getCoordonnees(aLine)
            self.geoLat = lat
            self.geoLong = lon
            return True
        except:
            raise

    def loadArc(self, aCenter:list, sPoint2Point:str, circleClockWise:str) -> bool:
        #aCenter = DP 47:36:04 N 000:25:56 W
        #sPoint2Point = 'DB 44:54:52 N 005:02:35 E, 44:55:20 N 004:54:10 E'
        try:
            self.openairType = "Arc"
            if circleClockWise == "-":
                self.codeType = "CCA"       #Counter Clock wise Arc
            else:
                self.codeType = "CWA"       #Clock Wise Arc

            #Centre de l'arc
            latC, lonC = getCoordonnees(aCenter)
            latCdd, lonCdd = bpaTools.geoStr2coords(latC, lonC, "dd")
            self.geoLatArc = latC
            self.geoLongArc = lonC

            #Point d'entrée de l'arc
            latE, lonE = getCoordonnees(sPoint2Point)
            latEdd, lonEdd = bpaTools.geoStr2coords(latE, lonE, "dd")
            self.geoLat = latE
            self.geoLong = lonE

            #Point de sortie de l'arc
            latS, lonS = getCoordonnees(sPoint2Point, bSecondPoint=True)
            latSdd, lonSdd = bpaTools.geoStr2coords(latS, lonS, "dd")

            #Détermination du rayon de l'arc / par moyenne des deux rayons retenues
            srs = Proj(proj="ortho", lat_0=latCdd, lon_0=lonCdd)
            #  a/ Calcul du rayon entre le centre et le point d'entré du cercle
            start_xE, start_yE = transform(p1=pWGS, p2=srs, x=latEdd, y=lonEdd)
            radiusE = math.sqrt(start_xE**2+start_yE**2)                    # Meter

            #  b/ Calcul du rayon entre le centre et le point de sortie du cercle
            start_xS, start_yS = transform(p1=pWGS, p2=srs, x=latSdd, y=lonSdd)
            radiusS = math.sqrt(start_xS**2+start_yS**2)                    # Meter

            #  c/ Retenir la moyenne des 2 rayons calculés afin de limiter les erreurs de déclallages
            radius:float = (radiusE + radiusS) / 2                          # Meter
            self.valRadiusArc = round(radius/nm, 2)                         # Nautic Mile

            return True
        except:
            raise

###############   Time schedule for Airspace area  ###########
class AixmTimsh4_5:
    """ standard aixm-4.5 output samples              // associate to POAF convertion samples
		<Att>
			<codeWorkHr>TIMSH</codeWorkHr>
		<Timsh>                                       '*ATimes {"1": ["UTC(01/01->31/12)", "WD(08:00->18:00)"], "2":...}'
			<codeTimeRef>UTCW</codeTimeRef>
			<dateValidWef>01-01</dateValidWef>
			<dateValidTil>31-12</dateValidTil>
			<codeDay>WD</codeDay>
			<codeDayTil>WD</codeDayTil>
			<timeWef>08:00</timeWef>
			<timeTil>18:00</timeTil>
		</Timsh>
		<Timsh>                                       '*ATimes {{"1":... , "2": ["UTC(EDLST->SDLST)", "SAT to SUN(08:30->16:00)"]}'
			<codeTimeRef>UTC</codeTimeRef>
			<dateValidWef>EDLST</dateValidWef>
			<dateValidTil>SDLST</dateValidTil>
			<codeDay>SAT</codeDay>
			<codeDayTil>SUN</codeDayTil>
			<timeWef>08:30</timeWef>
			<timeTil>16:00</timeTil>
		</Timsh>
        <Timsh>                                       '*ATimes {{"1":... , "2":... , "3": ["UTC(01/01->31/12)", "ANY(SR/30/E->SS/30/L)"]}'
			<codeTimeRef>UTC</codeTimeRef>
			<dateValidWef>01-01</dateValidWef>
			<dateValidTil>31-12</dateValidTil>
			<codeDay>ANY</codeDay>
			<codeEventWef>SR</codeEventWef>
			<timeRelEventWef>30</timeRelEventWef>
			<codeCombWef>E</codeCombWef>
			<codeEventTil>SS</codeEventTil>
			<timeRelEventTil>30</timeRelEventTil>
			<codeCombTil>L</codeCombTil>
		</Timsh>
    </Att>
    """

    def __init__(self) -> None:
        self.sCodeTimeRef:str = None
        self.sDateValidWef:str = None
        self.sDateValidTil:str = None
        self.sCodeDay:str = None
        self.sCodeDayTil:str = None
        self.sTimeWef:str = None
        self.sTimeTil:str = None
        self.sCodeEventWef:str = None
        self.sTimeRelEventWef:str = None
        self.sCodeCombWef:str = None
        self.sCodeEventTil:str = None
        self.sTimeRelEventTil:str = None
        self.sCodeCombTil:str = None

    def getXml(self) -> etree:
        oTsh:etree = etree.Element("Timsh")
        if not self.sCodeTimeRef in [None, ""]:
            oItem = etree.SubElement(oTsh, "codeTimeRef")
            oItem.text = self.sCodeTimeRef
        if not self.sDateValidWef in [None, ""]:
            oItem = etree.SubElement(oTsh, "dateValidWef")
            oItem.text = self.sDateValidWef.replace("/","-")
        if not self.sDateValidTil in [None, ""]:
            oItem = etree.SubElement(oTsh, "dateValidTil")
            oItem.text = self.sDateValidTil.replace("/","-")
        if not self.sCodeDay in [None, ""]:
            oItem = etree.SubElement(oTsh, "codeDay")
            oItem.text = self.sCodeDay
        if not self.sCodeDayTil in [None, ""]:
            oItem = etree.SubElement(oTsh, "codeDayTil")
            oItem.text = self.sCodeDayTil
        if not self.sTimeWef in [None, ""]:
            oItem = etree.SubElement(oTsh, "timeWef")
            oItem.text = self.sTimeWef
        if not self.sTimeTil in [None, ""]:
            oItem = etree.SubElement(oTsh, "timeTil")
            oItem.text = self.sTimeTil
        if not self.sCodeEventWef in [None, ""]:
            oItem = etree.SubElement(oTsh, "codeEventWef")
            oItem.text = self.sCodeEventWef
        if not self.sTimeRelEventWef in [None, ""]:
            oItem = etree.SubElement(oTsh, "timeRelEventWef")
            oItem.text = self.sTimeRelEventWef
        if not self.sCodeCombWef in [None, ""]:
            oItem = etree.SubElement(oTsh, "codeCombWef")
            oItem.text = self.sCodeCombWef
        if not self.sCodeEventTil in [None, ""]:
            oItem = etree.SubElement(oTsh, "codeEventTil")
            oItem.text = self.sCodeEventTil
        if not self.sTimeRelEventTil in [None, ""]:
            oItem = etree.SubElement(oTsh, "timeRelEventTil")
            oItem.text = self.sTimeRelEventTil
        if not self.sCodeCombTil in [None, ""]:
            oItem = etree.SubElement(oTsh, "codeCombTil")
            oItem.text = self.sCodeCombTil
        return oTsh

###############   Airspace area  ###########
class AixmAse4_5:

    def __init__(self) -> None:
        self.bBorderInProcess:bool = False

        #---Airspace Header---
        self.sClass:str = None
        self.sType:str = None
        self.sName:str = None
        self.sUpper:str = None
        self.sLower:str = None

        #---Ase objet--- Complementary items for Aixm 4.5 format
        self.sLocalType:str = None
        self.sCodeActivity:str = None
        self.sDesc:str = None
        self.sMhz:str = None
        self.sCodeWorkHr:str = None
        self.sRmkWorkHr:str = None
        self.oTimesh:list = list()
        self.AseUid_mid:str = None
        self.sId = " "                    #Défaut = Espace pour alimenter cet élément Aixm
        self.sUId = None
        self.sGUId = None
        self.codeDistVerUpper:str = None
        self.valDistVerUpper:int = None
        self.uomDistVerUpper:str = None
        self.codeDistVerLower:str = None
        self.valDistVerLower:int = None
        self.uomDistVerLower:str = None

        #---Abd--- Airspace Borders
        self.oBorder:list = list()
        return

    #Samples of source line:
    #   '*ATimes {"1": ["UTC(01/01->31/12)", "ANY(00:00->23:59)"]}'
    #   '*ATimes {"1": ["UTC(01/01->01/10)", "ANY(00:00->23:59)"], "2": ["UTC(01/12->31/12)", "ANY(00:00->23:59)"]}'
    #   '*ATimes {"1": ["UTC(01/01->31/12)", "MON to FRI(08:30->16:00)"]}'
    #   '*ATimes {"1": ["UTC(EDLST->SDLST)", "MON to FRI(07:00->21:00)"], "2": ["UTC(SDLST->EDLST)", "MON to FRI(06:00->22:00)"]}'
    #   '*ATimes {"1": ["UTC(01/01->31/12)", "ANY(SR/30/E->SS/30/L)"]}'
    def addTimeSheduler(self, oATimes:dict) -> None:
        self.oTimesh = []     #Reset (if necesary...)
        for sKey, aTime in oATimes.items():
            oTimeSch = AixmTimsh4_5()       #New instence of...
            self.oTimesh.append(oTimeSch)   #Add to list

            #Content of aTime[0] --> "UTC(01/01->31/12)" or "UTC(EDLST->SDLST)"
            oTimeSch.sCodeTimeRef:str = bpaTools.getLeftOf(aTime[0], "(")
            sDates:str = bpaTools.getContentOf(aTime[0], "(", ")")
            oTimeSch.sDateValidWef, oTimeSch.sDateValidTil = sDates.split("->")

            #Content of aTime[1] --> "WD(08:00->18:00)" or "SAT to SUN(08:30->16:00)" or "ANY(SR/30/E->SS/30/L)"
            sCodeDays:str = bpaTools.getLeftOf(aTime[1], "(")
            if sCodeDays.find(" to ")>0:    #case "SAT to SUN(08:30->16:00)"
                oTimeSch.sCodeDay, oTimeSch.sCodeDayTil = sCodeDays.split(" to ")
            else:                           #case "WD(08:00->18:00)" or "ANY(SR/30/E->SS/30/L)"
                oTimeSch.sCodeDay = sCodeDays
                oTimeSch.sCodeDayTil = sCodeDays
            sDates:str = bpaTools.getContentOf(aTime[1], "(", ")")
            sDateDeb, sDateFin = sDates.split("->")
            if sDateDeb.find("/")>0:    #case "(SR/30/E->SS/30/L)"
                oTimeSch.sCodeEventWef, oTimeSch.sTimeRelEventWef, oTimeSch.sCodeCombWef = sDateDeb.split("/")
            else:                       #case "(08:00->18:00)"
                oTimeSch.sTimeWef = sDateDeb
            if sDateFin.find("/")>0:    #case "(SR/30/E->SS/30/L)"
                oTimeSch.sCodeEventTil, oTimeSch.sTimeRelEventTil, oTimeSch.sCodeCombTil = sDateFin.split("/")
            else:                       #case "(08:00->18:00)"
                oTimeSch.sTimeTil = sDateFin
        return

    def isCorrectHeader(self) -> bool:
        #ret = self.sClass!=None or (self.sClass==None and self.sType in ["R","P","W","TMZ","RMZ","TMZ/RMZ","ZSM"])
        ret = self.sClass  != None and \
              self.sType   != None and \
              self.sName   != None and \
              self.sUpper  != None and \
              self.sLower  != None
        return ret

    def getID(self) -> str:
        return self.AseUid_mid

    def getLongName(self) -> str:
        if self.sType:
            ret = "[{0}]({1}) {2}".format(self.sClass, self.sType, self.sName)
        else:
            ret = "[{0}] {1}".format(self.sClass, self.sName)
        return ret

    def getAlt(self) -> str:
        ret = "[{0}/{1}]".format(self.sLower, self.sUpper)
        return ret

    def getDesc(self) -> str:
        ret = "{0} {1}".format(self.getLongName(), self.getAlt())
        return ret

    def getAllProperties(self) -> str:
        ret = "id={0} - {1}\ncodeUpper={2} valUpper={3} uomUpper={4}\ncodeLower={5} valLower={6} uomLower={7}".format(self.getID(), self.getDesc(), \
                self.codeDistVerUpper, \
                self.valDistVerUpper,  \
                self.uomDistVerUpper,  \
                self.codeDistVerLower, \
                self.valDistVerLower,  \
                self.uomDistVerLower)
        return ret

    def makePoint(self, aLine:list) -> AixmAvx4_5:
        #aLine = DP 47:13:25 N 002:37:25 E
        try:
            oPoint = AixmAvx4_5()
            if oPoint.loadPoint(aLine):
                self.oBorder.append(oPoint)
            return oPoint
        except:
            raise

    def makeArc(self, aCenter:list, sPoint2Point:str, circleClockWise:str) -> AixmAvx4_5:
        #aCenter = DP 47:36:04 N 000:25:56 W
        #sPoint2Point = DB 44:54:52 N 005:02:35 E, 44:55:20 N 004:54:10 E
        oArc = AixmAvx4_5()
        if oArc.loadArc(aCenter, sPoint2Point, circleClockWise):
            self.oBorder.append(oArc)

            #Recup et construction du point de sortie de l'arc
            aCoords = sPoint2Point.split(",")
            aLastPoint = str("DP " + aCoords[1]).split(" ")
            self.makePoint(aLastPoint)
        return oArc

    def makeCircle(self, aCenter:list, fRadius:float) -> AixmCircle4_5:
        oCircle = AixmCircle4_5()
        if oCircle.loadCircle(aCenter, fRadius):
            self.oBorder.append(oCircle)
        return oCircle


###############   Airspaces factory  ###########
class AixmAirspaces:

    def __init__(self, oLog:bpaTools.Logger=None) -> None:
        bpaTools.initEvent(__file__, oLog)
        self.oLog:bpaTools.Logger = oLog                    #Log file
        self.oAirspaces = list()
        self.schemaLocation:str = "../_aixm_xsd-4.5b/AIXM-Snapshot.xsd"     #Default dictionary
        return

    def getFactoryAirspace(self) -> AixmAse4_5:
        oAS = AixmAse4_5()    #New object
        return oAS

    def addAirspace(self, oAS:AixmAse4_5) -> AixmAse4_5:
        self.oAirspaces.append(oAS)                 #Add object in factoty list
        #if oAS.sUId==None:
        #Generate new id !
        oAS.AseUid_mid = len(self.oAirspaces)   #Create object identifier
        #else:
        #    oAS.AseUid_mid = oAS.sUId               #Reuse existing identifier
        return oAS

    def parse2Aixm4_5(self, sOutPath:str, sSrcFile:str, sDstFile:str=None) -> None:
        oAS:AixmAse4_5 = None

        #AIXM 4.5 XML Header file
        oXML = etree.Element("AIXM-Snapshot")
        attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "noNamespaceSchemaLocation")
        #oXML.set(attr_qname, "http://www.aixm.aero/schema/4.5/AIXM-Snapshot.xsd")
        oXML.set(attr_qname, self.schemaLocation)
        oXML.set("origin", "BPa")
        oXML.set("version", "4.5")
        oXML.set("created", bpaTools.getNowISO())
        oXML.set("effective", bpaTools.getNowISO())
        #print(etree.tostring(oXML, pretty_print=True))

        #Ajout des zones aériennes
        for oAS in self.oAirspaces:
            #<Ase> bloc
            oAse = etree.SubElement(oXML, "Ase")

            #<AseUid> bloc
            oAseUid = etree.SubElement(oAse, "AseUid")
            oAseUid.set("mid", str(oAS.getID()))
            oCodeType = etree.SubElement(oAseUid, "codeType")
            if oAS.sType in [None, ""]:
                oCodeType.text = " "
            else:
                oCodeType.text = oAS.sType
            oCodeId = etree.SubElement(oAseUid, "codeId")
            oCodeId.text = oAS.sId

            #Spécifique Poaff - Caractéristiques complémentaires évzntuellement a conserver
            sTmp:str = str(oAS.sGUId) + str(oAS.sUId) + str(oAS.sMhz)
            sTmp = sTmp.replace("None", "")
            if len(sTmp)>1:         #Au moins 1 caractéristique complémentaire a conserver
                oAseAdding = etree.SubElement(oAse, "PoaffAdding")
                if not oAS.sGUId in [None, ""]:
                    oItem = etree.SubElement(oAseAdding, "GUId")
                    oItem.text = oAS.sGUId
                if not oAS.sUId in [None, ""]:
                    oItem = etree.SubElement(oAseAdding, "UId")
                    oItem.text = oAS.sUId
                if not oAS.sMhz in [None, ""]:
                    oItem = etree.SubElement(oAseAdding, "Mhz")
                    oItem.text = oAS.sMhz

            #<Ase> bloc
            if not oAS.sLocalType in [None, ""]:
                oItem = etree.SubElement(oAse, "txtLocalType")
                oItem.text = oAS.sLocalType
            oItem = etree.SubElement(oAse, "txtName")
            oItem.text = bpaTools.cleanAccent(oAS.sName)
            if not oAS.sClass in [None, ""]:
                oItem = etree.SubElement(oAse, "codeClass")
                oItem.text = oAS.sClass
            if not oAS.sCodeActivity in [None, ""]:
                oItem = etree.SubElement(oAse, "codeActivity")
                oItem.text = oAS.sCodeActivity
            oItem = etree.SubElement(oAse, "codeDistVerUpper")
            oItem.text = oAS.codeDistVerUpper
            oItem = etree.SubElement(oAse, "valDistVerUpper")
            oItem.text = str(oAS.valDistVerUpper)
            oItem = etree.SubElement(oAse, "uomDistVerUpper")
            oItem.text = oAS.uomDistVerUpper
            oItem = etree.SubElement(oAse, "codeDistVerLower")
            oItem.text = oAS.codeDistVerLower
            oItem = etree.SubElement(oAse, "valDistVerLower")
            oItem.text = str(oAS.valDistVerLower)
            oItem = etree.SubElement(oAse, "uomDistVerLower")
            oItem.text = oAS.uomDistVerLower

            #<Att> bloc
            if not oAS.sCodeWorkHr in [None, ""]:
                oAtt = etree.SubElement(oAse, "Att")
                oItem = etree.SubElement(oAtt, "codeWorkHr")
                oItem.text = oAS.sCodeWorkHr

                #<Timsh> bloc
                for o in oAS.oTimesh:
                    oAtt.append(o.getXml())

                #<Att> bloc
                if not oAS.sRmkWorkHr in [None, ""]:
                    oItem = etree.SubElement(oAtt, "txtRmkWorkHr")
                    oItem.text = oAS.sRmkWorkHr

            #<Ase> bloc
            if not oAS.sDesc in [None, ""]:
                oItem = etree.SubElement(oAse, "txtRmk")
                oItem.text = oAS.sDesc


        #print(etree.tostring(oXML, pretty_print=True))
        #Ajout des bordures de zones aériennes
        for oAS in self.oAirspaces:
            oAbd = etree.SubElement(oXML, "Abd")
            oAbdUid = etree.SubElement(oAbd, "AbdUid")
            oAbdUid.set("mid", str(oAS.getID()))
            oAseUid = etree.SubElement(oAbdUid, "AseUid")
            oAseUid.set("mid", str(oAS.getID()))
            oCodeType = etree.SubElement(oAseUid, "codeType")
            if oAS.sType in [None, ""]:
                oCodeType.text = " "
            else:
                oCodeType.text = oAS.sType
            oCodeId = etree.SubElement(oAseUid, "codeId")
            oCodeId.text = oAS.sId

            for oBD in oAS.oBorder:
                if isinstance(oBD, AixmAvx4_5):
                    oAvx = etree.SubElement(oAbd, "Avx")
                    oCodeType = etree.SubElement(oAvx, "codeType")
                    if oAS.sType in [None, ""]:
                        oCodeType.text = " "
                    else:
                        oCodeType.text = oBD.codeType
                    oGeoLat = etree.SubElement(oAvx, "geoLat")
                    oGeoLat.text = oBD.geoLat
                    oGeoLong = etree.SubElement(oAvx, "geoLong")
                    oGeoLong.text = oBD.geoLong
                    oCodeDatum = etree.SubElement(oAvx, "codeDatum")
                    oCodeDatum.text = oBD.codeDatum
                    if not oBD.geoLatArc is None:
                        oGeoLatArc = etree.SubElement(oAvx, "geoLatArc")
                        oGeoLatArc.text = oBD.geoLatArc
                        oGeoLongArc = etree.SubElement(oAvx, "geoLongArc")
                        oGeoLongArc.text = oBD.geoLongArc
                        oValRadiusArc = etree.SubElement(oAvx, "valRadiusArc")
                        oValRadiusArc.text = str(oBD.valRadiusArc)
                        oUomRadiusArc = etree.SubElement(oAvx, "uomRadiusArc")
                        oUomRadiusArc.text = oBD.uomRadiusArc
                elif isinstance(oBD, AixmCircle4_5):
                    oCircle = etree.SubElement(oAbd, "Circle")
                    oGeoLatCen = etree.SubElement(oCircle, "geoLatCen")
                    oGeoLatCen.text = oBD.geoLatCen
                    oGeoLongCen = etree.SubElement(oCircle, "geoLongCen")
                    oGeoLongCen.text = oBD.geoLongCen
                    oCodeDatum = etree.SubElement(oCircle, "codeDatum")
                    oCodeDatum.text = oBD.codeDatum
                    oValRadius = etree.SubElement(oCircle, "valRadius")
                    oValRadius.text = str(oBD.valRadius)
                    oUomRadius = etree.SubElement(oCircle, "uomRadius")
                    oUomRadius.text = oBD.uomRadius

        #print(etree.tostring(oXML, pretty_print=True))
        oTree = etree.ElementTree(oXML)

        #Creation du fichier xml
        if sDstFile==None:
            sDstFile = bpaTools.getFileName(sSrcFile) + "_aixm45.xml"
        oTree.write(sOutPath + sDstFile, pretty_print=True, xml_declaration=True, encoding="utf-8")
        return


if __name__ == '__main__':
    ### Tests
    aTestLines = ["V X=48:36:03 N 003:49:00 W",
                  "DP 50:25:12N 001:37:52E",
                  "DP 50:25:12 N 001:37:52E",
                  "DP 50:25:12N 001:37:52 E",
                  "DP 50:25:12N 001:37:52E",
                  "DP 50:25:12.123 N 001:37:52.625 E",
                  "V X=48:36:03 N 003:49:00 W",
                  "DB 50:25:12N 001:37:52E, 50:26:16N 001:33:37E",
                  "DB 50:25:12 N 001:37:52E, 50:26:16 N 001:33:37E",
                  "DB 50:25:12N 001:37:52 E, 50:26:16N 001:33:37 E",
                  "DB 50:25:12 N 001:37:52 E, 50:26:16 N 001:33:37 E"]

    for sLine in aTestLines:
        aLine = sLine.split(" ")
        print(getCoordonnees(aLine))
        print(getCoordonnees(sLine))
        if "," in sLine:
            print(getCoordonnees(sLine, bSecondPoint=True))
        print("---")