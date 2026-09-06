#-------------------------------------------------------------------------------
# Name:        cpyxlsclipsn.py
# Purpose:
#
# Author:      x
#
# Created:     22/06/2023
# Copyright:   (c) x 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import pandas as pd


df=pd.read_excel("C:\\Users\\kenners\\Downloads\\task.xlsx", engine='openpyxl')
df.to_clipboard(excel=True, sep=None, index=False)


#def main():
#    pass

#if __name__ == '__main__':
#    main()
