# openairParser

Programme d'extraction et de formatage des données issues du format OpenAir (Airspace and Terrain description language).
Un unique fichier au format standard AIXM v4.5 (Aeronautical Information Exchange Modele) est générée en sortie de traitement.  


(*) OpenAir - Airspace and Terrain description language : A open standard for displaying map information - http://www.winpilot.com/UsersGuide/UserAirspace.asp

(*) AIXM - Aeronautical Information Exchange Modele : Un standard internationanl d'échange de données aéronautiques. Basé sur la technologie XML - http://www.aixm.aero/   
Nota. Actuellement, seul l'ancien format AIXM 4.5 est pris en charge. Ultérieurement, ce programme évoluera probablement pour générer la version AIXM 5.1  


## Installation
```
pip install -r requirements.txt
```

## Utilisation
Le programme produit un log et un fichier dans le dossier ./out/  
```
openairParser v1.2.0  
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


## Credits
- [Pascal Bazile](https://github.com/BPascal-91/) for complete writing of openairPaser
- the many open source libraries, projects, and data sources used by this software (show file content of 'requirements.txt' for complete components detail)

