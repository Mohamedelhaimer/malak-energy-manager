# Serveur Gestion Energie

## Description
Le serveur permet de gérer les informations liées à la consommation d'énergie électrique. Il est le nœud entre le consommateur et les outils de mesure et de maitrise de l'énergie électrique d'un foyer. 

## Fonctions
* Afficher les informations générées par le compteur communicant
* Interpréter les informations du compteur communicant pour être utile au consommateur et ainsi mieux gérer sa consommation 
* Avoir une vision détaillée de la consommation du foyer
* Controller les objets connectés pour maitriser la consommation
* Programmer le déclenchement des prises en fonction de plages horaires
* Paramétrer les priorités des objets alimentés pour un délestage intelligent 
* Stocker les données pour de faire du traitement de données

## Composants
* Raspberry Pi 3 
* nRF24

## Echanges d'informations
Le serveur tel qu'il est conçu possède deux type de connexion : Radio Fréquence et wifi.
La connexion radio fréquence sert à récupérer les informations générés par le compteur communicant (Linky) grâce à l'ajout d'un "décodeur" et d'un transmetteur RF (TIC).
La wifi permet de créer un réseau local afin que les objets connectés échange avec le serveur. 

### Informations récupérées
* Trame du compteur via la TIC en RF.
* Informations d'état des différents objets connectés via une API REST.
* Informations de mesure du courant des objets connectés

### Informations envoyées
* Information de pilotage des objets connectés. 

## Setup Instructions

1. Create a virtual environment and activate it:
```bash
python -m venv env
# On Windows
.\env\Scripts\activate
# On Linux/Mac
source env/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
- Install MySQL if not already installed
- Create a database named 'IoEDb'
- Create necessary tables (see Database Setup section)

4. Configure environment variables:
- Copy `.env.template` to `.env`
- Update the values in `.env` with your configuration

5. Run the application:
```bash
python application.py
```

The server will start on http://localhost:5000

## Database Setup

Create the following tables in your MySQL database:

```sql
CREATE TABLE connected_obj (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(255),
    device_type VARCHAR(255),
    nb_soc INT
);

CREATE TABLE raw_histo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    IINST INT,
    IMAX INT,
    ISOUSC INT,
    PTEC VARCHAR(255)
);
```

## To do
* Implémenter la collecte d'information via RF (librairie nRF24)
* Systématiser la collecte d'information des objets connectés (fonctionne partiellement pour l'[écran déporté](https://github.com/LF2L/RemoteLinkyInfo))
* Créer la fonction de délestage
