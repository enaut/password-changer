# window.py
#
# Copyright 2019 Dietrich
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk
import paramiko
import getpass
import crypt
import string
import random
from .gi_composites import GtkTemplate

@GtkTemplate(ui='/de/Teilgedanken/change-password/window.ui')
class ChangePasswordWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'ChangePasswordWindow'

    confirm = GtkTemplate.Child()
    cancel = GtkTemplate.Child()
    apw = GtkTemplate.Child()
    npw = GtkTemplate.Child()
    npwconf = GtkTemplate.Child()
    errorlabel = GtkTemplate.Child()
    message = GtkTemplate.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.application = kwargs["application"]
        # This must occur *after* you initialize your base
        self.init_template()

        self.confirm.connect("clicked", self.on_confirm_clicked)
        self.cancel.connect("clicked", self.on_cancel_clicked)

    def on_confirm_clicked(self, button):
        print("\"Click me\" button was clicked")
        username = getpass.getuser()
        apwv = self.apw.get_text()
        npwv = self.npw.get_text()
        npwconfv = self.npwconf.get_text()
        if len(npwv) > 5 and (npwv == npwconfv):
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect("server", username=username, password=apwv)
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("passwd")
            print("interacting")
            ssh_stdin.write(apwv + '\n' + npwv + '\n' + npwv + '\n')
            ssh_stdin.channel.shutdown_write()
            print("done")
            self.errorlabel.set_visible(True)
            response = ssh_stderr.read().decode()
            cleaned = response.replace("(aktuelles) UNIX-Passwort:", '').replace("Geben Sie ein neues UNIX-Passwort ein:", '').replace("Geben Sie das neue UNIX-Passwort erneut ein:", '')
            self.message.set_text(cleaned)
            self.message.set_visible(True)
            if "erfolgreich geändert" in cleaned:
                self.confirm.set_visible(False)
    def on_cancel_clicked(self, button):
        self.application.quit()
