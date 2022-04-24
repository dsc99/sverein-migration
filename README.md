# sverein-migration
Skripte zur Migration der DSC99 Mitgliederverwaltung nach S-Verein

## Setup

* Works in MacOS and Linux (Ubuntu)
* Create a Python3 virtualenv in the GIT directory, using env subdirectory


## Usage and Directory structure

* Run scripts in bin/
    * list_tables.py to test whether everything works --> lists all table definitions
    * generate-sverein.py to generate the SVerein import files
* Files are created in the var/ directory (excluded from GIT)
* Source DB is expected "parallel" to the GIT worksapce
    * Available in the DSC99 Cloud
    * Sync locally using the nexcloud client


## Online resources

* DSC99 S-Verein: https://verwaltung.s-verein.de/login/d17
* DSC99 Cloud: https://cloud.dsc-99.org/
    * Verwaltungs-Ordner: https://cloud.dsc-99.org/f/1408

