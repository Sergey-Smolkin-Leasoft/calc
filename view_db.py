from app import db, Machine, MachineData

def print_machines():
    print("\nСписок машин:")
    machines = Machine.query.all()
    for machine in machines:
        print(f"\nID: {machine.id}")
        print(f"Название: {machine.name}")
        print(f"Тип: {machine.type}")
        print(f"Производитель: {machine.manufacturer}")
        print(f"Год выпуска: {machine.year}")
        
        # Показать данные машины
        print("\nДанные машины:")
        for data in machine.data:
            print(f"- {data.parameter}: {data.value} {data.unit if data.unit else ''}")

if __name__ == '__main__':
    with app.app_context():
        print_machines()
