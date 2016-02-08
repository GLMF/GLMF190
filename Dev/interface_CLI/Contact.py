"""
    Objet Contact représentant un contact de l'Annuaire

    Author: Tristan Colombo <tristan@gnulinuxmag.com>
                            (@TristanColombo)

    Date: 17-12-2015

    Last modification: 17-12-2015

    Licence: GNU GPL v3 (voir fichier gpl_v3.txt joint)
"""


import sqlite3
import pystache
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders


class Contact:

    base = None
    cursor = None
    template = None
    send_from = 'tristan@gnulinuxmag.com'
    server = 'smtp.numericable.com'

    def __init__(self, name, db_args):
        name = name.split(' ')

        if len(name) != 2:
            print('Vous devez saisir un prénom suivi du nom')
            print('Syntaxe: Prénom Nom')
            exit(1)

        if Contact.base is None:
            Contact.base = db_args[0]
        if Contact.cursor is None:
            Contact.cursor = db_args[1]

        if Contact.template is None:
            try:
                with open('doc.tex', 'r') as fic:
                    Contact.template = fic.read()
            except:
                print('Accès impossible au gabarit')
                exit(3)

        self.forename = Contact.capitalizeName(name[0])
        self.name = Contact.capitalizeName(name[1])
        self.mail = self.searchMail()

    @staticmethod
    def capitalizeName(name):
        capitalized = ''
        pred = ''
        for letter in name:
            if pred in ('', ' ', '-'):
                if letter != ' ':
                    capitalized += letter.upper()
            else:
                capitalized += letter
            pred = letter

        return capitalized

    def isInDB(self):
        result = Contact.cursor.execute("""select name from Contact
                               where forename = ?
                               and name = ?""", (self.forename,
                                                 self.name))
        result = result.fetchone()
        return result is not None

    def addInDB(self):
        try:
            Contact.cursor.execute("""insert into Contact
                                   values(NULL, ?, ?, ?)""",
                                   (self.name, self.forename, self.mail))
            Contact.base.commit()
        except sqlite3.OperationalError:
            print('Erreur d\'écriture dans la base')
            exit(2)

    def searchMail(self):
        mail = Contact.cursor.execute("""select mail from Contact
                               where forename = ?
                               and name = ?""", (self.forename,
                                                 self.name))
        mail = mail.fetchone()
        if mail is None:
            return None
        else:
            return mail[0]

    def getMail(self):
        if self.__mail is None:
            return self.searchMail()
        else:
            return self.__mail
    def setMail(self, mail):
        if mail is None:
            self.__mail = None
        else:
            self.__mail = mail.lower()
            if self.isInDB():
                try:
                    Contact.cursor.execute("""update Contact
                                   set mail = ?
                                   where name = ?
                                   and forename = ?""",
                                   (self.mail, self.name, self.forename))
                    Contact.base.commit()
                except sqlite3.OperationalError:
                    print('Erreur d\'écriture dans la base')
                    exit(2)
            else:
                self.addInDB()
    mail = property(getMail, setMail)

    def getName(self):
        return self.__name
    def setName(self, name):
        self.__name = name
    name = property(getName, setName)

    def getForename(self):
        return self.__forename
    def setForename(self, forename):
        self.__forename = forename
    forename = property(getForename, setForename)

    def generateDoc(self, sun=False):
        try:
            with open('doc_contact.tex', 'w') as fic:
                fic.write(pystache.render(Contact.template,
                              {'name': self.name,
                               'forename': self.forename,
                               'sun': sun}))

            # Génération du PDF
            os.system('pdflatex doc_contact.tex 1>/dev/null')
        except:
            print('Erreur lors de la génération du PDF')
            exit(4)

    def sendMail(self):
        try:
            filename = 'doc_contact.pdf'
            msg = MIMEMultipart()
            msg['From'] = Contact.send_from
            msg['To'] = self.mail
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = 'Un petit message'

            msg.attach(MIMEText("""
                Hey!\n
                \n
                Ce n'est pas du SPAM, tu peux lire le fichier attaché!
            """))

            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(filename,'rb').read() )
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            'attachment; filename="{}"'.format(
                                os.path.basename(filename)))
            msg.attach(part)

            smtp = smtplib.SMTP(Contact.server)
            smtp.sendmail(Contact.send_from, self.mail,
                          msg.as_string().encode('utf-8'))
            smtp.close()
        except:
            print('Erreur lors de l\'envoi du mail')
            exit(4)
