import pandas as pd
 import os
import psycopg2
import re

pw='***'

mugshotsfolder = '/opt/openlattice/data/johnson_booking'
images = os.listdir(mugshotsfolder)

# read table with columns: [Index_ID] = MNI numbers, [Image_ID] = index with link to other table
smarttable = pd.read_csv('/opt/openlattice/data/johnson_booking/smart_image.csv', index_col="Image_ID")
# read table with columns: [ExtractFilePath] = path to image, [Image_ID] = link to smarttable
datatable = pd.read_csv('/opt/openlattice/data/johnson_booking/tblExtractedPhotos1.csv',index_col="Image_ID")

conn = psycopg2.connect(f"dbname=*** port=*** user=*** password={pw} host=***")
cur = conn.cursor()

tableno = 1
cur.execute(f"CREATE TABLE jail_mugshots_{tableno} (mni varchar(50), imagestring bytea)")

cntr = 0
for idx,row in datatable.iterrows():
    cntr += 1
    MNI = "\'{"+smarttable.loc[row.name]['Index_ID']+"}\'"
    Jail_ID_re = re.search('(\d+)(?:_\d+.JPG\'?)', row.ExtractFilePath)

    if Jail_ID_re != None:
        Jail_ID = Jail_ID_re.group(1)
        if df[(df['MNI_No'] == MNI) & (df['Jail_ID'] == Jail_ID)].shape[0] > 0:   
            image = psycopg2.Binary(open(os.path.join(mugshotsfolder,row.ExtractFilePath), 'rb').read())
            cur.execute(f"INSERT INTO jail_mugshots_{tableno} (mni, imagestring, Jail_ID) VALUES ({MNI},{image},{Jail_ID})")
            if cntr % 10000 == 0:
                conn.commit()
                conn = psycopg2.connect("dbname=johnsoncounty_iowa port=30001 user=itjecc password={pw} host=atlas.openlattice.com")
                cur = conn.cursor()

                tableno += 1
                cur.execute(f"CREATE TABLE jail_mugshots_{tableno} (mni char(50), imagestring bytea)")
conn.commit()
