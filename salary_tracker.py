import sys
import csv
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
        date_obj = datetime.strptime(self.date, "%Y-%m-%d")
        day_name = date_obj.strftime("%A")

        return day_name

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        try:
            date_obj = datetime.strptime(value, "%Y-%m-%d")
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

def add_work_day(work_days):
    while True:
        date = input("\nDate: ")

        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            continue
        break
    while True:
        try:
            classes = int(input("Classes: "))
        except ValueError:
            continue
        break

    description = input("Description: ")
    work_day = WorkDay(date, classes, description)

    work_days.append(work_day)




def calculate_pay(total_classes, rate):
    return total_classes * rate

def view_earnings(days):
    total_classes_all = 0

    print("\n------Earning Viewer------\n")
    for day in days:
        total_classes_day = sum(days[day])
        print(f"{day}: {total_classes_day} classes - RM{calculate_pay(total_classes_day, 25)}")
        total_classes_all += total_classes_day
    
    print(f"\nTotal classes: {total_classes_all}")
    print(f"Total earnings: RM{calculate_pay(total_classes_all, 25)}")

def save_file(days):
    with open("salary.json", "w") as file:
        json_string = json.dumps(days)
        file.write(json_string)

def load_file():
    try:
        with open("salary.json", "r") as file:
            days = json.load(file)

            return days
  
    except FileNotFoundError:
        return {}

def main():
    days = load_file()
    work_days = []

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
                view_earnings(days)
            case 3:
                save_file(days)
                sys.exit("Thanks for using! ")
                

if __name__ == "__main__":
    main()