project('shuttlemessages',         version: '1.0.1',
  meson_version: '>= 0.46.0',
)

subdir('src')

message('Looking for dependencies...')

py3 = find_program('python3', required : true)

r = run_command(py3, '-c', '"import pymongo"')
if r.returncode() != 0
    error('Python - Cannot import pymongo.')
endif

r = run_command(py3, '-c', '"import smtplib"')
if r.returncode() != 0
    error('Python - Cannot import smtplib.')
endif

r = run_command(py3, '-c', '"import socket"')
if r.returncode() != 0
    error('Python - Cannot import socket.')
endif

r = run_command(py3, '-c', '"import email"')
if r.returncode() != 0
    error('Python - Cannot import email.')
endif

r = run_command(py3, '-c', '"import sqlite3"')
if r.returncode() != 0
    error('Python - Cannot import sqlite3.')
endif

install_data(sources : 'src/shuttlemessages.py', rename : 'shuttlemessages', install_dir : '/usr/local/bin')