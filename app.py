from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import date
import pytz

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
 
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Inicializar Flask-Migrate

BASE_URL = '/api/v1'
 
mexico_tz = pytz.timezone('America/Mexico_City')
# -----------------------------------------------------------------------
# MODELOS
class WallData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    propeller1 = db.Column(db.Float, nullable=False)
    propeller2 = db.Column(db.Float, nullable=False)
    propeller3 = db.Column(db.Float, nullable=False)
    propeller4 = db.Column(db.Float, nullable=False)
    propeller5 = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.Date, default=lambda: datetime.now(mexico_tz).date())
    hour = db.Column(db.String(2), default=lambda: datetime.now(mexico_tz).strftime('%H'))  # Use Mexico City time
    def __init__(self, propeller1, propeller2, propeller3, propeller4, propeller5):    
        self.propeller1 = propeller1
        self.propeller2 = propeller2
        self.propeller3 = propeller3
        self.propeller4 = propeller4
        self.propeller5 = propeller5

    def to_json(self):
        return {
            'id': self.id,  # Siempre es buena idea incluir el id también
            'propeller1': self.propeller1,
            'propeller2': self.propeller2,
            'propeller3': self.propeller3,
            'propeller4': self.propeller4,
            'propeller5': self.propeller5,
            'created_at': self.created_at.strftime('%Y-%m-%d'),  # Incluir created_at
            'hour': self.hour  # Incluir la hora
            
        }

    def __repr__(self):
        return '<WallData %r>' % self.propeller1

 # -----------------------------------------------------------------------
class DayTotal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grupo1 = db.Column(db.Float, default=0)  # Sumatoria de propeller1 y propeller2
    grupo2 = db.Column(db.Float, default=0)  # Sumatoria de propeller3
    grupo3 = db.Column(db.Float, default=0)  # Sumatoria de propeller4 y propeller5
    total = db.Column(db.Float, default=0)  # Sumatoria de todos los propellers
    entries = db.Column(db.Integer, default=0)  # Número de registros en el día
    created_at = db.Column(db.Date, default=lambda: datetime.now(mexico_tz).date())  # Use Mexico City time

    def to_json(self):
        return {
            'id': self.id,
            'grupo1': self.grupo1,
            'grupo2': self.grupo2,
            'grupo3': self.grupo3,
            'total': self.grupo1 + self.grupo2 + self.grupo3,
            'entries': self.entries,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }
# -----------------------------------------------------------------------
class MonthTotal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float, default=0)  # Sumatoria de todos los propellers
    entries = db.Column(db.Integer, default=0)  # Número de registros en el mes
    month = db.Column(db.String(2), default=lambda: datetime.now(mexico_tz).strftime('%m'))  # Use Mexico City time

    def to_json(self):
        return {
            'id': self.id,
            'total': self.total,
            'entries': self.entries,
            'month': self.month
        }

# --- MAIN --------------------------------------------------------------------
@app.route('/')
def index():
    return "Welcome to my ORM app toDoList!"
 
