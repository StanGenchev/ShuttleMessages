#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""ShuttleMessages"""

import os
import sys
import datetime
import smtplib
import socket
import sqlite3
from email.message import EmailMessage

current_directory = os.getcwd() + "/"

try:
    from pymongo import MongoClient
except:
    print("You must have pymongo installed in order for this program to work.\n" +
          "Install it using the command:\n" +
          "sudo apt install python3-pymongo\nsudo dnf install python3-pymongo\n")

class ShuttleMessages:
    """ShuttleMessages"""
    def __init__(self):
        try:
            self.argument = sys.argv[1]
        except:
            self.argument = "no-arg"

        self.database = current_directory + 'reports.db'
        self.base_folder = current_directory
        self.log_file = "/var/log/shuttlemessages.log"
        #self.requirements_check()
        self.conn = sqlite3.connect(current_directory + 'reports.db')
        self.users_to_monitor = self.conn.execute("SELECT id, username, report_num FROM users")
        self.rooms_to_monitor = []
        self.emails = dict(self.conn.execute("SELECT email FROM emails"))
        print(self.users_to_monitor.fetchone())
        print(self.users_to_monitor.fetchone())
        print(self.users_to_monitor.fetchone())

        try:
            self.client = MongoClient('localhost', 27017)
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

        self.db = self.client.parties
        self.all_users = self.db.users
        self.all_rooms = self.db.rocketchat_room
        self.all_messages = self.db.rocketchat_message
        if self.argument == "--add-users":
            self.add_users()
        elif self.argument == "--add-emails":
            self.add_emails()
        elif self.argument == "--clear-emails":
            self.conn.execute("DELETE FROM emails")
            self.conn.commit()
        elif self.argument == "--clear-users":
            self.conn.execute("DELETE FROM users")
            self.conn.commit()
        else:
            self.get_reports()
        self.client.close()

    def requirements_check(self):
        """Checks if the required files and folders exist"""
        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)
        try:
            os.stat(self.database)
        except:
            self.conn.execute("CREATE TABLE IF NOT EXISTS 'users' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'username' TEXT);")
            self.conn.execute("CREATE TABLE IF NOT EXISTS 'reports' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'user_id' INTEGER, 'time' TEXT, 'report' TEXT);")
            self.conn.execute("CREATE TABLE IF NOT EXISTS 'emails' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'email' TEXT);")
            self.conn.commit()

    def send_mail(self, user, diff):
        """Sends mail"""
        try:
            for send_to_mail in self.emails:
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

    def get_all_reports(self):
        """Writes reports to db"""
        rids = self.all_rooms.find({"t":"p"}, {"_id":1, "name":1})
        for rid in rids:
            usr = rid['name'].replace('-', '.')
            if usr in self.users_to_monitor.values():
                reports = self.all_messages.find({"rid":rid['_id']}, {"_id": 1, "msg":1, "ts":1})
                for report in reports:
                    self.conn.execute("INSERT INTO reports (id, user_id, time, report) VALUES ( " + str(report["_id"]) + ", '" + self.users_to_monitor[usr] + "', '" + str(report["ts"]) + "', '" + str(report["msg"]) + "' );")
                self.send_mail(rid['name'], diff)
                with open(self.reports_folder + '/' + rid["name"], "w") as write_down:
                        write_down.write(all_reports)
                else:
                    for report in reports:
                        all_reports += report["msg"]
                    with open(self.reports_folder + '/' + rid["name"], "w") as write_down:
                        write_down.write(all_reports)

    def latest_report(self):
        

    def add_users(self):
        """Add users to monitor"""
        usrs = self.all_users.find({"type":"user"}, {"_id":1, "username":1})
        for usr in usrs:
            print("\nUser: " + str(usr['username']))
            yn = input("Do you want to add this user? (y/n): ")
            if yn == 'y' or yn == 'Y' or yn == 'Yes' or yn == 'YES':
                self.conn.execute("INSERT INTO users (id, name) VALUES ( '" + str(usr['_id']) + "', '" + str(usr['username']) + "' );")
                self.conn.commit()

    def add_emails(self):
        """Add emails"""
        email = ''
        while True:
            email = input("Email: ")
            yes_no = input("Do you want to add another email? (y/n): ")
            if yes_no == "n" or yes_no == "N" or yes_no == "no" or yes_no == "No":
                self.conn.commit()
                break
            else:
                self.conn.execute("INSERT INTO emails (email) VALUES ( '" + email + "' );")

def main():
    """Load the main class"""
    ShuttleMessages()

if __name__ == "__main__":
    main()
