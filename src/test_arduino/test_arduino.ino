
#include <Arduino.h>
#include <telecommande.h>
#include <RunningAverage.h>

int pinMotorLeftSpeed = 5;
int pinMotorLeftSens = 4;
int sensBranchementLeft = 1;
int pinMotorRightSpeed = 6;
int pinMotorRightSens = 7;
int sensBranchementRight = -1;

int pinMotorLameSpeed = 3;
int pinMotorLameSens = 2;

int maxSonarPin = 0;


int maxMotorSpeed = 150; //255
int maxRotationSpeed = int(maxMotorSpeed / 1.5); // 30%
int  maxEvolution = 10;


int maxMotorSpeedLame = 255; //255


Telecommande telecommande;
bool error;

double vitesse = 0;
double vitesseRotation = 0;
int vitesseMoteurGaucheAvant;
int vitesseMoteurDroitAvant;
int speedLameAvant;


long sensor, mm, inches;
int Ilame;
int Iroues;
int Vbat;
RunningAverage MoyGlissImoteur(40);
RunningAverage MoyGlissTension(40);


int previousTriangle = 0;
int previousRond = 0;

unsigned long startManoeuvreTime ;
unsigned long dureeManoeuvre ;
enum manoeuvres
{
  pause,
  ligneDroite,
  marcheArriere,
  rotation,
};
enum manoeuvres manoeuvre;

int sensRotation ;

void setup()
{

  pinMode(pinMotorLeftSpeed, OUTPUT);
  pinMode(pinMotorLeftSens, OUTPUT);
  pinMode(pinMotorRightSpeed, OUTPUT);
  pinMode(pinMotorRightSens, OUTPUT);
  analogWrite(pinMotorLeftSpeed, 0);
  analogWrite(pinMotorRightSpeed, 0);

  error = telecommande.initialize(13, 11, 10, 12);


  pinMode(maxSonarPin, INPUT); //capteur ultrason

  Serial.begin(9600);


}

void read_distance () {
  //sensor = pulseIn(maxSonarPin, HIGH);
  //mm = sensor;

  sensor = analogRead(maxSonarPin);
  mm = sensor * 5;

}

void envoieConsigneAuMoteur(int pinVitesse, int pinSens, int vitesse)
{
  if (vitesse >= 0)
  {
    analogWrite(pinVitesse, vitesse);
    digitalWrite(pinSens, 0);
  }
  else
  {
    analogWrite(pinVitesse, -vitesse);
    digitalWrite(pinSens, 1);
  }
}


