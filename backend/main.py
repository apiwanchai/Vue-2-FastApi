from fastapi import Depends, FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

DATABASE_URL = "mysql+pymysql://root@localhost/factory_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

origins = [
    "http://localhost:8080",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PartsChangeover(Base):
    __tablename__ = "parts_changeover"
    id = Column(Integer, primary_key=True, index=True)
    part_no = Column(String(50), unique=True, index=True, nullable=False)
    tg11111 = Column(Float, nullable=True)
    tg22222 = Column(Float, nullable=True)
    tg33333 = Column(Float, nullable=True)
    tg44444 = Column(Float, nullable=True)
    tg55555 = Column(Float, nullable=True)
    tg66666 = Column(Float, nullable=True)

Base.metadata.create_all(bind=engine)

class PartsChangeoverBase(BaseModel):
    part_no: str
    tg11111: Optional[float] = None
    tg22222: Optional[float] = None
    tg33333: Optional[float] = None
    tg44444: Optional[float] = None
    tg55555: Optional[float] = None
    tg66666: Optional[float] = None

class PartsChangeoverCreate(PartsChangeoverBase):
    pass

class PartsChangeoverSchema(PartsChangeoverBase):
    id: int

    class Config:
        orm_mode: True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/parts", response_model=List[PartsChangeoverSchema])
def read_parts(db: Session = Depends(get_db)):
    parts = db.query(PartsChangeover).all()
    return parts

@app.post("/parts", response_model=PartsChangeoverSchema)
def create_part(part: PartsChangeoverCreate, db: Session = Depends(get_db)):
    db_part = PartsChangeover(**part.dict())
    db.add(db_part)
    db.commit()
    db.refresh(db_part)
    return db_part

@app.post("/upload-excel/")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        data = pd.read_excel(io.BytesIO(contents))
        for index, row in data.iterrows():
            part = db.query(PartsChangeover).filter(PartsChangeover.part_no == row['Part No']).first()
            if part:
                part.tg11111 = row['TG11111']
                part.tg22222 = row['TG22222']
                part.tg33333 = row['TG33333']
                part.tg44444 = row['TG44444']
                part.tg55555 = row['TG55555']
                part.tg66666 = row['TG66666']
            else:
                new_part = PartsChangeover(
                    part_no=row['Part No'],
                    tg11111=row['TG11111'],
                    tg22222=row['TG22222'],
                    tg33333=row['TG33333'],
                    tg44444=row['TG44444'],
                    tg55555=row['TG55555'],
                    tg66666=row['TG66666']
                )
                db.add(new_part)
        db.commit()
        return {"message": "Data imported successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing data: {e}")

@app.get("/export-excel/")
def export_excel(db: Session = Depends(get_db)):
    parts = db.query(PartsChangeover).all()
    parts_data = [{"Part No": p.part_no, "TG11111": p.tg11111, "TG22222": p.tg22222, "TG33333": p.tg33333, "TG44444": p.tg44444, "TG55555": p.tg55555, "TG66666": p.tg66666} for p in parts]
    df = pd.DataFrame(parts_data)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    output.seek(0)
    return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={"Content-Disposition": "attachment; filename=parts_changeover.xlsx"})
