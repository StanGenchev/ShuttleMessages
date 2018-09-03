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

install_data(sources : 'src/shuttlemessages.py', rename : 'shuttlemessages', install_dir : '/usr/local/bin')