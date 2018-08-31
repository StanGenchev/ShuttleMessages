# ShuttleMessages
Collect message data from chat rooms in Rocket.Chat.

# How to install
Clone the repo:

```bash
git clone https://github.com/StanGenchev/ShuttleMessages.git
```

If running Debian/Ubuntu:
```bash
sudo yum install python3-pymongo postfix mailx
```

If running RedHat/CentOS/Fedora
```bash
sudo yum install python3-pymongo postfix mailx
```

```bash
mkdir /opt/shuttlemessages
cd ShuttleMessages/src
cp shuttlemessages.py /opt/shuttlemessages/shuttlemessages.py
```

# How to automate it

Add the following lines to your crontab:

MAILTO=""
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
59 20 * * *   /usr/bin/python3 /opt/shuttlemessages/shuttlemessages.py

You can add them using the command:
```bash
sudo crontab -e
```

# How to add/show/clear users
You can collect data from a set of users. The user name must be formated as "firstname.lastname" and the chat room as "firstname-lastname".

The following command will give you a list of all the users and it will give you the ability to select which ones are to be added:

```bash
python3 /opt/shuttlemessages/shuttlemessages.py --add-users
```

The following command will give you the ability to add a user manually:

```bash
python3 /opt/shuttlemessages/shuttlemessages.py --add-manually
```

To show all users from the monitored list:

```bash
python3 /opt/shuttlemessages/shuttlemessages.py --show-users
```

To clear all users from the monitored list:

```bash
python3 /opt/shuttlemessages/shuttlemessages.py --clear-users
```

# How to add/show/clear emails
You can add multiple emails to which the data will be send to.

```bash
python3 /opt/shuttlemessages/shuttlemessages.py --add-emails
```

To show all emails:

```bash
python3 /opt/shuttlemessages/shuttlemessages.py --show-emails
```

To clear all email:

```bash
python3 /opt/shuttlemessages/shuttlemessages.py --clear-emails
```

# How to clear collected database
You can clear all collected data using the command:

```bash
python3 /opt/shuttlemessages/shuttlemessages.py --clear-messages
```