void loop() {
  struct TelecommandeData telecommandeData;
  int vitesseMoteurGauche = 0;
  int vitesseMoteurDroit = 0;
  int speedLame = 0;

  if (error != 0)
  {
    Serial.println("error ");
    return ;
  }
  telecommandeData = telecommande.get_telecommandeData()  ;

  read_distance();
  //Serial.print(" mm = ");
  //Serial.print(mm);



  if (telecommandeData.n2 == 1)
  {
    Serial.print("automatique ");
    Serial.print(manoeuvre);


    if ((telecommandeData.rond == 1) && previousRond == 0 )
    {
      //on lance une ligne droite
      Serial.println("debut ligne droite");
      startManoeuvreTime = millis();
      manoeuvre =  ligneDroite;
      vitesse = 1;
      vitesseRotation = 0;
      dureeManoeuvre = 20 * 1000;
    }
    if ((telecommandeData.triangle == 1) && (previousTriangle == 0))
    {
      //obstacle détecte
      Serial.println("debut marche arrière");
      startManoeuvreTime = millis();
      manoeuvre =  marcheArriere;
      vitesse = -1;
      vitesseRotation = 0;
      dureeManoeuvre = 3 * 1000;
    }

    //detection fin de manoeuvre
    if ((dureeManoeuvre > 0) && (millis() - startManoeuvreTime >= dureeManoeuvre))
    {
      if (manoeuvre == marcheArriere)
      {
        Serial.println("début Rotation");
        manoeuvre = rotation;
        startManoeuvreTime = millis();
        dureeManoeuvre = random(2, 5) * 1000;
        sensRotation = int(random(0, 1));
        vitesse = 0;
        vitesseRotation = (sensRotation * 2 - 1) * 1 ; // donc -0.5 ou 0.5
        Serial.println(vitesseRotation);
        Serial.println(dureeManoeuvre);

      }
      else if (manoeuvre == rotation)
      {
        Serial.println("debut ligne droite");
        manoeuvre = ligneDroite;
        startManoeuvreTime = millis();
        dureeManoeuvre = 20 * 1000;
        vitesse = 1;
        vitesseRotation = 0;

      }
      else
      {
        Serial.println("debut pause");
        manoeuvre = pause;
        startManoeuvreTime = millis();
        dureeManoeuvre = 0; // infinie
        vitesse = 0;
        vitesseRotation = 0;


      }
    }

    previousTriangle = telecommandeData.triangle;
    previousRond = telecommandeData.rond;
  }
  else
  {
    Serial.print("manuel");

    vitesse = telecommandeData.X;
    vitesseRotation = -telecommandeData.Y;
  }


  // calcul des vitesse moteurs liées à la consigne vitesse
  // compris entre -1 et 1
  vitesseMoteurGauche = vitesse * maxMotorSpeed;
  vitesseMoteurDroit = vitesse * maxMotorSpeed;

  // ajout des vitesse moteurs liées à la vitesse de rotation
  vitesseMoteurGauche += vitesseRotation * maxRotationSpeed;
  vitesseMoteurDroit -= vitesseRotation * maxRotationSpeed;


  if ((vitesseMoteurDroit - vitesseMoteurDroitAvant) > maxEvolution) {
    vitesseMoteurDroit = vitesseMoteurDroitAvant + maxEvolution;
  }
  if ((vitesseMoteurDroit - vitesseMoteurDroitAvant) < -maxEvolution) {
    vitesseMoteurDroit = vitesseMoteurDroitAvant - maxEvolution;
  }
  if ((vitesseMoteurGauche - vitesseMoteurGaucheAvant) > maxEvolution) {
    vitesseMoteurGauche = vitesseMoteurGaucheAvant + maxEvolution;
  }
  if ((vitesseMoteurGauche - vitesseMoteurGaucheAvant) < -maxEvolution) {
    vitesseMoteurGauche = vitesseMoteurGaucheAvant - maxEvolution;
  }
  if (vitesseMoteurDroit > maxMotorSpeed) {
    vitesseMoteurDroit = maxMotorSpeed;
  }
  if (vitesseMoteurDroit < -maxMotorSpeed) {
    vitesseMoteurDroit = -maxMotorSpeed;
  }
  if (vitesseMoteurGauche > maxMotorSpeed) {
    vitesseMoteurGauche = maxMotorSpeed;
  }
  if (vitesseMoteurGauche < -maxMotorSpeed) {
    vitesseMoteurGauche = -maxMotorSpeed;
  }

  //Serial.print(" # moteurs: Gauche = ");
  //Serial.print(vitesseMoteurGauche);
  //Serial.print(" Droit = ");
  //Serial.print(vitesseMoteurDroit);


  envoieConsigneAuMoteur(pinMotorLeftSpeed, pinMotorLeftSens, vitesseMoteurGauche * sensBranchementLeft) ;
  envoieConsigneAuMoteur(pinMotorRightSpeed, pinMotorRightSens, vitesseMoteurDroit * sensBranchementRight) ;

  speedLame = telecommandeData.carre * maxMotorSpeedLame;
  if ((speedLame - speedLameAvant) > 1) {
    speedLame = speedLameAvant + 3;
  }
  else if ((speedLame - speedLameAvant) < -1) {
    speedLame = speedLameAvant - 3;
  }

  envoieConsigneAuMoteur(pinMotorLameSpeed, pinMotorLameSens, speedLame) ;
  speedLameAvant = speedLame;
  //Serial.print(" speedLame");
  //Serial.print(speedLame);

  Ilame = analogRead(0);
  Iroues = analogRead(1);
  Vbat = analogRead(2);

  Serial.print(" | ");
  //  Serial.print(Ilame);
  //  Serial.print(' ');
  MoyGlissImoteur.addValue(abs(Iroues - 524));
  //  Serial.print(MoyGlissImoteur.getAverage());
  //  Serial.print(' ');
  MoyGlissTension.addValue(Vbat);
  Serial.print(MoyGlissTension.getAverage());


  Serial.println(" ");

  vitesseMoteurGaucheAvant = vitesseMoteurGauche;
  vitesseMoteurDroitAvant = vitesseMoteurDroit;
}
