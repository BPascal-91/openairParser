# openairParser

**EN COURS DE DEVELOPPEMENT !!!**  
--> Les Pull-Request et Issues sont les bienvenues :)  


Programme d'extraction et de formatage des données issues du format OpenAir ()  
Un unique fichier au format standard AIXM v4.5 (Aeronautical Information Exchange Modele) est générée en sortie de traitement.  

(*) AIXM - Aeronautical Information Exchange Modele : Un standard internationanl d'échange de données aéronautiques. Basé sur la technologie XML, ce formay est décrit ici - http://www.aixm.aero/   
Nota. Actuellement, seul l'ancien format AIXM 4.5 est pris en charge. Ultérieurement, ce programme évoluera probablement pour générer la version AIXM 5.1  


## Installation
```
pip install -r requirements.txt
```

## Utilisation
Le programme produit un log et un fichier dans le dossier ./out/  
```
openairParser v1.1.0  
-----------------  
Aeronautical Information Exchange Model (AIXM) Converter  
Call: openairParser <[drive:][path]filename>
With:  
  <[drive:][path]filename>       AIXM source file  

  <Option(s)> - Complementary Options:  
    -h              Help syntax  
    -CleanLog       Clean log file before exec  

  Samples: openairParser ../tst/aixm4.5_SIA-FR_2019-12-05.xml -CleanLog  

  Resources  
     OpenAir files: http://soaringweb.org/Airspace/  --or--  http://xcglobe.com/cloudapi/browser  -or-  http://cunimb.net/openair2map.php  
     AIXM output format: http://www.aixm.aero/
```
