#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""ShuttleMessages"""

import os
import sys
import datetime
import smtplib
import socket
from email.message import EmailMessage
try:
    from pymongo import MongoClient
except:
    print("You must have pymongo installed in order for this program to work.\n" +
          "Install it using the command:\n" +
          "sudo apt install python3-pymongo\n")

class ShuttleMessages:
    """ShuttleMessages"""
    def __init__(self):
        try:
            self.argument = sys.argv[1]
        except:
            self.argument = "no-arg"
        self.base_folder = "/opt/shuttlemessages"
        self.users_to_monitor_file = "/opt/shuttlemessages/users"
        self.users_to_monitor = []
        self.rooms_to_monitor = []
        self.reports_folder = "/opt/shuttlemessages/reports"
        self.emails_file = "/opt/shuttlemessages/shuttle.mails"
        self.log_file = "/var/log/shuttlemessages.log"
        self.send_to_mails = []
        self.requirements_check()
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
            clear = open(self.emails_file, "w")
            clear.write('')
            clear.close()
        elif self.argument == "--clear-users":
            clear = open(self.users_to_monitor_file, "w")
            clear.write('')
            clear.close()
        else:
            self.load_usernames()
            self.load_emails()
            self.get_reports()
        self.client.close()

    def requirements_check(self):
        """Checks if the required files and folders exist"""
        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)
        if not os.path.exists(self.reports_folder):
            os.makedirs(self.reports_folder)
        try:
            os.stat(self.emails_file)
        except:
            db_file = open(self.emails_file, "w")
            db_file.close()
        try:
            os.stat(self.log_file)
        except:
            db_file = open(self.log_file, "w")
            db_file.close()
        try:
            os.stat(self.users_to_monitor_file)
        except:
            db_file = open(self.users_to_monitor_file, "w")
            db_file.close()

    def load_emails(self):
        """Load all email form file"""
        with open(self.emails_file) as mail:
            mails = mail.readlines()
            for single_mail in mails:
                if single_mail == "\n":
                    break
                else:
                    self.send_to_mails.append(single_mail.replace('\n', ''))

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
        rids = self.all_rooms.find({"t":"p"}, {"_id":1, "name":1})
        for rid in rids:
            if rid['name'].replace('-', '.') in self.users_to_monitor:
                reports = self.all_messages.find({"rid":rid['_id']}, {"_id": 0, "msg":1, "ts":1})
                all_reports = ''
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

    def load_usernames(self):
        """Load all usernames from file"""
        self.users_to_monitor.clear()
        with open(self.users_to_monitor_file) as usrs:
            users = usrs.readlines()
            for single_user in users:
                if single_user == "\n":
                    break
                else:
                    self.users_to_monitor.append(single_user.replace('\n', ''))

    def add_users(self):
        """Add users to monitor"""
        usrs = self.all_users.find({"type":"user"}, {"_id":0, "username":1})
        for usr in usrs:
            print("\nUser: " + str(usr['username']))
            yn = input("Do you want to add this user? (y/n): ")
            if yn == 'y' or yn == 'Y' or yn == 'Yes' or yn == 'YES':
                with open(self.users_to_monitor_file, "a") as usr_file:
                    usr_file.write(str(usr['username']) + '\n')

    def add_emails(self):
        """Add emails"""
        email = ''
        while True:
            email = email + input("Email: ") + '\n'
            yes_no = input("Do you want to add another email? (y/n): ")
            if yes_no == "n" or yes_no == "N" or yes_no == "no" or yes_no == "No":
                with open(self.emails_file, "a") as emails:
                    emails.write(email)
                print("Emails added.")
                break
            else:
                continue

def main():
    """Load the main class"""
    ShuttleMessages()

if __name__ == "__main__":
    main()
