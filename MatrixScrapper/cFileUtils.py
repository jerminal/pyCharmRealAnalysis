import os
import shutil
import glob

class cFileUtils:

    def get_download_path(self):
        """Returns the default downloads path for linux or windows"""
        if os.name == 'nt':
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            return location
        else:
            return os.path.join(os.path.expanduser('~'), 'downloads')

    def move_file(self,src_file_name, dest_file_name):
        '''
        Move files in one location to another and rename it
        :param src_file_name: full path of the source file
        :param dest_file_name: full path of the destination file name
        :return: True or false
        '''
        try:
            shutil.move(src_file_name, dest_file_name)
            return True
        except:
            return False

    def delete_files(self, strFileNames):
        '''
        delete some files,
        :param strFileNames: file names, it supports wild cards
        :return:
        '''
        fileList = glob.glob(strFileNames)
        if fileList is not None:
            for file in fileList:
                try:
                    os.remove(file)
                except:
                    print("Error! Attempt to delete {0} failed.".format(file))
            return True
        else:
            return False
