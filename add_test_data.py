from app import db, Machine, MachineData
from datetime import datetime

# Create test machines
machines = [
    {
        'name': 'Экскаватор-погрузчик JCB 540-170',
        'type': 'Экскаватор-погрузчик',
        'manufacturer': 'JCB',
        'year': 2023
    },
    {
        'name': 'Бульдозер Caterpillar D6',
        'type': 'Бульдозер',
        'manufacturer': 'Caterpillar',
        'year': 2022
    }
]

# Create test machine data
machine_data = [
    {
        'machine_id': 1,
        'parameter': 'Максимальная высота подъема',
        'value': 6.1,
        'unit': 'м'
    },
    {
        'machine_id': 1,
        'parameter': 'Максимальная глубина копания',
        'value': 4.5,
        'unit': 'м'
    },
    {
        'machine_id': 2,
        'parameter': 'Мощность двигателя',
        'value': 220,
        'unit': 'л.с.'
    },
    {
        'machine_id': 2,
        'parameter': 'Масса',
        'value': 15500,
        'unit': 'кг'
    }
]

with app.app_context():
    # Add machines
    for machine in machines:
        new_machine = Machine(**machine)
        db.session.add(new_machine)
    
    # Add machine data
    for data in machine_data:
        new_data = MachineData(**data)
        db.session.add(new_data)
    
    db.session.commit()
    print("Test data added successfully!")
