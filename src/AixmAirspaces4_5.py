#!/usr/bin/env python3

import bpaTools
import math
from pyproj import Proj, transform


pWGS = Proj("epsg:4326")            # EPSG:4326 = WGS84 / Geodetic coordinate system for World  :: Deprecated format --> Proj(init="epsg:4326")
nm = 1852                           # Nautic Mile to meters


def getCoordonnees(aLine:list) -> (str,str):
    sLat:str = None
    sLon:str = None
    aLat = ["N","S"]
    aLon = ["E","W","O"]
    try:
        if aLine[0] == "V" and aLine[1][:2] == "X=":
            #Openair format - V X=48:36:03 N 003:49:00 W
            aLine[1] = aLine[1][2:]     #Cleaning start coords
            
        if aLine[0] in ["DP", "DB", "V"]:
            #Openair format - DP 47:36:04 N 000:25:56 W
            #Openair format - DP 47:36:04 N 000:25:56W
            #Openair format - DP 47:36:04N 000:25:56 W
            #Openair format - DP 47:36:04N 000:25:56W
            #Openair format - DB 44:54:52N 005:02:35 E 44:55:20N 004:54:10 E
            #Openair format - DB 44:54:52N 005:02:35 E 44:55:20N 004:54:10E
            #Openair format - DB 44:54:52N 005:02:35E 44:55:20N 004:54:10 E
            #Openair format - DB 44:54:52N 005:02:35E 44:55:20N 004:54:10E
            #Openair format - V 48:36:03 N 003:49:00 W
            #Openair format - V 48:36:03 N 003:49:00W
            #Openair format - V 48:36:03N 003:49:00 W
            #Openair format - V 48:36:03N 003:49:00W
            
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

            if sLat==None or sLon==None:
                raise Exception("?")
                
            #Calcul en D.d pour reformattage systématique en DMS.d
            lat, lon = bpaTools.geoStr2dd(sLat, sLon)
            sLat, sLon = bpaTools.geoDd2dms(lat,"lat" ,lon,"lon", digit=4)
            
        return sLat, sLon
    
    except Exception as e:
        sHeader = "[" + bpaTools.getFileName(__file__) + "." + getCoordonnees.__name__ + "()] "
        sMsg = "/!\ Parsing Line Error - {}".format(aLine)
        raise Exception(sHeader + sMsg + " / " + str(e))


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
            return True
        except:
            raise
        


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
            return True
        except:
            raise

        
    def loadArc(self, aCenter:list, aPoint2Point:list, circleClockWise:str) -> bool:
        #aCenter = DP 47:36:04 N 000:25:56 W
        #aPoint2Point = 'DB 44:54:52 N 005:02:35 E 44:55:20 N 004:54:10 E'
        try:
            self.openairType = "Arc"
            if circleClockWise == "-":
                self.codeType = "CCA"       #Clockwise Arc
            else:
                self.codeType = "CWA"       #Counter Clockwise Arc
            
            #Point d'entrée de l'arc
            lat, lon = getCoordonnees(aPoint2Point)
            self.geoLat = lat
            self.geoLong = lon
            #Le centre de l'arc
            lat, lon = getCoordonnees(aCenter)
            self.geoLatArc = lat
            self.geoLongArc = lon
            
            # Détermination du rayon de l'arc
            latC, lonC = bpaTools.geoStr2dd(self.geoLatArc, self.geoLongArc)
            latS, lonS = bpaTools.geoStr2dd(self.geoLat, self.geoLong)
            srs = Proj(proj="ortho", lat_0=latC, lon_0=lonC)
            start_x, start_y = transform(p1=pWGS, p2=srs, x=latS, y=lonS)
            radius = math.sqrt(start_x**2+start_y**2)   # Meter
            self.valRadiusArc = round(radius/nm,2)      # Nautic Mile
            return True
        except:
            raise        
         
        
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
        try:
            oPoint = AixmAvx4_5()
            if oPoint.loadPoint(aLine):
                self.oBorder.append(oPoint)
            return oPoint
        except:
            raise

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
        oXML.set(attr_qname, "../_aixm_xsd-4.5b/AIXM-Snapshot.xsd")
        oXML.set("origin", "BPa")
        oXML.set("version", "4.5")
        oXML.set("created", bpaTools.getNowISO())
        oXML.set("effective", bpaTools.getNowISO())
        #print(etree.tostring(oXML, pretty_print=True))
        
        #Ajout des zones aériennes
        for oAS in self.oAirspaces:
            oAse = etree.SubElement(oXML, "Ase")
            oAseUid = etree.SubElement(oAse, "AseUid")
            oAseUid.set("mid", str(oAS.getID()))
            oCodeType = etree.SubElement(oAseUid, "codeType")
            if oAS.sType in [None, ""]:
                oCodeType.text = " "
            else:
                oCodeType.text = oAS.sType
            oCodeId = etree.SubElement(oAseUid, "codeId")
            oCodeId.text = oAS.codeId
            oItem = etree.SubElement(oAse, "txtName")
            oItem.text = str(oAS.sName)
            if not oAS.sClass in [None, ""]:
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
            oCodeId.text = oAS.codeId
            
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
        #Creation du fichier xml
        oTree = etree.ElementTree(oXML)
        oTree.write(sDstFile, pretty_print=True, xml_declaration=True, encoding="utf-8")
        
        return
    
