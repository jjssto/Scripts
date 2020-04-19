#!/usr/bin/env python3

import gpg
import re
import os
import sys
from gpg.errors import GPGMEError, BadSignatures 
from datetime import datetime
from os import path

class Crypt_mail:
    
    indicator = "-----BEGIN PGP MESSAGE-----"
    tmp_dir = '/home/josef/Encfs/Plain/Mail/tmp'
    backup = True
    backup_dir = "/home/josef/Encfs/Plain/Mail/backup"
    key = "4A91C6C9D934106DF18EF88B45714E0878D6776E"
    log_file = "/home/josef/Encfs/Plain/Mail/log" 

    def __init__( self, crypt_file ):
        self.crypt = crypt_file
        self.name = os.path.basename(self.crypt)
        self.clear = Crypt_mail.tmp_dir + '/' + self.name 
        self.decrypted = False

    def __del__( self ):
        try:
            os.remove(self.clear)
        except OSError:
            pass

    def isPGP( self ):
        '''Tests wether the e-mail is pgp-encrypted'''
        try:
            with open(self.crypt,'r') as f:
                for line in f:
                    if line[0:27] == Crypt_mail.indicator:
                        return True
        except UnicodeDecodeError:
            return False
        return False

    def decrypt( self ):
        '''Decrypts the e-mail'''
        if self.isPGP() == False:
            return False
        else:
            c = gpg.Context()
            c.get_key( Crypt_mail.key, secret=True )
            with open(self.crypt,'r') as f_in:
                with open(self.clear,'w') as f_out:
                    try:
                        c.decrypt(f_in,f_out)
                    except GPGMEError as error:
                        self.log("decryption failed: " 
                                + self.name + ' ('
                                + str(error) + ')' )
                        return False
                    except BadSignatures as error:
                        self.log("bad signature: " 
                                + self.name + ' ('
                                + str(error) + ')' )
                        pass

                self.decrypted=True
            return True

    def replace( self ):
        """
        Replace the encrypted file with the decrypted one.
        The original is saved in the backup folder.
        """
        if self.decrypted == False:
            return False
        else:
            if Crypt_mail.backup == True:
                bckp_file = Crypt_mail.backup_dir + '/' + self.name 
                os.rename(self.crypt,bckp_file)
            else:
                os.remove(self.crypt)
            os.rename(self.clear,self.crypt)
            self.log( "decrypted " + self.name)
            return True

    def log(self, message):
        time_stamp = datetime.now()
        with open( Crypt_mail.log_file, 'a') as f:
            f.write(time_stamp.isoformat() + " > " + message 
                + '\n')
                

class Mailbox:
    
    def __init__(self, mail_dir ):
        self.mailbox = mail_dir

    def decrypt_all(self):
        dirs = os.listdir( self.mailbox )
        #dirs = os.scandir( self.mailbox )
        for folder in dirs:
            if folder in {'tmp','new'}:
                continue
            elif folder == 'cur':
                full_path = path.join(self.mailbox,'cur')
                self.decrypt_files( full_path )
            elif folder == '.Archiv':
                continue
            else:
                full_path = path.join(self.mailbox,folder,'cur')
                self.decrypt_files( full_path )
                
    def decrypt_files(self, folder):
        '''decrypts all encrypted mail in folder'''
        if path.isdir(folder):
            mails = os.scandir(folder)
            for mail in mails:
                if mail.name[0] == '.':
                    continue
                if path.isfile(mail.path):
                    crypt = Crypt_mail(mail.path)
                    if crypt.decrypt():
                        crypt.replace()
                    del crypt

if __name__ == "__main__":
    full_path = path.join( os.getcwd(), sys.argv[1] )
    mailbox = Mailbox( sys.argv[1] ) 
    mailbox.decrypt_all()
