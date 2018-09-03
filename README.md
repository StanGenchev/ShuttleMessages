# ShuttleMessages
Collect message data from chat rooms in Rocket.Chat.

# How to build and install
Clone the repo:

```bash
git clone https://github.com/StanGenchev/ShuttleMessages.git
```

Install dependencies:

If running Debian/Ubuntu:
```bash
sudo apt install python3 python3-pip postfix mailutils
sudo pip3 install pymongo meson ninja
```

If running RedHat/CentOS/Fedora
```bash
sudo yum install python3 python3-pip postfix mailx
sudo pip3 install pymongo meson ninja
```

Build and install:

```bash
cd ShuttleMessages
meson builddir
cd builddir
sudo ninja install
```

# How to automate it

Add the following lines to your crontab:
```bash
MAILTO=""
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
59 20 * * *   /usr/bin/python3 /usr/local/bin/shuttlemessages
```

You can add them using the command:
```bash
sudo crontab -e
```

# How to add/show/remove/clear users
You can collect data from a set of users. The user name must be formated as "firstname.lastname" and the chat room as "firstname-lastname".

The following command will give you a list of all the users and it will give you the ability to select which ones are to be added:

```bash
shuttlemessages --add-users
```

The following command will give you the ability to add a user manually:

```bash
shuttlemessages --add-manually
```

To show all users from the monitored list:

```bash
shuttlemessages --show-users
```

To remove select users from the monitored list:

```bash
shuttlemessages --remove-user
```

To clear all users from the monitored list:

```bash
shuttlemessages --clear-users
```

# How to add/show/remove/clear emails
You can add multiple emails to which the data will be send to.

```bash
shuttlemessages --add-emails
```

To show all emails:

```bash
shuttlemessages --show-emails
```

To remove a select email:

```bash
shuttlemessages --remove-email
```

To clear all email:

```bash
shuttlemessages --clear-emails
```

# How to clear collected database
You can clear all collected data using the command:

```bash
shuttlemessages --clear-messages
```
