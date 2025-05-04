from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    fuel_consumption = db.Column(db.Float, nullable=False)
    idle_consumption = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Vehicle {self.name}>'

    calculations = db.relationship('Calculation', backref='vehicle', lazy=True)

class Calculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    idle_hours = db.Column(db.Float, nullable=False)
    expression = db.Column(db.String(200), nullable=False)
    result = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify([
        {
            'id': v.id,
            'name': v.name,
            'fuel_consumption': v.fuel_consumption,
            'idle_consumption': v.idle_consumption
        }
        for v in vehicles
    ])

@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    data = request.json
    vehicle = Vehicle(
        name=data['name'],
        fuel_consumption=float(data['fuel_consumption']),
        idle_consumption=float(data['idle_consumption'])
    )
    db.session.add(vehicle)
    db.session.commit()
    return jsonify({
        'id': vehicle.id,
        'name': vehicle.name,
        'fuel_consumption': vehicle.fuel_consumption,
        'idle_consumption': vehicle.idle_consumption
    })

@app.route('/api/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        data = request.json
        
        vehicle.name = data['name']
        vehicle.fuel_consumption = float(data['fuel_consumption'])
        vehicle.idle_consumption = float(data['idle_consumption'])
        
        db.session.commit()
        return jsonify({
            'id': vehicle.id,
            'name': vehicle.name,
            'fuel_consumption': vehicle.fuel_consumption,
            'idle_consumption': vehicle.idle_consumption
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_vehicle: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        vehicle_id = data.get('vehicle_id')
        distance = float(data.get('distance', 0))
        idle_hours = float(data.get('idle_hours', 0))
        
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        result = (distance * vehicle.fuel_consumption / 100) + (idle_hours * vehicle.idle_consumption)
        
        calculation = Calculation(
            vehicle_id=vehicle_id,
            distance=distance,
            idle_hours=idle_hours,
            expression=f"{distance} * {vehicle.fuel_consumption} / 100 + {idle_hours} * {vehicle.idle_consumption}",
            result=result
        )

        # Обновляем данные автомобиля
        vehicle.distance = distance
        vehicle.idle_hours = idle_hours

        db.session.add(calculation)
        db.session.commit()

        return jsonify({
            'distance': distance,
            'fuel_consumption': vehicle.fuel_consumption,
            'idle_hours': idle_hours,
            'idle_consumption': vehicle.idle_consumption,
            'distance_consumption': distance * vehicle.fuel_consumption / 100,
            'engine_consumption': idle_hours * vehicle.idle_consumption,
            'total_consumption': result,
            'expression': calculation.expression
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/vehicle-calculations/<int:vehicle_id>', methods=['GET'])
def get_vehicle_calculations(vehicle_id):
    try:
        calculations = Calculation.query.filter_by(vehicle_id=vehicle_id).all()
        return jsonify([
            {
                'id': calc.id,
                'distance': calc.distance,
                'idle_hours': calc.idle_hours,
                'expression': calc.expression,
                'result': calc.result,
                'timestamp': calc.created_at.isoformat()
            }
            for calc in calculations
        ])
    except Exception as e:
        return jsonify({'error': str(e)}), 400
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/vehicles/<int:vehicle_id>', methods=['GET', 'PUT'])
def vehicle_details(vehicle_id):
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        if request.method == 'GET':
            return jsonify({
                'id': vehicle.id,
                'name': vehicle.name,
                'fuel_consumption': vehicle.fuel_consumption,
                'idle_consumption': vehicle.idle_consumption
            })
        
        if request.method == 'PUT':
            data = request.json
            vehicle.name = data.get('name', vehicle.name)
            vehicle.fuel_consumption = float(data.get('fuel_consumption', vehicle.fuel_consumption))
            vehicle.idle_consumption = float(data.get('idle_consumption', vehicle.idle_consumption))
            
            db.session.commit()
            return jsonify({'message': 'Автомобиль успешно обновлен'})
        
        return jsonify({'error': 'Method not allowed'}), 405
    except Exception as e:
        print(f"Error in vehicle_details: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        # Удаляем все расчеты для этого автомобиля
        Calculation.query.filter_by(vehicle_id=vehicle_id).delete()
        
        # Удаляем сам автомобиль
        db.session.delete(vehicle)
        db.session.commit()
        
        return jsonify({'message': 'Автомобиль успешно удален'})
    except Exception as e:
        print(f"Error in delete_vehicle: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        calculations = Calculation.query.join(Vehicle).order_by(Calculation.created_at.desc()).all()
        return jsonify([
            {
                'id': calc.id,
                'vehicle': calc.vehicle.name,
                'distance': calc.distance,
                'idle_hours': calc.idle_hours,
                'fuel_consumption': calc.vehicle.fuel_consumption,
                'idle_consumption': calc.vehicle.idle_consumption,
                'expression': calc.expression,
                'result': calc.result,
                'timestamp': calc.created_at.isoformat()
            }
            for calc in calculations
        ])
    except Exception as e:
        print(f"Error in get_history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    try:
        Calculation.query.delete()
        db.session.commit()
        return '', 204  # No content
    except Exception as e:
        db.session.rollback()
        print(f"Error in clear_history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/vehicle-summary', methods=['GET'])
def get_vehicle_summary():
    try:
        calculations = Calculation.query.join(Vehicle).all()
        
        # Группируем по автомобилям
        summary = {}
        for calc in calculations:
            if calc.vehicle.name not in summary:
                summary[calc.vehicle.name] = {
                    'vehicle': calc.vehicle.name,
                    'total_distance': 0,
                    'total_idle_hours': 0,
                    'total_fuel': 0,
                    'trips': 0
                }
            
            summary[calc.vehicle.name]['total_distance'] += calc.distance
            summary[calc.vehicle.name]['total_idle_hours'] += calc.idle_hours
            summary[calc.vehicle.name]['total_fuel'] += calc.result
            summary[calc.vehicle.name]['trips'] += 1
        
        # Добавляем средний расход
        for vehicle, data in summary.items():
            if data['total_distance'] > 0:
                data['average_consumption'] = (data['total_fuel'] / data['total_distance']) * 100
            else:
                data['average_consumption'] = 0
        
        return jsonify(list(summary.values()))
    except Exception as e:
        print(f"Error in get_vehicle_summary: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/db-viewer', methods=['GET'])
def db_viewer():
    try:
        # Получаем все автомобили
        vehicles = Vehicle.query.all()
        
        # Получаем все расчеты
        calculations = Calculation.query.all()
        
        return jsonify({
            'vehicles': [
                {
                    'id': v.id,
                    'name': v.name,
                    'fuel_consumption': v.fuel_consumption,
                    'idle_consumption': v.idle_consumption,
                    'created_at': v.created_at.isoformat()
                }
                for v in vehicles
            ],
            'calculations': [
                {
                    'id': c.id,
                    'vehicle_id': c.vehicle_id,
                    'distance': c.distance,
                    'idle_hours': c.idle_hours,
                    'expression': c.expression,
                    'result': c.result,
                    'created_at': c.created_at.isoformat()
                }
                for c in calculations
            ]
        })
    except Exception as e:
        print(f"Error in db_viewer: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

    
    app.run(debug=True, host='0.0.0.0')
