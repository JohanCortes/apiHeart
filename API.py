from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from csvTable import csvTable
from draw import draw
from arbol_kd import arbol_kd
import pandas as pd

db = csvTable("heart.csv")
dw = draw("heart.csv")
tree = arbol_kd()

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FilaNueva(BaseModel):
    age: int
    sex: int
    cp: int
    trestbps: int
    chol: int
    fbs: int
    restecg: int
    thalach: int
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int
    target: int

class FilaClas(BaseModel):
    age: int
    sex: int
    cp: int
    trestbps: int
    chol: int
    fbs: int
    restecg: int
    thalach: int
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int

@app.get("/obtener_filas/")
def obtener_filas():
    res = db.obtener_filas()
    if not res:
        raise HTTPException(status_code=404, detail="No se encontraron resultados")
    return res

@app.get("/obtener_filas/{indice}")
def obtener_fila(indice: int):
    res = db.obtener_fila(indice)
    if not res:
        raise HTTPException(status_code=404, detail="No se encontraron resultados")
    return res

@app.get("/filtrar_filas/{columna}/{valor}")
def filtrar_filas(columnas: str, operadores: str, valores: str):
    res = db.filtrar_filas(columnas, valores, operadores)
    if not res:
        raise HTTPException(status_code=404, detail="No se encontraron resultados")
    return res

@app.post("/crear_fila/")
def crear_fila(fila: FilaNueva):
    res = db.crear_fila(fila.model_dump())
    if not res:
        raise HTTPException(status_code=403, detail="No se agregó la fila")
    return {"msg": "Fila creada exitosamente", "row": res}

@app.put("/actualizar_fila/{indice}")
def actualizar_fila(indice: int, fila: FilaNueva):
    res = db.actualizar_fila(indice, fila.model_dump())
    if not res:
        raise HTTPException(status_code=403, detail="No se actualizó la fila")
    return {"msg": "Fila actualizada exitosamente", "row": res}

@app.delete("/eliminar_fila/{indice}")
def eliminar_fila(indice: int):
    res = db.eliminar_fila(indice)
    if not res:
        raise HTTPException(status_code=403, detail="No se eliminó la fila")
    return {"msg": "Fila eliminada exitosamente"}

@app.get("/scatter/")
async def draw_graph(colx: str, coly: str, nombre: str, columnas: str = None, operadores: str = None, valores: str = None):
    res = await dw.scatter_graph(colx, coly, nombre, columnas, valores, operadores)
    if not res:
        raise HTTPException(status_code=404, detail="No se encontraron resultados")
    return FileResponse(res)

@app.get("/bar/")
async def draw_graph(col: str, rango: float, nombre: str, columnas: str = None, operadores: str = None, valores: str = None):
    res = await dw.bar_graph(col, rango, nombre, columnas, valores, operadores)
    if not res:
        raise HTTPException(status_code=404, detail="No se encontraron resultados")
    return FileResponse(res)

@app.get("/pie/")
async def draw_graph(col: str, rango: float, nombre: str, columnas: str = None, operadores: str = None, valores: str = None):
    res = await dw.pie_graph(col, rango, nombre, columnas, valores, operadores)
    if not res:
        raise HTTPException(status_code=404, detail="No se encontraron resultados")
    return FileResponse(res)

@app.post("/clasificar/")
def clasificar(fila: FilaClas, guardar: bool = False):
    dict = fila.model_dump()
    row = pd.DataFrame([list(dict.values())], columns=['age','sex','cp','trestbps','chol','fbs','restecg','thalach','exang','oldpeak','slope','ca','thal'])
    res = tree.classify_row(row.iloc[0])
    fila = FilaNueva(**dict, target=res)
    if guardar:
        print(fila.model_dump())
        db.crear_fila(fila.model_dump())
    return {"msg": "Fila clasificada exitosamente", "row": fila.model_dump()}