#!/usr/bin/env python

#Python "Sticky" Note Application
#Copyright (C) 2012  Nick Hu

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import traceback
import sqlite3
try:
  from gi.repository import Gtk
  from gi.repository import Gdk
except:
  print 'GTK3 Unavailable\nStack trace: '
  traceback.print_exc()
  sys.exit(1)

class PystDB:

  def __init__(self, con = None):
    self.con = sqlite3.connect('pysted.db')

  def writeNote(self, noted):

    with self.con:

      cur = self.con.cursor()

      cur.executescript('''
        --DROP TABLE IF EXISTS Notes;
        CREATE TABLE IF NOT EXISTS Notes(Title TEXT PRIMARY KEY, Note TEXT);
        ''')

      try:
        cur.executemany('INSERT INTO Notes VALUES (?, ?)', noted)
      
      except sqlite3.IntegrityError:
        PystIt.error(None, 'Non unique title!')

  def readNote(self):

    with self.con:

      self.con.row_factory = sqlite3.Row

      cur = self.con.cursor()

      try:
        cur.execute('SELECT * FROM Notes')
      except sqlite3.OperationalError:
        print "Database does not exist!"
        return 0

      rows = cur.fetchall()

      #print '%s %s %s' % (rows.keys()[0], rows.keys()[1], rows.keys()[2])
      #print rows.keys()
      #for row in rows:
      #  print '%s %s' % (row['Title'], row['Note'])
      return rows

class PystIt:

  def __init__(self):
    try:
      self.builder = Gtk.Builder()
      self.builder.add_from_file('PystIt.ui')
    except:
      self.error('Failed to load UI XML file: PystIt.ui')
      sys.exit(1)

    self.builder.connect_signals(self)
    # self.builder.get_object('windowMain').set_events(Gdk.EventMask.FOCUS_CHANGE_MASK)

    self.focused = None

    self.pystit = PystDB()

    # if self.focused:
    #   for i in args[2]:
    #     i.set_sensitive(True)
    # else:
    #   for i in args[2]:
    #     i.set_sensitive(False)

  def main(self):
    Gtk.main()

  @staticmethod
  def error(self, message):
    print message
    dialog = Gtk.MessageDialog(None,
      Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
      Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, message)
    dialog.set_type_hint(Gdk.WindowTypeHint.MENU)
    dialog.run()
    dialog.destroy()

  def gtk_widget_hide(self, window, event):
    window.hide()
    return True

  def on_windowMain_delete_event(self, *args):
    Gtk.main_quit(*args)

  def on_imagemenuitemSave_activate(self, *args):
    notes = []
    for i in range(0, args[0].get_n_pages()):
      note = (args[0].get_tab_label_text(args[0].get_nth_page(i)), args[0].get_nth_page(i).get_child().get_buffer().get_text(args[0].get_nth_page(i).get_child().get_buffer().get_start_iter(), args[0].get_nth_page(i).get_child().get_buffer().get_end_iter(), 1))
      notes.append(note)
    self.pystit.writeNote(notes)

  def on_imagemenuitemOpen_activate(self, *args):
    rows = self.pystit.readNote()
    for row in rows:
      editor = Gtk.ScrolledWindow()
      editor.add(Gtk.TextView())
      editor.set_shadow_type(Gtk.ShadowType.IN)
      
      sensitiveitems = [\
        self.builder.get_object('imagemenuitemCut'),\
        self.builder.get_object('imagemenuitemCopy'),\
        self.builder.get_object('imagemenuitemPaste'),\
        self.builder.get_object('imagemenuitemDelete'),\
        self.builder.get_object('imagemenuitemClose'),\
        ]
  
      editor.get_child().connect('focus-in-event', self.on_editor_focus_in_event, sensitiveitems)
      editor.get_child().connect('focus-out-event', self.on_editor_focus_out_event, sensitiveitems)
      editor.get_child().get_buffer().set_text(row['Note'])
      editor.show_all()
      args[0].append_page(editor, Gtk.Label(row['Title']))

  def on_imagemenuitemNew_activate(self, *args):
    self.builder.get_object('windowTitle').show_all()

  def on_entryTitle_activate(self, *args):
    text = self.builder.get_object('entryTitle').get_text()
    self.builder.get_object('windowTitle').hide()
    editor = Gtk.ScrolledWindow()
    editor.add(Gtk.TextView())
    editor.set_shadow_type(Gtk.ShadowType.IN)
    
    sensitiveitems = [\
      self.builder.get_object('imagemenuitemCut'),\
      self.builder.get_object('imagemenuitemCopy'),\
      self.builder.get_object('imagemenuitemPaste'),\
      self.builder.get_object('imagemenuitemDelete'),\
      self.builder.get_object('imagemenuitemClose'),\
      ]

    editor.get_child().connect('focus-in-event', self.on_editor_focus_in_event, sensitiveitems)
    editor.get_child().connect('focus-out-event', self.on_editor_focus_out_event, sensitiveitems)
    editor.show_all()
    args[0].append_page(editor, Gtk.Label(text))
    
  def on_editor_focus_in_event(self, *args):
    self.focused = args[0]
    for si in args[2]:
      si.set_sensitive(True)
    #print self.focused

  def on_editor_focus_out_event(self, *args):    
    self.focused = args[0]
    for si in args[2]:
      si.set_sensitive(False)
    #print self.focused

  def on_imagemenuitemClose_activate(self, *args):
    args[0].remove_page(args[0].get_current_page())
  def on_imagemenuitemAbout_activate(self, *args):
    args[0].show()
    response = args[0].run()
    if response == Gtk.ResponseType.DELETE_EVENT or response == Gtk.ResponseType.CANCEL:
      args[0].hide()
  def on_imagemenuitemCut_activate(self, *args):
    try:
      args[0].get_focus_child().get_child().get_buffer().cut_clipboard(args[0].get_focus_child().get_child().get_clipboard(Gdk.SELECTION_CLIPBOARD), True)
    except AttributeError:
      self.error('No selection!')
  def on_imagemenuitemCopy_activate(self, *args):
    try:
      args[0].get_focus_child().get_child().get_buffer().copy_clipboard(args[0].get_focus_child().get_child().get_clipboard(Gdk.SELECTION_CLIPBOARD))
    except AttributeError:
      self.error('No selection!')
  def on_imagemenuitemPaste_activate(self, *args):
    try:
      args[0].get_focus_child().get_child().get_buffer().paste_clipboard(args[0].get_focus_child().get_child().get_clipboard(Gdk.SELECTION_CLIPBOARD), None, True)
    except AttributeError:
      self.error('No cursor!')
  def on_imagemenuitemDelete_activate(self, *args):
    try:
      args[0].get_focus_child().get_child().get_buffer().delete_selection(False, False)
    except AttributeError:
      self.error('No selection!')

if __name__ == '__main__':
  pystit = PystIt()
  pystit.main()
