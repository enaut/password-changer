pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'change_password')
gnome = import('gnome')

gnome.compile_resources('change-password',
  'change-password.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python3 = import('python3')

conf = configuration_data()
conf.set('PYTHON', python3.find_python().path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'change-password.in',
  output: 'change-password',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

change_password_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'gi_composites.py',
]

install_data(change_password_sources, install_dir: moduledir)
