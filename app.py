#   Alfredo Barranco Ahued
#   5 de octubre de 2024
#   ORM para la base de datos de la Pared Eólica para ASE II
#   Versión 2.1

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import date, timedelta
import pytz
from sqlalchemy import cast, Date, func

# Cargar variables de entorno
load_dotenv()

# Crear aplicación Flask
app = Flask(__name__)

# Configurar SQLAlchemy con la URL de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Crear instancia de SQLAlchemy
db = SQLAlchemy(app)

BASE_URL = "/api/v1"

mexico_tz = pytz.timezone('America/Mexico_City')

migrate = Migrate(app, db)


# -----------------------------------------------------------------------
# MODELOS: CREACIÓN DE TABLAS
# -----------------------------------------------------------------------

class TempWallData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False)
    group = db.Column(db.Integer, nullable=False)
    propeller1 = db.Column(db.Float, nullable=False)
    propeller2 = db.Column(db.Float, nullable=False)
    propeller3 = db.Column(db.Float, nullable=False)
    propeller4 = db.Column(db.Float, nullable=False)
    propeller5 = db.Column(db.Float, nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
            'group': self.group,
            'propeller1': self.propeller1,
            'propeller2': self.propeller2,
            'propeller3': self.propeller3,
            'propeller4': self.propeller4,
            'propeller5': self.propeller5,
        }

    def __repr__(self):
        return '<TempWallData %r>' % self.propeller1


class WallData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False)
    group = db.Column(db.Integer, nullable=False)
    propeller1 = db.Column(db.Float, nullable=False)
    propeller2 = db.Column(db.Float, nullable=False)
    propeller3 = db.Column(db.Float, nullable=False)
    propeller4 = db.Column(db.Float, nullable=False)
    propeller5 = db.Column(db.Float, nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
            'group': self.group,
            'propeller1': self.propeller1,
            'propeller2': self.propeller2,
            'propeller3': self.propeller3,
            'propeller4': self.propeller4,
            'propeller5': self.propeller5,
        }

    def __repr__(self):
        return '<WallData %r>' % self.propeller1