# ---POST----------------------------------------------------------------
@app.route(BASE_URL + '/new', methods=['POST'])
def create():


    date = datetime.now(mexico_tz)
    today = date.strftime("%Y-%m-%d")

    month = date.strftime("%m")
    #today = date(2024, 9, 19)

    # ---WallData----------------------------------------------------------------
    if not request.json or 'propeller1' not in request.json:
        abort(400)
    
    # Crear el nuevo objeto WallData
    data = WallData(
        propeller1=request.json['propeller1'], 
        propeller2=request.json['propeller2'], 
        propeller3=request.json['propeller3'], 
        propeller4=request.json['propeller4'], 
        propeller5=request.json['propeller5']
    )
    
    # Añadir a la sesión y guardar en la base de datos
    db.session.add(data)
    db.session.commit()
    
    # Calcular las sumatorias de los grupos
    grupo1_sum = request.json['propeller1'] + request.json['propeller2']
    grupo2_sum = request.json['propeller3']
    grupo3_sum = request.json['propeller4'] + request.json['propeller5']
    total_sum = grupo1_sum + grupo2_sum + grupo3_sum
    
    # ---DayTotal----------------------------------------------------------------

    # Actualizar el total en DayTotal (suponiendo que solo tienes un registro en DayTotal)
    day_total = DayTotal.query.order_by(DayTotal.id.desc()).first()

    print(day_total.created_at)
    print(today)
    print(str(day_total.created_at) == str(today))

    if not day_total:
        # Si no existe un registro de DayTotal, lo creamos
        day_total = DayTotal(grupo1=grupo1_sum, grupo2=grupo2_sum, grupo3=grupo3_sum, total=total_sum, entries=1, created_at=today)
        db.session.add(day_total)
        print("Caso 1")
    
    elif str(day_total.created_at) == str(today):
        # Si ya existe, lo actualizamos sumando los valores a cada grupo
        day_total.grupo1 += grupo1_sum
        day_total.grupo2 += grupo2_sum
        day_total.grupo3 += grupo3_sum
        day_total.total += total_sum
        day_total.entries += 1
        print("Caso 2")

    else:
        # Si el registro de DayTotal no es de hoy, lo creamos
        day_total = DayTotal(grupo1=grupo1_sum, grupo2=grupo2_sum, grupo3=grupo3_sum, total=total_sum, entries=1, created_at=today)
        db.session.add(day_total)
        print("Caso 3")
    
    # Guardar los cambios en DayTotal
    db.session.commit()

    # ---MonthTotal---------------------------------------------------------------
    # Proceso de MonthTotal
    month_total = MonthTotal.query.filter_by(month=month).first()
    if not month_total:
        # Si no existe un registro de MonthTotal, lo creamos
        month_total = MonthTotal(total=total_sum, entries=1, month=month)
        db.session.add(month_total)
    else:
        # Si ya existe, lo actualizamos sumando los valores a total
        month_total.total += total_sum
        month_total.entries += 1

    # Guardar los cambios en MonthTotal
    db.session.commit()

    # Devolver la respuesta con los datos de WallData
    return jsonify(data.to_json()), 201

 # ---GET----------------------------------------------------------------

@app.route(BASE_URL + '/readAll', methods=['GET'])
def read():
    tasks = WallData.query.all()
    #print(tasks)
   
    return jsonify([task.to_json() for task in tasks])

@app.route(BASE_URL + '/readLatest', methods=['GET'])
def readLatest():
    data = WallData.query.order_by(WallData.id.desc()).first()
    #print(tasks)
   
    return jsonify(data.to_json())

@app.route(BASE_URL + '/readCurrentDay', methods=['GET'])
def readDay():
    tasks = WallData.query.filter_by(created_at=datetime.now(mexico_tz).date()).all()

    hours_and_total = {}
    totalData = len(tasks)

    for task in tasks:
        hour = task.hour
        total = task.propeller1 + task.propeller2 + task.propeller3 + task.propeller4 + task.propeller5
        total = round((total / totalData) * 50, 2)
        if hour in hours_and_total:
            hours_and_total[hour] += total
        else:
            hours_and_total[hour] = total

    return jsonify(hours_and_total)

@app.route(BASE_URL + '/readDayTotal', methods=['GET'])
def readDayTotal():
    tasks = DayTotal.query.all()

    return jsonify([task.to_json() for task in tasks])

@app.route(BASE_URL + '/readLatestDayTotal', methods=['GET'])
def readLatestDayTotal():
    data = DayTotal.query.order_by(DayTotal.id.desc()).first()
    try:
        return jsonify(data.to_json())
    except:
        return jsonify({'status': "False", 'message': "There is no data"}), 404
    

@app.route(BASE_URL + '/readMonthTotal', methods=['GET'])
def readMonthTotal():
    tasks = MonthTotal.query.all()

    return jsonify([task.to_json() for task in tasks])

# ---DELETE----------------------------------------------------------------

@app.route(BASE_URL + '/reset', methods=['DELETE'])
def reset():
    try:
        # Eliminar todos los registros de WallData
        WallData.query.delete()
        
        # Eliminar todos los registros de DayTotal
        DayTotal.query.delete()
        
        # Eliminar todos los registros de MonthTotal
        MonthTotal.query.delete()

        # Confirmar los cambios
        db.session.commit()
        
        return jsonify({'status': "True", 'message': "All data has been reset"}), 200
    except Exception as e:
        db.session.rollback()  # Hacer rollback en caso de error
        return jsonify({'status': "False", 'message': str(e)}), 50


@app.route(BASE_URL + '/deleteDayTotalID', methods=['DELETE'])
def deleteDayTotalID():
    try:
        # Eliminar un registro de DayTotal por su ID
        DayTotal.query.filter_by(id=request.json['id']).delete()

        # Confirmar los cambios
        db.session.commit()
        return jsonify({'status': "True", 'message': "DayTotal has been deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': "False", 'message': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Tables created")
    app.run(debug=False)