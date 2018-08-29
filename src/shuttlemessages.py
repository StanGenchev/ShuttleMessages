#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""ShuttleMessages"""

import os
import sys
import datetime
import smtplib
import sqlite3
import socket
from email.message import EmailMessage

try:
    from pymongo import MongoClient
except:
    print("You must have pymongo installed in order for this program to work.\n" +
          "Install it using the command:\n" +
          "sudo apt install python3-pymongo\n" +
          "or:" +
          "sudo yum install python3-pymongo\n")

class ShuttleMessages:
    """ShuttleMessages"""
    def __init__(self):
        try:
            self.argument = sys.argv[1]
        except:
            self.argument = None

        self.base_folder = "/opt/shuttlemessages"
        
        self.log_file = "/var/log/shuttlemessages.log"
        
        self.collected_db_file = self.base_folder + "/collected.db"
        
        self.requirements_check()
        
        self.shuttledb, self.rocketdb = self.init_db_connection()
        
        self.users_to_monitor = self.get_monitored_users()
        
        self.rooms_to_monitor = []
        
        for user in self.users_to_monitor:
            self.rooms_to_monitor.append(user.replace('.', '-'))
        
        self.send_to_mails = self.get_emails()
        
        self.rocket_parties = self.rocketdb.parties
        
        self.rocket_users = self.rocket_parties.users
        
        self.rocket_rooms = self.rocket_parties.rocketchat_room
        
        self.rocket_messages = self.rocket_parties.rocketchat_message
        
        if self.argument is not None:
            if self.argument == "--add-users":
                self.add_users()
            
            elif self.argument == "--add-emails":
                self.add_emails()
            
            elif self.argument == "--clear-emails":
                self.shuttledb.cursor().execute("DELETE FROM Emails")
                self.shuttledb.commit()
                print("Emails cleared!")
                sys.exit(0)
            
            elif self.argument == "--clear-users":
                self.shuttledb.cursor().execute("DELETE FROM Users")
                self.shuttledb.commit()
                print("Users cleared!")
                sys.exit(0)
            
            else:
                print('Unknown argument - "', self.argument, '"\n')
                print("Available options:\n\t--add-users\t" +
                      "Add rocket.chat users to your monitored list." +
                      "\n\t--add-emails\t" +
                      "Add emails to which you would send the collected data." +
                      "\n\t--clear-users\t" +
                      "Remove all users from your monitored list." +
                      "\n\t--clear-emails\t" +
                      "Remove all emails from your 'send to' list.\n")
        
        self.rocketdb.close()
        
        self.shuttledb.close()

    def init_db_connection(self):
        """Initializes the connections to mongo and sqlite dbs"""
        
        conn = sqlite3.connect(self.collected_db_file)
        
        try:
            rocketdb = MongoClient('localhost', 27017)
        except:
            time = datetime.datetime.now()
            
            with open(self.log_file, "a") as log:
                log.write("Date: " +
                          str(time.year) +
                          "-" + str(time.month) +
                          "-" + str(time.day) +
                          "-" + str(time.hour) +
                          ":" + str(time.minute) +
                          " - Could not connect to mongo!\n")
            
            sys.exit("Error connecting to mongo!")
        
        return conn, rocketdb

    def create_collected_db(self):
        """Creates the tables in the sqlite db file if they do not exist"""
        conn = sqlite3.connect(self.collected_db_file)
        
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS `Messages` (
	    `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	    `username`	INTEGER,
	    `msgid`	INTEGER,
	    `time`	TEXT,
	    `message`	TEXT,
	    FOREIGN KEY(`username`) REFERENCES `Users`(`id`)
        );''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS `Emails` (
	    `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	    `email`	TEXT
        );''')
        
        c.execute('''CREATE TABLE `Users` (
	    `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	    `userid`	INTEGER,
	    `name`	TEXT
        );''')

        conn.commit()
        
        conn.close()

    def requirements_check(self):
        """Checks if the required files and folders exist"""
        
        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)
        
        try:
            os.stat(self.log_file)
        except:
            db_file = open(self.log_file, "w")
            db_file.close()
        
        try:
            os.stat(self.collected_db_file)
        except:
            self.create_collected_db()

    def get_emails(self):
        """Gets all emails"""
        emails = []
        
        for email in self.shuttledb.cursor().execute('SELECT email FROM Emails'):
            emails.append(email)
        
        return emails

    def send_mail(self, user, diff):
        """Sends mail"""
        try:
            for send_to_mail in self.send_to_mails:
                msg = EmailMessage()
                msg.set_content(diff)
                msg['Subject'] = user
                msg['From'] = "Shuttle" + "@" + socket.gethostname()
                msg['To'] = send_to_mail
                to_send = smtplib.SMTP('localhost')
                to_send.send_message(msg)
                to_send.quit()
        except:
            time = datetime.datetime.now()
            with open(self.log_file, "a") as log:
                log.write("Date: " +
                          str(time.year) +
                          "-" + str(time.month) +
                          "-" + str(time.day) +
                          "-" + str(time.hour) +
                          ":" + str(time.minute) +
                          " - Could not send email!\n")

    def get_reports(self):
        """Writes reports to file"""
        rids = self.rocket_rooms.find({"t":"p"}, {"_id":1, "name":1})
        for rid in rids:
            if rid['name'].replace('-', '.') in self.users_to_monitor:
                reports = self.rocket_messages.find({"rid":rid['_id']}, {"_id": 0, "msg":1, "ts":1})
                for report in reports:
                    all_reports += "\nTime Submitted: " + str(report["ts"]) + '\n\n' + report["msg"]
                init = 0
                try:
                    os.stat(self.reports_folder + '/' + rid["name"])
                except:
                    init = 1
                if init is 0:
                    old = ''
                    old_report = open(self.reports_folder + '/' + rid["name"], 'r')
                    old = old_report.read()
                    old_report.close()
                    if old == "" or old == " ":
                        diff = ""
                    else:
                        diff = "".join(all_reports.rsplit(old))
                    if diff == "" or diff == '' or diff == " " or diff == '\n':
                        time = datetime.datetime.now()
                        self.send_mail("NO REPORT: " + rid['name'],
                                       "Date: " + str(time.year) +
                                       "-" + str(time.month) +
                                       "-" + str(time.day) +
                                       "-" + str(time.hour) +
                                       ":" + str(time.minute) +
                                       ":" + str(time.second) +
                                       '\n\n' +
                                       "No report submitted since last check.")
                    else:
                        self.send_mail(rid['name'], diff)
                        with open(self.reports_folder + '/' + rid["name"], "w") as write_down:
                            write_down.write(all_reports)
                else:
                    for report in reports:
                        all_reports += report["msg"]
                    with open(self.reports_folder + '/' + rid["name"], "w") as write_down:
                        write_down.write(all_reports)

    def get_monitored_users(self):
        """Get all monitored users"""
        users = []
        
        for user in self.shuttledb.cursor().execute('SELECT userid FROM Users'):
            users.append(str(user))
        
        return users

    def add_users(self):
        """Add users to monitor"""
        usrs = self.rocket_users.find({"type":"user"}, {"_id":1, "username":1})
        
        print("Answer with 'y', 'n' or 'quit'.\n")
        
        for usr in usrs:
            question = input("Add " + str(usr['username']) + "? (y/n/quit): ")
            if question == 'y' or question == 'Y' or question == 'Yes' or question == 'YES':
                self.shuttledb.cursor().execute("INSERT INTO Users (userid, name) VALUES ('" + str(usr['_id']) + "','" + str(usr['username']) + "')")
            elif question == 'quit' or question == 'QUIT':
                break
        
        self.shuttledb.commit()

    def add_emails(self):
        """Add emails"""
        while True:
            email = input("Email: ")
            self.shuttledb.cursor().execute("INSERT INTO Emails (email) VALUES ('" + email + "')")
            yes_no = input("Do you want to add another email? (y/n): ")
            if yes_no == "n" or yes_no == "N" or yes_no == "no" or yes_no == "No":
                print("Emails added.")
                self.shuttledb.commit()
                break
            else:
                continue

def main():
    """Load the main class"""
    ShuttleMessages()

if __name__ == "__main__":
    main()
