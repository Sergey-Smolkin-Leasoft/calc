from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

app = Flask(__name__)
CORS(app)

# Create engine and session
engine = create_engine(
    'sqlite:///calc.db',
    echo=True,
    connect_args={'check_same_thread': False}
)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Machine(Base):
    __tablename__ = 'machine'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    manufacturer = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    data = relationship('MachineData', backref='machine', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'manufacturer': self.manufacturer,
            'year': self.year
        }

class MachineData(Base):
    __tablename__ = 'machine_data'
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey('machine.id'), nullable=False)
    parameter = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    timestamp = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'machine_id': self.machine_id,
            'parameter': self.parameter,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat()
        }

# Create tables
Base.metadata.create_all(engine)

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    with Session() as session:
        vehicles = session.query(Machine).filter_by(type='автомобиль').all()
        return jsonify([{
            'id': v.id,
            'name': v.name,
            'fuel_consumption': v.data[0].value if v.data else 0,
            'idle_consumption': v.data[1].value if len(v.data) > 1 else 0
        } for v in vehicles])

@app.route('/api/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    with Session() as session:
        vehicle = session.query(Machine).filter_by(id=vehicle_id).first()
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        return jsonify({
            'id': vehicle.id,
            'name': vehicle.name,
            'fuel_consumption': vehicle.data[0].value if vehicle.data else 0,
            'idle_consumption': vehicle.data[1].value if len(vehicle.data) > 1 else 0
        })

@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    data = request.json
    with Session() as session:
        new_vehicle = Machine(
            name=data['name'],
            type='автомобиль',
            manufacturer='-',
            year=2023
        )
        session.add(new_vehicle)
        session.flush()  # Получаем ID новой машины
        
        # Добавляем данные о расходе топлива
        session.add(MachineData(
            machine_id=new_vehicle.id,
            parameter='fuel_consumption',
            value=data['fuel_consumption'],
            unit='л/100км',
            timestamp=datetime.datetime.now()
        ))
        
        # Добавляем данные о расходе на холостом ходу
        session.add(MachineData(
            machine_id=new_vehicle.id,
            parameter='idle_consumption',
            value=data['idle_consumption'],
            unit='л/ч',
            timestamp=datetime.datetime.now()
        ))
        
        session.commit()
        return jsonify({
            'id': new_vehicle.id,
            'name': new_vehicle.name,
            'fuel_consumption': data['fuel_consumption'],
            'idle_consumption': data['idle_consumption']
        }), 201

@app.route('/api/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    data = request.json
    with Session() as session:
        vehicle = session.query(Machine).filter_by(id=vehicle_id).first()
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        vehicle.name = data['name']
        
        # Обновляем данные о расходе топлива
        fuel_data = next((d for d in vehicle.data if d.parameter == 'fuel_consumption'), None)
        if fuel_data:
            fuel_data.value = data['fuel_consumption']
        else:
            session.add(MachineData(
                machine_id=vehicle_id,
                parameter='fuel_consumption',
                value=data['fuel_consumption'],
                unit='л/100км',
                timestamp=datetime.datetime.now()
            ))
        
        # Обновляем данные о расходе на холостом ходу
        idle_data = next((d for d in vehicle.data if d.parameter == 'idle_consumption'), None)
        if idle_data:
            idle_data.value = data['idle_consumption']
        else:
            session.add(MachineData(
                machine_id=vehicle_id,
                parameter='idle_consumption',
                value=data['idle_consumption'],
                unit='л/ч',
                timestamp=datetime.datetime.now()
            ))
        
        session.commit()
        return jsonify({
            'id': vehicle_id,
            'name': vehicle.name,
            'fuel_consumption': data['fuel_consumption'],
            'idle_consumption': data['idle_consumption']
        })

@app.route('/api/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    with Session() as session:
        vehicle = session.query(Machine).filter_by(id=vehicle_id).first()
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        # Удаляем все связанные данные
        session.query(MachineData).filter_by(machine_id=vehicle_id).delete()
        session.delete(vehicle)
        session.commit()
        return '', 204

if __name__ == '__main__':
    app.run(debug=True)
