from app import crud
from app.db.session import SessionLocal

db = SessionLocal()
print(db)

from app.worker.uipath import FetchUIPathToken

FetchUIPathToken()

# CHECK FOLDER

folderlist = [2440043]

for folderid in folderlist:
    a = crud.uip_folder.get(db=db, id=folderid)
