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
    print("3. Manage Work Days")
    print("4. Exit\n")


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

def work_day_management_menu():
    print("\n------Work Day Management------\n")
    print("1. View all work days")
    print("2. Edit a work day")
    print("3. Delete a work day")
    print("4. Back\n")


def work_day_management(work_days: list[WorkDay]):
    while True:
        work_day_management_menu()

        try:
            select = int(input("Select: "))
            if select < 1 or select > 4:
                print("Please select a valid option. ")
                continue
        except ValueError:
            continue

        match select:
            case 1:
                view_all_work_days(work_days)
            case 2:
                edit_work_day(find_work_day(work_days))
            case 3:
                delete_work_day(work_days)
            case 4:
                return


def view_all_work_days(work_days: list[WorkDay]):
    print("\n------Work Day Management------\n")

    for work_day in work_days:
        print(f"{work_day.date} ({work_day.day}): {work_day.classes}")

def find_work_day(work_days: list[WorkDay]):
    print("\n------Find Work Day------\n")

    while True:
        date = input("Date: ")
        try:
            date = convert_date(date)
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format DD-MM")
            continue
        break

    for work_day in work_days:
        if date == work_day.date:
            print("\nFound: ")
            print(f"{work_day.date} ({work_day.day})")
            print(f"Classes: {work_day.classes} ")
            print(f"Description: {work_day.description}\n")
            return work_day
    return None

def edit_day_menu(work_day: WorkDay):
    print("What would you like to edit? \n")
    print("1. Classes")
    print("2. Description")
    print("3. Date")
    print("4. Cancel\n")


def edit_work_day(work_day: WorkDay):
    if work_day is None:
        print("\nno date found! ")
        return

    while True:
        edit_day_menu(work_day)

        try:
            select = int(input("Select: "))
            if select < 1 or select > 4:
                continue
        except ValueError:
            print("Please select a valid option. ")
            continue
        
        match select:
            case 1:
                while True:
                    try:
                        work_day.classes = int(input("New number of classes: "))
                    except ValueError:
                        print("Invalid number of classes. ")
                        continue
                    break
            case 2:
                work_day.description = input("New description: ")
            case 3:
                while True:
                    try:
                        date = input("Date: ")
                        date = convert_date(date)
                        work_day.date = date
                    except ValueError:
                        print("Invalid date formate DD-MM")
                        continue
                    break
            case 4:
                return

def delete_work_day(work_days: list[WorkDay]):
    removing_date = find_work_day(work_days)

    if removing_date is None:
        print("no date found! ")
        return

    while True:
        confirmation = input("Are you sure you want to delete this work day? (y/n)\n").lower()
        if confirmation == "y":
            work_days.remove(removing_date)
            return
        if confirmation == "n":
            return
        else:
            print("y - yes.\nn - no. ")
            continue
    



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
            
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return []



def main():
    work_days = load_file()

    while True:
        print_menu()
        try:
            select = int(input("Select: "))
            if select < 1 or select > 4:
                print("Please select a valid option. ")
                continue
        except ValueError:
            continue

        match select:
            case 1:
                add_work_day(work_days)
            case 2:
                view_earnings(work_days)
            case 3:
                work_day_management(work_days)
            case 4:
                save_file(work_days)
                sys.exit("Thanks for using! ")
                

if __name__ == "__main__":
    main()