#include <telecommande.h>

bool Telecommande::initialize(int clk,int cmd,int att,int dat) 
{
    // setting télécommande
        // setup pins and settings:  GamePad(clock, command, attention, data, Pressures?, Rumble?) check for error
    error = ps2x.config_gamepad(clk, cmd, att, dat, true, true);
    Serial.print(clk);
    Serial.print(cmd);
    Serial.print(att);
    Serial.print(dat);


    if(error == 0)
    {
        Serial.println("Found Controller, configured successful");
        Serial.println("Try out all the buttons, X will vibrate the controller, faster as you press harder;");
        Serial.println("holding L1 or R1 will print out the analog stick values.");
        Serial.println("Go to www.billporter.info for updates and to report bugs.");
    }
    else if(error == 1)
        Serial.println("No controller found, check wiring, see readme.txt to enable debug. visit www.billporter.info for troubleshooting tips");
    else if(error == 2)
        Serial.println("Controller found but not accepting commands. see readme.txt to enable debug. Visit www.billporter.info for troubleshooting tips");
    else if(error == 3)
        Serial.println("Controller refusing to enter Pressures mode, may not support it. ");
    
    // Serial.print(ps2x.Analog(1), HEX);
    type = ps2x.readType();
    switch(type)
    {
        case 0:
        Serial.println("Unknown Controller type");
        break;
        case 1:
        Serial.println("DualShock Controller Found");
        break;
        case 2:
        Serial.println("GuitarHero Controller Found");
        break;
    }

    if (error == 0 && type == 1)
        return 1;
    else
        return 0;
}

struct TelecommandeData Telecommande::get_telecommandeData()
{
    ps2x.read_gamepad(false, vibrate);
    struct TelecommandeData telecommandeData;
    telecommandeData.X = 0;
    telecommandeData.Y = 0;
    telecommandeData.carre = 0;
    telecommandeData.triangle = 0;
    telecommandeData.rond = 0;
    telecommandeData.croix = 0;
    telecommandeData.n1 = 0;
    telecommandeData.n2 = 0;

    if(ps2x.Button(PSB_PAD_UP))
    {
        telecommandeData.X += 1;
    }
    if(ps2x.Button(PSB_PAD_RIGHT))
    {
        telecommandeData.Y += 1;
    }
    if(ps2x.Button(PSB_PAD_LEFT))
    {
        telecommandeData.Y -= 1;
    }
    if(ps2x.Button(PSB_PAD_DOWN))
    {
        telecommandeData.X -= 1;
    }


    if(ps2x.Button(PSB_L1) || ps2x.Button(PSB_R1))
    {
        // récupération des données du stick au lieu du pad
        telecommandeData.X = -ps2x.Analog(PSS_LY)/255.*2.+1;
        telecommandeData.Y = ps2x.Analog(PSS_LX)/255.*2.-1; 
        Serial.print(telecommandeData.X ,DEC);
        Serial.print(telecommandeData.Y ,DEC);

    }




    if(ps2x.Button(PSB_PINK))
    {
        telecommandeData.carre = 1;
    }
    if(ps2x.Button(PSB_GREEN))
    {
        telecommandeData.triangle = 1;
    }
    if(ps2x.Button(PSB_RED))
    {
        telecommandeData.rond = 1;
    }
    if(ps2x.Button(PSB_BLUE))
    {
        telecommandeData.croix = 1;
    }
    if(ps2x.Button(PSB_L1) || ps2x.Button(PSB_R1))
    {
        telecommandeData.n1 = 1;
    }
    if(ps2x.Button(PSB_L2) || ps2x.Button(PSB_R2))
    {
        telecommandeData.n2 = 1;
    }

    //Serial.print(telecommandeData.carre);
    //Serial.print(telecommandeData.triangle);
    // Serial.print(telecommandeData.rond );
    // Serial.print(telecommandeData.croix);
    // Serial.print(telecommandeData.n1 );
    // Serial.println(telecommandeData.n2);

    return telecommandeData;

};
