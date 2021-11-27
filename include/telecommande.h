#include <PS2X_lib.h> 

struct TelecommandeData {
    double X;
    double Y;
    int carre;
    int rond;
    int triangle;
    int croix;
    int n1;
    int n2;
};



class Telecommande {
    public:
        boolean initialize ( int clk,int cmd,int att,int dat);
        struct TelecommandeData get_telecommandeData ();



    private:
        PS2X ps2x;
        int error = 0; 
        byte type = 0;
        byte vibrate = 0;
};