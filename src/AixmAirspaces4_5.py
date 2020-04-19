#!/usr/bin/env python3

import bpaTools


def getCoordonnees(aLine:list) -> (str,str):
    sLat:str = None
    sLon:str = None
    #Openair format - DP 47:36:04 N 000:25:56 W  
    if aLine[0] == "DP" and len(aLine) == 5:
        sLat = str(aLine[1]).replace(":","") + aLine[2]
        sLon = str(aLine[3]).replace(":","") + aLine[4]
    #Openair format - V X=48:36:03 N 003:49:00 W
    elif aLine[0] == "V" and aLine[1][:2] == "X=" and len(aLine) == 5:
        sLat = str(aLine[1][2:]).replace(":","") + aLine[2]
        sLon = str(aLine[3]).replace(":","") + aLine[4]
    #Openair format - DB 44:54:52 N 005:02:35 E,44:55:20 N 004:54:10 E // ['DB', '44:54:52', 'N', '005:02:35', 'E', '44:55:20', 'N', '004:54:10', 'E']
    elif aLine[0] == "DB" and len(aLine) == 9:
        sLat = str(aLine[1]).replace(":","") + aLine[2]
        sLon = str(aLine[3]).replace(":","") + aLine[4]        
    else:
        sHeader = "[" + bpaTools.getFileName(__file__) + "." + getCoordonnees.__name__ + "()] "
        sMsg = "/!\ Parsing Line Error - {}".format(aLine)
        raise Exception(sHeader + sMsg)
    return sLat,sLon


#########   Cirlce of Airespace border  ########
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
        except:
            raise
        return True



#########   Vector of Airespace border  ########
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
        except:
            raise
        return True
        
    def loadArc(self, aCenter:list, aPoint2Point:list, circleClockWise:str) -> bool:
        #aCenter = DP 47:36:04 N 000:25:56 W
        #aPoint2Point = 'DB 44:54:52 N 005:02:35 E,44:55:20 N 004:54:10 E'
        try:
            self.openairType = "Arc"
            if circleClockWise == "-":
                self.codeType = "CCA"       #Clockwise Arc
            else:
                self.codeType = "CWA"       #Counter Clockwise Arc
            lat, lon = getCoordonnees(aCenter)
            self.geoLatArc = lat
            self.geoLongArc = lon
            self.valRadiusArc = "#"         #Non connue en Openair !
            lat, lon = getCoordonnees(aPoint2Point)
            self.geoLat = lat
            self.geoLong = lon  
        except:
            raise        
        return True    
         
        
###############   Airespace area  ###########
class AixmAse4_5:

    def __init__(self) -> None:
        self.bBorderInProcess:bool = False
        
        #---Airespace Header---
        self.sClass:str = None
        self.sType:str = None
        self.sName:str = None
        self.sUpper:str = None
        self.sLower:str = None
        
        #---Ase objet--- Complementary items for Aixm 4.5 format
        self.AseUid_mid:str = None
        self.codeId = " "                    #Défaut = Espace pour alimenter cet élément Aixm
        self.codeDistVerUpper:str = None
        self.valDistVerUpper:int = None
        self.uomDistVerUpper:str = None
        self.codeDistVerLower:str = None
        self.valDistVerLower:int = None
        self.uomDistVerLower:str = None
        
        #---Abd--- Airespace Borders
        self.oBorder:list = list()
        return

    def isCorrectHeader(self) -> bool:
        ret = self.sClass!=None or (self.sClass==None and self.sType in ["R","P","W","TMZ","RMZ","ZSM"])
        ret = ret and \
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
        try:
            oPoint = AixmAvx4_5()
            if oPoint.loadPoint(aLine):
                self.oBorder.append(oPoint)
        except:
            raise       
        return oPoint

    def makeArc(self, aCenter:list, aPoint2Point:list, circleClockWise:str) -> AixmAvx4_5:
        oArc = AixmAvx4_5()
        if oArc.loadArc(aCenter, aPoint2Point, circleClockWise):
            self.oBorder.append(oArc)
        return oArc
    
    def makeCircle(self, aCenter:list, fRadius:float) -> AixmCircle4_5:
        oCircle = AixmCircle4_5()
        if oCircle.loadCircle(aCenter, fRadius):
            self.oBorder.append(oCircle)
        return oCircle
    



###############   Airespaces factory  ###########
class AixmAirspaces:

    def __init__(self, oLog:bpaTools.Logger=None) -> None:
        bpaTools.initEvent(__file__, oLog)
        self.oLog:bpaTools.Logger = oLog                    #Log file
        self.oAirspaces = list()
        return

    def getFactoryAirspace(self) -> AixmAse4_5:
        oAS = AixmAse4_5()    #New object
        return oAS
    
    def addAirspace(self, oAS:AixmAse4_5) -> AixmAse4_5:
        self.oAirspaces.append(oAS)             #Add object in factoty list
        oAS.AseUid_mid = len(self.oAirspaces)   #Create object identifier 
        return oAS
    
    def parse2Aixm4_5(self, sOutPath:str, sSrcFile:str) -> None:
        from lxml import etree
        oAS:AixmAse4_5 = None
        
        #Destination file
        sDstFile =  sOutPath + bpaTools.getFileName(sSrcFile) + "_aixm45.xml"
        
        #AIXM 4.5 XML Header file
        oXML = etree.Element("AIXM-Snapshot")
        attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "noNamespaceSchemaLocation")
        #oXML.set(attr_qname, "http://www.aixm.aero/schema/4.5/AIXM-Snapshot.xsd")
        oXML.set(attr_qname, "./xsd-4.5b/AIXM-Snapshot.xsd")
        oXML.set("origin", "BPa")
        oXML.set("version", "4.5")
        oXML.set("created", bpaTools.getNowISO())
        oXML.set("effective", bpaTools.getNowISO())
        
        #Ajout des zones aériennes
        for oAS in self.oAirspaces:
            oAse = etree.SubElement(oXML, "Ase")
            oAseUid = etree.SubElement(oAse, "AseUid")
            oAseUid.set("mid", str(oAS.getID()))
            oCodeType = etree.SubElement(oAseUid, "codeType")
            oCodeType.text = oAS.sType
            oCodeId = etree.SubElement(oAseUid, "codeId")
            oCodeId.text = oAS.codeId
            oItem = etree.SubElement(oAse, "txtName")
            oItem.text = str(oAS.sName).upper()
            if oAS.sClass != None:
                oItem = etree.SubElement(oAse, "codeClass")
                oItem.text = oAS.sClass
            
            
            
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

        
        #print(etree.tostring(oXML, pretty_print=True))
        oTree = etree.ElementTree(oXML)
        oTree.write(sDstFile, pretty_print=True, xml_declaration=True, encoding="utf-8")
        
        return
    
