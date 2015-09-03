#!/usr/bin/python3
"""
hivex-commander - hive-file browser
Copyright (C) 2015 0rovan

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import curses
from hivex import Hivex
from sys import argv
from os.path import isfile

def listHiveDir(hive,key=None):
    stdout.write(str(key))
    key=hive.root() if key==None else key
    lst=[] if key==hive.root() else [('..'+38*' ',hive.node_parent(key),0),]
    for child in hive.node_children(key):
        lst.append(((hive.node_name(child)+40*' ')[:40],child,0))
    for child in hive.node_values(key):
        lst.append(((hive.value_key(child)+40*' ')[:40],child,1))
    return lst

def listHivePair(hive,key):
    lst=[('..'+38*' ',hive.root(),0),]
    for i in hive.value_value(key):
        lst.append(((str(i)+40*' ')[:40],i,'0'))
    return lst

class Cursor(object):
    def __init__(self,browser):
        self.browser=browser
        self.pos=0;
    def show(self):
        color=curses.color_pair(2) if self.browser.visibleLines[self.pos][2]==0 else curses.color_pair(4)
        self.browser.win.addstr(self.pos,0,self.browser.visibleLines[self.pos][0],color)
    def __hide(self):
        color=curses.color_pair(1) if self.browser.visibleLines[self.pos][2]==0 else curses.color_pair(3)
        self.browser.win.addstr(self.pos,0,self.browser.visibleLines[self.pos][0],color)
    def move(self,direction):
        self.__hide()
        if direction=='u':
            if self.pos>0:
                self.pos-=1
            elif self.browser.shift>0:
                self.browser.shift-=1
                self.browser.draw()
        elif direction=='d':
            if self.pos<self.browser.drawed-1:
                self.pos+=1
            elif self.pos+self.browser.shift<self.browser.count-1:
                self.browser.shift+=1
                self.browser.draw()   
        self.show()

class Browser(object):
    def __init__(self,win,lines):
        self.win=win
        self.lines=lines
        self.shift=0
        self.count=len(lines)
    @property
    def visibleLines(self):
        return self.lines[0+self.shift:20+self.shift] if self.count>20 else self.lines
    def draw(self):
        self.win.clear()
        i=0
        for line in self.visibleLines:
            color=curses.color_pair(1) if line[2]==0 else curses.color_pair(3)
            self.win.addstr(i,0,line[0],color)
            i+=1
        self.drawed=i

class Gui(object):
    def __init__(self,stdscr,hive):
        self.hive=hive
        curses.init_pair(1,curses.COLOR_WHITE,curses.COLOR_BLUE)
        curses.init_pair(2,curses.COLOR_BLACK,curses.COLOR_GREEN)
        curses.init_pair(3,curses.COLOR_MAGENTA,curses.COLOR_BLUE)
        curses.init_pair(4,curses.COLOR_YELLOW,curses.COLOR_GREEN)
        win=curses.newwin(20,141,1,1)
        stdscr.refresh()
        key=None
        browser=Browser(win,listHiveDir(hive))
        cursor=Cursor(browser)
        while key!='q':
            browser.draw()
            key=None
            while key not in ('\n','q'):
                cursor.show()
                key=browser.win.getkey()
                if key=='A':
                    cursor.move('u')
                if key=='B':
                    cursor.move('d')
            selected=browser.visibleLines[cursor.pos]
            del cursor
            del browser
            dirListing=listHiveDir(hive,selected[1]) if selected[2]==0 else listHivePair(hive,selected[1])
            browser=Browser(win,dirListing)
            cursor=Cursor(browser)

def main():
    if len(argv)<2 or argv[1] in('-h','--help'):
        print('\nUsage: '+__file__.split('/')[-1]+' HIVE_FILE')
        exit()
    if not isfile(argv[1]):
        print('\nUnable to open '+argv[1])
        exit()
    curses.wrapper(Gui,Hivex(argv[1]))

main()
