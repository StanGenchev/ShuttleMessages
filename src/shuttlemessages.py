#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""ShuttleMessages"""

import sys

try:
    assert sys.version_info >= (3,0)
except:
    print('This is a python 3 application, but you are running python 2.')
    sys.exit(1)

import os
import datetime
import smtplib
import sqlite3
import socket

from email.message import EmailMessage

try:
    from pymongo import MongoClient
except:
    print("You must have pymongo installed in order for this program to work.\n\n" +
          "Install it using the command:\n" +
          "sudo pip3 install pymongo\n")
    sys.exit(1)

class ShuttleMessages:
    """ShuttleMessages"""
    def __init__(self):
        try:
            self.argument = sys.argv[1]
        except:
            self.argument = None

        self.dbase_folder = "/var/shuttlemessages"
        
        self.log_file = "/var/log/shuttlemessages.log"
        
        self.collected_db_file = self.dbase_folder + "/collected.db"
        
        self.requirements_check()
        
        self.shuttledb, self.rocketdb = self.init_db_connection()
        
        self.users_to_monitor = self.get_monitored_users()
        
        self.send_to_mails = self.get_emails()
        
        self.messages_count = self.get_messages_count()

        self.rocket_parties = self.rocketdb.parties
        
        self.rocket_users = self.rocket_parties.users
        
        self.rocket_rooms = self.rocket_parties.rocketchat_room
        
        self.rocket_messages = self.rocket_parties.rocketchat_message
        
        if self.argument is not None:
            if self.argument == "--add-users" or self.argument == "-u":
                self.add_users()
                sys.exit(0)
            
            elif self.argument == "--add-manually" or self.argument == "-am":
                user = input("User: ")
                self.shuttledb.cursor().execute("INSERT INTO Users (name) VALUES ('" + user + "');")
                self.shuttledb.commit()
                print("User added!")
                sys.exit(0)

            elif self.argument == "--add-emails" or self.argument == "-e":
                self.add_emails()
                sys.exit(0)

            elif self.argument == "--show-users" or self.argument == "-su":
                for user in self.users_to_monitor:
                    print(user)
                sys.exit(0)

            elif self.argument == "--remove-user" or self.argument == "-ru":
                self.remove_user()
                sys.exit(0)

            elif self.argument == "--show-emails" or self.argument == "-se":
                for email in self.send_to_mails:
                    print(email)
                sys.exit(0)
            
            elif self.argument == "--remove-email" or self.argument == "-re":
                self.remove_email()
                sys.exit(0)

            elif self.argument == "--clear-emails" or self.argument == "-ce":
                self.shuttledb.cursor().execute("DELETE FROM Emails")
                self.shuttledb.commit()
                print("Emails cleared!")
                sys.exit(0)
            
            elif self.argument == "--clear-users" or self.argument == "-cu":
                self.shuttledb.cursor().execute("DELETE FROM Users")
                self.shuttledb.commit()
                print("Users cleared!")
                sys.exit(0)
            
            elif self.argument == "--collect" or self.argument == "-c":
                self.get_messages(False)
                sys.exit(0)

            elif self.argument == "--clear-messages" or self.argument == "-cm":
                self.shuttledb.cursor().execute("DELETE FROM Messages")
                self.shuttledb.commit()
                print("Messages cleared!")
                sys.exit(0)

            else:
                if self.argument == "--help" or self.argument == "-h":
                    print("Available options:\n")

                else:
                    print('Unknown argument - "' + self.argument + '"\nAvailable options:\n')

                print("  -h,  --help\t\t\t" +
                      "Show this help information." +
                      "\n  -u,  --add-users\t\t" +
                      "Add rocket.chat users to your monitored list." +
                      "\n  -u,  --add-manually\t\t" +
                      "Add rocket.chat users to your monitored list by typing the name manually." +
                      "\n  -e,  --add-emails\t\t" +
                      "Add emails to which you would send the collected data." +
                      "\n  -c,  --collect\t\t" +
                      "Collect messages from users and do not send emails." +
                      "\n  -su, --show-users\t\t" +
                      "Show all monitored users." +
                      "\n  -ru, --remove-user\t\t" +
                      "Remove a user from the monitored list." +
                      "\n  -se, --show-emails\t\t" +
                      "Show all 'send to' emails." +
                      "\n  -re, --remove-email\t\t" +
                      "Remove email from the 'send to' list." +
                      "\n  -cu, --clear-users\t\t" +
                      "Remove all users from your monitored list." +
                      "\n  -ce, --clear-emails\t\t" +
                      "Remove all emails from your 'send to' list." +
                      "\n  -cm, --clear-messages\t\t" +
                      "Remove all messages from the collected database.\n")
                sys.exit(1)
        
        self.get_messages(True)

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
	    `username`	TEXT,
	    `msgid`	TEXT,
	    `time`	TEXT,
	    `message`	TEXT
        );''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS `Emails` (
	    `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	    `email`	TEXT
        );''')
        
        c.execute('''CREATE TABLE `Users` (
	    `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	    `name`	TEXT
        );''')

        conn.commit()
        
        conn.close()

    def requirements_check(self):
        """Checks if the required files and folders exist"""
        
        if not os.path.exists(self.dbase_folder):
            os.makedirs(self.dbase_folder)
        
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
            emails.append(str(email[0]))
        
        return emails

    def send_mail(self, messages):
        """Sends mail"""
        try:
            for key, val in messages.items():
                msg = EmailMessage()
                msg.set_content(val)
                msg['Subject'] = str(key.replace('.', ' ') + ' report.').title()
                msg['From'] = "Shuttle" + "@" + socket.gethostname()
                msg['To'] = ', '.join(self.send_to_mails)
                to_send = smtplib.SMTP('localhost')
                to_send.send_message(msg)
                to_send.quit()

            for user in self.users_to_monitor:
                if user not in messages.keys():
                    msg = EmailMessage()
                    msg.set_content("This user did not write his report!")
                    msg['Subject'] = str('No Report - ' + user.replace('.', ' ')).title()
                    msg['From'] = "Shuttle" + "@" + socket.gethostname()
                    msg['To'] = ', '.join(self.send_to_mails)
                    to_send = smtplib.SMTP('localhost')
                    to_send.send_message(msg)
                    to_send.quit()
        except:
            print('Error - Could not send email!')
            time = datetime.datetime.now()
            with open(self.log_file, "a") as log:
                log.write("Date: " +
                          str(time.year) +
                          "-" + str(time.month) +
                          "-" + str(time.day) +
                          "-" + str(time.hour) +
                          ":" + str(time.minute) +
                          " - Could not send email!\n")

    def get_messages(self, email):
        """Writes reports to file"""

        rids = self.rocket_rooms.find({"t":"p"}, {"_id":1, "name":1})

        for rid in rids:
            user = rid['name'].replace('-', '.')
            if user in self.users_to_monitor:
                reports = self.rocket_messages.find({"rid":rid['_id']}, {"_id": 1, "msg":1, "ts":1})
                for report in reports:
                    self.shuttledb.cursor().execute("INSERT INTO Messages (username, msgid, time, message) SELECT '" + user + "','" + str(report["_id"]) + "','" + str(report["ts"]) + "'," + '"' + str(report["msg"]).replace('"', "'") + '" WHERE NOT EXISTS(SELECT username, msgid FROM Messages WHERE msgid = ' + "'" + str(report["_id"]) + "' AND username = '" + user + "')")

        self.shuttledb.commit()

        if email:
            current_count = self.get_messages_count()

            msgs = {}

            if self.messages_count < current_count:
                for msg in self.shuttledb.cursor().execute('SELECT id, username, time, message FROM Messages ORDER BY id DESC LIMIT ' + str(current_count - self.messages_count)):
                    if str(msg[1]) in msgs.keys():
                        msgs[str(msg[1])] += '\nTime - ' + str(msg[2]) + '\n\n' + str(msg[3] + '\n')
                    else:
                        msgs[str(msg[1])] = 'Time - ' + str(msg[2]) + '\n\n' + str(msg[3] + '\n')
            self.send_mail(msgs)


    def get_monitored_users(self):
        """Get all monitored users"""
        users = []
        
        for user in self.shuttledb.cursor().execute('SELECT name FROM Users'):
            users.append(str(user[0]))

        return users

    def get_messages_count(self):
        """Get all monitored users"""
        count = 0

        count = self.shuttledb.cursor().execute('SELECT count(*) FROM Messages').fetchall()

        return int(count[0][0])

    def add_users(self):
        """Add users to monitor"""
        usrs = self.rocket_users.find({"type":"user"}, {"_id":0, "username":1})
        
        print("Answer with 'y', 'n' or 'quit'.\n")
        
        for usr in usrs:
            question = input("Add " + str(usr['username']) + "? (y/n/quit): ")
            if question == 'y' or question == 'Y' or question == 'Yes' or question == 'yes' or question == 'YES':
                self.shuttledb.cursor().execute("INSERT INTO Users (name) VALUES ('" + str(usr['username']) + "')")
            elif question == 'quit' or question == 'QUIT' or question == 'Quit':
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

    def remove_user(self):
        for user in self.users_to_monitor:
            question = input("Remove user - '" + user + "'? (y/n/quit): ")
            if question == 'y' or question == 'Y' or question == 'Yes' or question == 'yes' or question == 'YES':
                self.shuttledb.cursor().execute("DELETE FROM Users WHERE name='" + user + "'")
            elif question == 'quit' or question == 'QUIT' or question == 'Quit':
                break
        self.shuttledb.commit()

    def remove_email(self):
        for email in self.send_to_mails:
            question = input("Remove email - '" + email + "'? (y/n/quit): ")
            if question == 'y' or question == 'Y' or question == 'Yes' or question == 'yes' or question == 'YES':
                self.shuttledb.cursor().execute("DELETE FROM Emails WHERE email='" + email + "'")
            elif question == 'quit' or question == 'QUIT' or question == 'Quit':
                break
        self.shuttledb.commit()

def main():
    """Check permissions and load the main class"""
    if os.geteuid() != 0:
        print('You need root permissions to run this program!')
        sys.exit(1)
    ShuttleMessages()

if __name__ == "__main__":
    main()