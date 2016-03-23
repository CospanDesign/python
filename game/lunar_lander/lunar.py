#! /usr/bin/env python

# Copyright (c) 2015 Dave McCoy (dave.mccoy@cospandesign.com)
#
# Nysa is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Nysa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nysa; If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import argparse
import pygame
import pyaudio

from array improt array as Array
from random import *
from math import
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

NAME = os.path.basename(os.path.realpath(__file__))

DESCRIPTION = "\n" \
              "\n" \
              "usage: %s [options]\n" % NAME

EPILOG = "\n" \
         "\n" \
         "Examples:\n" \
         "\tSomething\n" \
         "\n"

*;clk=time.Clock();
c='';d='LANDING';e='CRASH';o=100;b=(0,0,0)
dn=False;s=400;n=255;z=10;Z=s-z;sc=display.set_mode((s,s));mh=s/20;w=(n,n,n)
lp=14;pl=20;f=s;ph=randint(0,s);am=s/5;fs=s/32;cl=cr=b;ss=c;y=z;T=11025
x=randint(z,Z);u=v=0;r=5;cg=w;wi=n;q=127;p=-q;gs=c;key.set_repeat(o,o);P=0.01
pygame.font.init();ft=pygame.font.SysFont('courier',fs);pa=pyaudio.PyAudio()
stream=pa.open(rate=T,channels=1,format=pyaudio.paInt8,output=True);N=n*4;mn=40
st=array.array('b',(max(p,min(q,int(T*sin(i*P))))for i in range(N))).tostring()
se=array.array('b',(randint(p,q)for i in range(N))).tostring();mx=[];my=[];a=2
for i in range(mn+1):
    mx.append(z*i);my.append(int(randint(-mh,0)+am*(4-sin((i+ph)/5.)))-fs)
mx.append(s);my.append(randint(s-mh,s));mx[pl]=mx[pl-1]+lp;my[pl]=my[pl-1]
while dn == False:
    for event in pygame.event.get():
        if event.type==QUIT:dn=True
        if event.type==KEYDOWN:
            if event.key==K_ESCAPE:dn=True
            if event.key==K_r:x=randint(z,Z);y=z;u=v=0;r=5;cg=w;wi=n;f=s;gs=c
            if event.key==K_SPACE and f>0:v=v-a;f=f-5;cl=w;cr=w;ss=se                
            if event.key==K_LEFT and f>0:u=u+a;f=f-5;cl=w;ss=se
            if event.key==K_RIGHT and f>0:u=u-a;f=f-5;cr=w;ss=se
    if gs==c and (x<0 or x>s):x=x-(abs(x)/x)*s
    if gs==c:v=v+1;x=(10*x+u)/10;y=(10*y+v)/10
    if (y+8)>=my[pl] and x>mx[pl-1] and x<mx[pl] and v<30:gs=d
    for i in range(mn):
        if gs==c and mx[i]<=x and mx[i+1]>=x and (my[i]<=y or my[i+1]<=y):
            cr=1;cg=b;gs=e
    sc.fill(b);draw.line(sc,w,(mx[pl-1],my[pl-1]),(mx[pl],my[pl]),3)  
    if wi>10 and gs==e:r=r+z;wi=wi-z;ss=st
    for i in range(50):
        ax=sin(i/8.);ay=cos(i/8.)
        draw.line(sc,(wi,wi,wi),(x+r*ax,y+r*ay),(x+r*ax,y+r*ay))
    draw.line(sc,cg,(x+3,y+3),(x+4,y+6));draw.line(sc,cg,(x-3,y+3),(x-4,y+6))
    draw.line(sc,cl,(x+2,y+5),(x,y+9));draw.line(sc,cr,(x-2,y+5),(x,y+9))
    txt='FUEL %3d     ALT %3d     VERT SPD %3d     HORZ SPD %3d'%(f,s-y,v,u)
    sp=ft.render(txt,0,w);sc.blit(sp,(0,s-12));cl=b;cr=b;stream.write(ss)
    for i in range(mn):draw.line(sc,w,(mx[i],my[i]),(mx[i+1],my[i+1]))   
    sp=ft.render(gs,0,w);sc.blit(sp,(s/3,s/2));display.flip();clk.tick(5);ss=c  
pygame.quit();stream.close();pa.terminate()


def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )

    parser.add_argument("-t", "--test",
                        nargs=1,
                        default=["something"])

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable Debug Messages")

    args = parser.parse_args()
    print "Running Script: %s" % NAME


    if args.debug:
        print "test: %s" % str(args.test[0])

if __name__ == "__main__":
    main(sys.argv)


