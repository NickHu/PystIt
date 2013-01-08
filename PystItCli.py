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

# Command line interface to database file

import sys
import sqlite3

class PystDB:

	def __init__(self, con = None):
		self.con = sqlite3.connect('pysted.db')

	def writeNote(self, noted):

		with self.con:

			self.cur = self.con.cursor()

			self.cur.executescript('''
				--DROP TABLE IF EXISTS Notes;
				CREATE TABLE IF NOT EXISTS Notes(Title TEXT PRIMARY KEY, Note TEXT);
				''')

			self.cur.executemany('INSERT INTO Notes VALUES (?, ?)', noted)

	def readNote(self):

		with self.con:

			self.con.row_factory = sqlite3.Row

			self.cur = self.con.cursor()

			try:
				self.cur.execute('SELECT * FROM Notes')
			except sqlite3.OperationalError:
				print "Database does not exist!"
				return 0

			self.rows = self.cur.fetchall()

			#print '%s %s %s' % (rows.keys()[0], rows.keys()[1], rows.keys()[2])
			#print rows.keys()
			for row in self.rows:
				print '%s %s' % (row['Title'], row['Note'])

def main():
	pystit = PystDB()
	sel = 0
	while sel != '1' or sel != '2':
		sel = raw_input('Select mode\n1. READ\n2. WRITE\n')
		if sel == '1':
			pystit.readNote()
			# break
		elif sel == '2':
			noted = [(raw_input('Title: '), raw_input('Note: '))]
			pystit.writeNote(noted)
			# break
		else:
			print 'Invalid selection'

	raw_input('Done, press Enter to exit')

if __name__ == '__main__':
	main()
