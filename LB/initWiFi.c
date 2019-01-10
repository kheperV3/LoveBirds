//init  du point d'acces wifi par écriture du fichier /etc/wpa_supplicant/wpa_supplicant.conf
// à partir de 2 fichiers :
//             /boot/ssid.txt  ===> ssid
//             /boot/psk.txt   ===> password
//
// les  2 fichiers sont supprimés avant un reboot
//
///////////////////////////////////////////////////




#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

int main()
{
char b[1000];
int p;
int n;


p = open("/boot/WIFI.txt", O_RDONLY);
if(p == -1) exit(0);
n = read(p,b,1000);
close(p);
remove("/etc/wpa_supplicant/wpa_supplicant.conf");
p = open("/etc/wpa_supplicant/wpa_supplicant.conf", O_WRONLY+O_CREAT, 0644);
n=write(p, b, n);
close(p);

//restart service with new config
system("sudo systemctl daemon-reload");
system("sudo systemctl restart dhcpcd");

//remove("/boot/WIFI.txt");

//system("shutdown -r now"); 
}
