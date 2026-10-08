import sys
import json
from datetime import datetime

class WorkDay:
    def __init__(self, date, classes, description=None):
        self.date = date
        self.classes = classes
        self.description = description

    @property
    def classes(self):
        return self._classes

    @classes.setter
    def classes(self, value):
        if value < 1:
            raise ValueError("Classes cannot be < 1. ")
        
        self._classes = value

    @property
    def day(self):
        return datetime.strptime(self.date, "%Y-%m-%d").strftime("%A")

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date format is wrong YYYY-MM-DD.")

        self._date = value


def print_menu():
    print("\n================")
    print(" Salary Tracker")
    print("================\n")
    print("1. Add Work Day")
    print("2. View earnings")
    print("3. Exit\n")


def add_work_day(work_days: list[WorkDay]):
    while True:
        date = input("\nDate: ")
        try:
            date = convert_date(date)
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format DD-MM. ")
            continue
        break

    while True:
        try:
            classes = int(input("Classes: "))
            if classes < 1:
                print("Classes cant be < 1. ")
                continue
        except ValueError:
            print("Classes cant be a str")
            continue
        break

    description = input("Description: ")
    work_day = WorkDay(date, classes, description)

    work_days.append(work_day)


def convert_date(short_date: str):
    today = datetime.today()
    day, month = short_date.split("-")

    return f"{today.year}-{month}-{day}"


def calculate_pay(total_classes: int, rate: float):
    return total_classes * rate


def view_earnings(work_days: list[WorkDay]):
    total_classes_all = 0

    print("\n------Earning Viewer------\n")
    for work_day in work_days:
        print(f"{work_day.date} ({work_day.day}): {work_day.classes} classes - RM{calculate_pay(work_day.classes, 25)}")
        print(f"    {work_day.description}\n")
        total_classes_all += work_day.classes

    print(f"\nTotal classes: {total_classes_all}")
    print(f"Total earnings: RM{calculate_pay(total_classes_all, 25)}")


def work_day_to_dict(work_day: WorkDay):
    dictionary = {}
    dictionary["date"] = work_day.date
    dictionary["classes"] = work_day.classes
    dictionary["description"] = work_day.description

    return dictionary


def save_file(work_days: list[WorkDay]):

    work_days_data = []
    for work_day in work_days:
        work_days_data.append(work_day_to_dict(work_day))
    
    with open("salary.json", "w") as file:
        json.dump(work_days_data, file)

def load_file():
    try:
        with open("salary.json", "r") as file:
            data = json.load(file)
            work_days_data = []
            for work_day_data in data:
                work_day = WorkDay(work_day_data["date"], work_day_data["classes"], work_day_data["description"])
                work_days_data.append(work_day)
            
            return work_days_data
            
    except FileNotFoundError:
        return []


def main():
    work_days = load_file()

    while True:
        print_menu()
        try:
            select = int(input("Select: "))
            if select < 1 or select > 3:
                continue
        except ValueError:
            continue

        match select:
            case 1:
                add_work_day(work_days)
            case 2:
                view_earnings(work_days)
            case 3:
                save_file(work_days)
                sys.exit("Thanks for using! ")
                

if __name__ == "__main__":
    main()