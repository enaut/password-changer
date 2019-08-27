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
import re
from .gi_composites import GtkTemplate
from gettext import gettext as _

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

        self.apw.next_field = self.npw
        self.npw.next_field = self.npwconf
        self.npwconf.next_field = self.confirm
        self.apw.connect("activate", self.next_field)
        self.npw.connect("activate", self.next_field)
        self.npwconf.connect("activate", self.next_field)


        self.confirm.connect("clicked", self.on_confirm_clicked)
        self.cancel.connect("clicked", self.on_cancel_clicked)

    def on_confirm_clicked(self, button):
        username = getpass.getuser()
        apwv = self.apw.get_text()
        npwv = self.npw.get_text()
        npwconfv = self.npwconf.get_text()
        if len(npwv) < 6:
            self.message.set_text(_("The password is too short!"))
            self.message.set_visible(True)
            self.errorlabel.set_visible(True)
        if npwv != npwconfv:
            self.message.set_text(_("The new passwords do not match!"))
            self.message.set_visible(True)
            self.errorlabel.set_visible(True)
        else:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect("server", username=username, password=apwv)
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("passwd")
                ssh_stdin.write(apwv + '\n' + npwv + '\n' + npwv + '\n')
                ssh_stdin.channel.shutdown_write()
                exit_status = ssh_stdout.channel.recv_exit_status()

                if exit_status == 0:
                    self.message.set_text(_("The password has been changed"))
                    self.message.set_visible(True)
                    self.errorlabel.set_visible(False)
                    self.confirm.set_visible(False)

                elif exit_status == 1:
                    self.message.set_text(_("Permission denied"))
                    self.message.set_visible(True)
                    self.errorlabel.set_visible(True)

                elif exit_status == 10:
                    self.message.set_text(_("The new password cannot be the same as the old one"))
                    self.message.set_visible(True)
                    self.errorlabel.set_visible(True)
                else:
                    # show some error message from the server.
                    self.errorlabel.set_visible(True)
                    response = ssh_stderr.read().decode()
                    self.message.set_text(response)
                    self.message.set_visible(True)

            except paramiko.ssh_exception.AuthenticationException:
                    self.message.set_text(_("The old password entered was not valid"))
                    self.message.set_visible(True)
                    self.errorlabel.set_visible(True)


    def on_cancel_clicked(self, button):
        self.application.quit()

    def next_field(self, entry):
        # Move the focus to the next field
        if entry.next_field is not None:
            entry.next_field.grab_focus()
