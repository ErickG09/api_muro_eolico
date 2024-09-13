from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os
from flask_cors import CORS
from flask_migrate import Migrate

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
 
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Inicializar Flask-Migrate

BASE_URL = '/api/v1'
 
 
class WallData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Add a unique id field
    propeller1 = db.Column(db.Float, nullable=False)
    propeller2 = db.Column(db.Float, nullable=False)
    propeller3 = db.Column(db.Float, nullable=False)
    propeller4 = db.Column(db.Float, nullable=False)
    propeller5 = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
   
    def __init__(self, propeller1, propeller2, propeller3, propeller4, propeller5):    
        
        self.propeller1 = propeller1
        self.propeller2 = propeller2
        self.propeller3 = propeller3
        self.propeller4 = propeller4
        self.propeller5 = propeller5
       
    def to_json(self):
        return {
            'propeller1': self.propeller1,
            'propeller2': self.propeller2,
            'propeller3': self.propeller3,
            'propeller4': self.propeller4,
            'propeller5': self.propeller5
        }

    def __repr__(self):
        return '<Task %r>' % self.propeller1
   
 # -----------------------------------------------------------------------
class DayTotal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grupo1 = db.Column(db.Float, default=0)  # Sumatoria de propeller1 y propeller2
    grupo2 = db.Column(db.Float, default=0)  # Sumatoria de propeller3
    grupo3 = db.Column(db.Float, default=0)  # Sumatoria de propeller4 y propeller5

    def to_json(self):
        return {
            'id': self.id,
            'grupo1': self.grupo1,
            'grupo2': self.grupo2,
            'grupo3': self.grupo3
        }

# --- MAIN --------------------------------------------------------------------
@app.route('/')
def index():
    return "Welcome to my ORM app toDoList!"
 
 
@app.route(BASE_URL + '/new', methods=['POST'])
def create():
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
    
    # Actualizar el total en DayTotal (suponiendo que solo tienes un registro en DayTotal)
    day_total = DayTotal.query.first()
    
    if not day_total:
        # Si no existe un registro de DayTotal, lo creamos
        day_total = DayTotal(grupo1=grupo1_sum, grupo2=grupo2_sum, grupo3=grupo3_sum)
        db.session.add(day_total)
    else:
        # Si ya existe, lo actualizamos sumando los valores a cada grupo
        day_total.grupo1 += grupo1_sum
        day_total.grupo2 += grupo2_sum
        day_total.grupo3 += grupo3_sum
    
    # Guardar los cambios en DayTotal
    db.session.commit()
    
    # Devolver la respuesta con los datos de WallData
    return jsonify(data.to_json()), 201
 
@app.route(BASE_URL + '/readAll', methods=['GET'])
def read():
    tasks = WallData.query.all()
    #print(tasks)
   
    return jsonify([task.to_json() for task in tasks])

@app.route(BASE_URL + '/readDayTotal', methods=['GET'])
def readDayTotal():
    tasks = DayTotal.query.all()
    #print(tasks)
   
    return jsonify([task.to_json() for task in tasks])

@app.route(BASE_URL + '/readLatest', methods=['GET'])
def readLatest():
    data = WallData.query.order_by(WallData.id.desc()).first()
    #print(tasks)
   
    return jsonify(data.to_json())
   
@app.route(BASE_URL + '/update/<id>', methods=['PUT'])
def update(id):
    data = WallData.query.get(id)
    if not data:
        abort(400)
    data.status = not data.status
    db.session.commit()
       
    return jsonify(data.to_json()), 201
 
 
@app.route(BASE_URL + '/delete/<id>', methods=['DELETE'])
def delete(id):
    data = WallData.query.get_or_404(id)

    db.session.delete(data)
    db.session.commit()
   
    return jsonify({'status':"True"}), 201
 
 
 
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Tables created...")
    app.run(debug=False)