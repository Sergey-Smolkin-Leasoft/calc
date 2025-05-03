from app import Session, Machine, MachineData
from datetime import datetime

# Создаем базовые автомобили
def add_base_vehicles():
    base_vehicles = [
        {
            'name': 'КАМАЗ',
            'fuel_consumption': 40,
            'idle_consumption': 2
        },
        {
            'name': 'ГАЗель',
            'fuel_consumption': 12,
            'idle_consumption': 1
        },
        {
            'name': 'Volvo FH',
            'fuel_consumption': 30,
            'idle_consumption': 1.5
        },
        {
            'name': 'Другой автомобиль',
            'fuel_consumption': 8,
            'idle_consumption': 1.5
        }
    ]

    with Session() as session:
        for vehicle in base_vehicles:
            new_vehicle = Machine(
                name=vehicle['name'],
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
                value=vehicle['fuel_consumption'],
                unit='л/100км',
                timestamp=datetime.now()
            ))
            
            # Добавляем данные о расходе на холостом ходу
            session.add(MachineData(
                machine_id=new_vehicle.id,
                parameter='idle_consumption',
                value=vehicle['idle_consumption'],
                unit='л/ч',
                timestamp=datetime.now()
            ))
        
        session.commit()
        print("Базовые автомобили добавлены успешно!")

if __name__ == '__main__':
    add_base_vehicles()