class TotalDay(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    total = db.Column(db.Float, nullable=False)
    group1 = db.Column(db.Float, nullable=False)
    group2 = db.Column(db.Float, nullable=False)
    group3 = db.Column(db.Float, nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'total': self.total,
            'group1': self.group1,
            'group2': self.group2,
            'group3': self.group3
        }

    def __repr__(self):
        return '<TotalDay %r>' % self.total

class TotalMonth(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    total = db.Column(db.Float, nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m'),
            'total': self.total
        }

    def __repr__(self):
        return '<TotalMonth %r>' % self.total

class TotalAll(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    total = db.Column(db.Float, nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'total': self.total
        }

    def __repr__(self):
        return '<TotalAll %r>' % self.total


# -----------------------------------------------------------------------
# INICIO DE | FUNCIONES
# -----------------------------------------------------------------------
def update_total_day(today, total_sum, sum_group1, sum_group2, sum_group3):
    today_object = TotalDay.query.filter_by(date=today).first()

    if today_object is None:
        new_total_day = TotalDay(date=today, total=total_sum, group1=sum_group1, group2=sum_group2, group3=sum_group3)
        db.session.add(new_total_day)
        db.session.commit()
    else:
        today_object.total += total_sum
        today_object.group1 += sum_group1
        today_object.group2 += sum_group2
        today_object.group3 += sum_group3
        db.session.commit()


def update_total_month(month, total_sum):
    if isinstance(month, str):
        month = datetime.strptime(month, '%Y-%m')  # ✅ Convertir string a `datetime`
    
    # ✅ Convertir `date` a `datetime` para agregar zona horaria correctamente
    month = datetime.combine(month, datetime.min.time())  
    month = mexico_tz.localize(month)  # ✅ Ahora `month` es `datetime` con zona horaria
    
    # Usar el primer día del mes para la consulta
    month_start = month.date()  # ✅ Extraer solo la fecha

    month_object = TotalMonth.query.filter_by(date=month_start).first()

    if month_object is None:
        new_total_month = TotalMonth(date=month_start, total=total_sum)
        db.session.add(new_total_month)
        db.session.commit()
    else:
        month_object.total += total_sum
        db.session.commit()


def update_total_all(total_sum):
    total_object = TotalAll.query.first()

    if total_object is None:
        new_total_all = TotalAll(total=total_sum)
        db.session.add(new_total_all)
        db.session.commit()
    else:
        total_object.total += total_sum
        db.session.commit()

# --- MAIN -------------------------------------------------------------

@app.route('/')
def home():
    return "Welcome to my ORM app!"

# ---POST---------------------------------------------------------------

@app.route(BASE_URL + '/new', methods=['POST'])
@app.route(BASE_URL + '/new', methods=['POST'])
def create():
    # Obtener la fecha actual en zona horaria de México
    date = datetime.now(mexico_tz)  # ✅ Dejarlo como datetime

    # Obtener datos del request
    data = request.get_json()

    if not data or 'propeller1' not in data:
        abort(400, description="Datos inválidos. Se requiere al menos 'propeller1'.")

    # Calcular la suma total de los propellers
    total_sum = sum([
        data.get('propeller1', 0),
        data.get('propeller2', 0),
        data.get('propeller3', 0),
        data.get('propeller4', 0),
        data.get('propeller5', 0)
    ])

    # Crear nuevos objetos en la base de datos
    new_wall_data = WallData(
        date=date,  # ✅ Guardar como `datetime`
        group=data['group'],
        propeller1=data['propeller1'],
        propeller2=data['propeller2'],
        propeller3=data['propeller3'],
        propeller4=data['propeller4'],
        propeller5=data['propeller5']
    )

    new_temp_wall_data = TempWallData(
        date=date,  # ✅ Guardar como `datetime`
        group=data['group'],
        propeller1=data['propeller1'],
        propeller2=data['propeller2'],
        propeller3=data['propeller3'],
        propeller4=data['propeller4'],
        propeller5=data['propeller5']
    )

    # Solo guardar si la suma total es mayor o igual a 0.2
    if total_sum >= 0.2:
        db.session.add(new_wall_data)
        db.session.add(new_temp_wall_data)

        # Calcular sumas por grupo
        sum_group1 = data['propeller1'] + data['propeller2']
        sum_group2 = data['propeller3']
        sum_group3 = data['propeller4'] + data['propeller5']

        # Formato correcto para `TotalDay`
        today = date.astimezone(mexico_tz).date()  # ✅ Extrae la fecha pero mantiene la zona horaria válida.
        month = today.replace(day=1)  # ✅ Para `TotalMonth`

        # Actualizar totales
        update_total_day(today, total_sum, sum_group1, sum_group2, sum_group3)
        update_total_month(month, total_sum)
        update_total_all(total_sum)

        db.session.commit()
        return jsonify(new_wall_data.to_json())

    return jsonify({'message': 'Data not saved. Total sum is less than 0.2'})

# ---GET----------------------------------------------------------------
@app.route(BASE_URL + '/readLatest', methods=['GET'])
def read_latest():
    latest_data = WallData.query.order_by(WallData.id.desc()).first()
    return jsonify(latest_data.to_json()) if latest_data else jsonify({'message': 'No data found'})

@app.route(BASE_URL + '/readTempLatest/<int:number>', methods=['GET'])
def read_temp_latest(number):
    latest_data = TempWallData.query.filter_by(group=number).order_by(TempWallData.id.desc()).first()
    return jsonify(latest_data.to_json()) if latest_data else jsonify({'message': 'No data found'})

@app.route(BASE_URL + '/readAll', methods=['GET'])
def read_all():
    all_data = WallData.query.all()
    return jsonify([data.to_json() for data in all_data])


@app.route(BASE_URL + '/getAllHours', methods=['GET'])
def get_all_hours():
    date_str = request.args.get('date')

    if not date_str:
        date = datetime.now(mexico_tz).date()
    else:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    all_data = WallData.query.filter(cast(WallData.date, Date) == date).all()

    hourly_totals = {hour: 0 for hour in range(24)}

    for data in all_data:
        hour = data.date.hour
        total = ((data.propeller1 ** 2 / 216 * 1000) +
                 (data.propeller2 ** 2 / 216 * 1000) +
                 (data.propeller3 ** 2 / 216 * 1000) +
                 (data.propeller4 ** 2 / 216 * 1000) +
                 (data.propeller5 ** 2 / 216 * 1000))
        hourly_totals[hour] += total

    return jsonify(hourly_totals)

@app.route(BASE_URL + '/getAllMinutes', methods=['GET'])
def get_all_minutes():
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Date parameter is required'}), 400

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}), 400

    all_data = WallData.query.filter(
        WallData.date >= date.replace(minute=0, second=0, microsecond=0),
        WallData.date < date.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    ).all()

    minute_totals = {minute: {'propeller1': 0, 'propeller2': 0, 'propeller3': 0,
                              'propeller4': 0, 'propeller5': 0, 'total': 0} for minute in range(60)}

    for data in all_data:
        minute = data.date.minute
        minute_totals[minute]['propeller1'] += data.propeller1 ** 2 / 216 * 1000
        minute_totals[minute]['propeller2'] += data.propeller2 ** 2 / 216 * 1000
        minute_totals[minute]['propeller3'] += data.propeller3 ** 2 / 216 * 1000
        minute_totals[minute]['propeller4'] += data.propeller4 ** 2 / 216 * 1000
        minute_totals[minute]['propeller5'] += data.propeller5 ** 2 / 216 * 1000
        minute_totals[minute]['total'] += sum(minute_totals[minute].values())

    return jsonify(minute_totals)

@app.route(BASE_URL + '/getHourByNumber/<int:number>', methods=['GET'])
def get_hour_by_number(number):
    today = datetime.now(mexico_tz).date()
    all_data = WallData.query.filter(cast(WallData.date, Date) == today).all()

    total = sum(data.propeller1 + data.propeller2 + data.propeller3 +
                data.propeller4 + data.propeller5 for data in all_data if data.date.hour == number)

    return jsonify({'hour': number, 'total': total})

@app.route(BASE_URL + '/get_totals', methods=['GET'])
def get_totals():
    results = (
        db.session.query(
            WallData.group,
            func.sum(
                WallData.propeller1 +
                WallData.propeller2 +
                WallData.propeller3 +
                WallData.propeller4 +
                WallData.propeller5
            ).label('total')
        )
        .group_by(WallData.group)
        .all()
    )

    totals = {f'group{row[0]}': row[1] for row in results}
    return jsonify(totals)

# GETs | TotalDay -------------------------------------------------------

@app.route(BASE_URL + '/readAllDays', methods=['GET'])
def read_all_days():
    all_data = TotalDay.query.all()
    return jsonify([data.to_json() for data in all_data])

@app.route(BASE_URL + '/getCurrentDay', methods=['GET'])
def get_current_day():
    today = datetime.now(mexico_tz).date()
    today_object = TotalDay.query.filter_by(date=today).first()
    return jsonify(today_object.to_json()) if today_object else jsonify({'total': 0})


@app.route(BASE_URL + '/read30days', methods=['GET'])
def read30days():
    today = datetime.now(mexico_tz).date()
    thirty_days_ago = today - timedelta(days=30)
    all_data = TotalDay.query.filter(TotalDay.date >= thirty_days_ago, TotalDay.date <= today).all()

    day_totals = { (thirty_days_ago + timedelta(days=i)).strftime('%d'): 0 for i in range(31) }

    for day in all_data:
        day_totals[day.date.strftime('%d')] = day.total

    return jsonify(day_totals)

@app.route(BASE_URL + '/getWeek', methods=['GET'])
def get_week():
    today = datetime.now(mexico_tz).date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    week_data = TotalDay.query.filter(TotalDay.date >= week_start, TotalDay.date <= week_end).all()

    week_totals = {day.date.strftime('%A, %Y-%m-%d'): (day.total ** 2/216 * 1000) for day in week_data}
    total_week = sum(day.total for day in week_data)

    return jsonify({'week_totals': week_totals, 'total_week': total_week})

@app.route(BASE_URL + '/getDayByNumber/<number>', methods=['GET'])
def get_day_by_number(number):

    today = datetime.now(mexico_tz).date()
    all_data = TotalDay.query.all()

    total = 0

    for data in all_data:
        if data.date.day == int(number):
            total += data.total

    return jsonify({'day': number, 'total': total})

# GETs | TotalMonth -----------------------------------------------------

@app.route(BASE_URL + '/getCurrentMonth', methods=['GET'])
def get_current_month():
    today = datetime.now(mexico_tz).date()
    month_start = today.replace(day=1)
    month_object = TotalMonth.query.filter_by(date=month_start).first()

    if month_object is None:
        return jsonify({'total': 0})
    else:
        return jsonify(month_object.to_json())
    
@app.route(BASE_URL + '/readAllMonths', methods=['GET'])
def readAllMonths():
    all_data = TotalMonth.query.all()

    #Crear un diccionario de meses del 1 al 12 que tenga el total de cada mes
    month_totals = {month: 0 for month in range(1, 13)}

    for data in all_data:
        month = data.date.month
        month_totals[month] += data.total

    return jsonify(month_totals)

@app.route(BASE_URL + '/getMonthsObjects', methods=['GET'])
def get_months_objects():
    all_data = TotalMonth.query.all()
    return jsonify([data.to_json() for data in all_data])

# GETs | TotalAll -------------------------------------------------------

@app.route(BASE_URL + '/getTotal', methods=['GET'])
def get_total():
    total_object = TotalAll.query.first()

    if total_object is None:
        return jsonify({'total': 0})
    else:
        return jsonify(total_object.to_json())

# ---DELETE-------------------------------------------------------------

@app.route(BASE_URL + '/resetAll', methods=['DELETE'])
def resetAll():
    db.session.query(WallData).delete()
    db.session.query(TotalDay).delete()
    db.session.query(TotalMonth).delete()
    db.session.query(TotalAll).delete()
    db.session.commit()
    return jsonify({'message': 'All data has been deleted'})
# -----------------------------------------------------------------------
@app.route(BASE_URL + '/resetTempWallData', methods=['DELETE'])
def resetTempWallData():
    db.session.query(TempWallData).delete()
    db.session.commit()
    return jsonify({'message': 'All data has been deleted'})
# -----------------------------------------------------------------------
@app.route(BASE_URL + '/deleteAllZeros', methods=['DELETE'])
def deleteAllZeros():
    db.session.query(WallData).filter(WallData.propeller1 == 0, WallData.propeller2 == 0, WallData.propeller3 == 0, WallData.propeller4 == 0, WallData.propeller5 == 0).delete()
    db.session.commit()
    return jsonify({'message': 'All zeros have been deleted'})


if __name__ == '__main__':
    app.run(debug=True)

# Cambios terminados v1  