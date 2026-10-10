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
    print("4. Search & Analytics")
    print("5. Exit\n")

def select_func(min: int, max: int):
    while True:
        try:
            select = int(input("Select: "))
            if select < min or select > max:
                print("Please select a valid option. ")
                continue
        except ValueError:
            print("Please select a valid option. ")
            continue
        return select



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
    
def search_n_analytics_menu():
    print("\n------Search & Analytics------\n")
    print("1. Browse by month")
    print("2. Browse by weekday")
    print("3. Earnings summary")
    print("4. Back\n")


def search_n_analytics(work_days: list[WorkDay]):

    while True:
        search_n_analytics_menu()
        select = select_func(1, 4)
        
        match select:
            case 1:
                sort_months(work_days)
            case 2:
                sort_days(work_days)
            case 3:
                earning_sums(work_days)
            case 4:
                return

def earning_sums(work_days: list[WorkDay]):
    while True:
        try:
            year = int(input("Year: "))
            if year > 9999 or year < 999:
                print("Invalid year. (Ex. 2026, 2016)")
                continue
        except ValueError:
            print("Year must be an int. (Ex. 2026, 2016)")
            continue
        break

    while True:
        print("\n----Select month----\n")
        print(" 1. January")
        print(" 2. February")
        print(" 3. March")
        print(" 4. April")
        print(" 5. May")
        print(" 6. June")
        print(" 7. July")
        print(" 8. August")
        print(" 9. September")
        print("10. October")
        print("11. November")
        print("12. December")

        month = select_func(1, 12)
        break

    
    temp_list = []
    total_workday = 0
    total_classes = 0

    for work_day in work_days:
        y, m, d = work_day.date.split("-")
        if int(y) == year:
            if int(m) == month:
                temp_list.append(work_day)
                total_workday += 1
                total_classes += work_day.classes

    if not temp_list:
        print("No work day found. ")
        return
    
    highest_day = max(temp_list, key=lambda work_day: work_day.classes * 25)
    month_name = datetime.strptime(str(month), "%m").strftime("%B")

    print("\n----Earning Summary----")
    print(f"     {month_name} {year}\n")
    print(f"Total work day: {total_workday}")
    print(f"Total classes: {total_classes}")
    print(f"Total earnings: {calculate_pay(total_classes, 25)}")
    print(f"Average earnings/day: RM{calculate_pay(total_classes, 25)/ total_workday:.2f}")
    print(f"Average classes/day: {total_classes/total_workday:.2f}")
    print(f"Higehst earning day: {highest_day.date} RM{(calculate_pay(highest_day.classes, 25))}")

    


def days_menu():
    print("\n----Browse by day----\n")
    print("1. Monday")
    print("2. Tuesday")
    print("3. Wednesday")
    print("4. Thursday")
    print("5. Friday")
    print("6. Saturday")
    print("7. Sunday")
    print("0. Back\n")

def sort_days(work_days: list[WorkDay]):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    while True:
        days_menu()
        select = select_func(0, 7)

        if select == 0:
            return
        else:
            filter_days(days[select-1], work_days)

        
def filter_days(day: str, work_days: list[WorkDay]):
    temp_list = []
    temp_classes = 0
    total_workday = 0

    for work_day in work_days:
        if day == work_day.day:
            temp_list.append(work_day)
            temp_classes += work_day.classes
            total_workday += 1
        else:
            continue

    if not temp_list:
        print("No work day found for this day. ")
        return
    
    for work_day in temp_list:
        print(f"{work_day.date} ({work_day.day}): {work_day.classes} classes")
        print(f"    {work_day.description}")    

    print("\n---Weekday Summary---\n")
    print(f"Total work days: {total_workday}")
    print(f"Total classes: {temp_classes}")
    print(f"Total earning: RM{calculate_pay(temp_classes, 25)}")
    print(f"Average per work day: RM{(calculate_pay(temp_classes, 25) / total_workday):.2f}")


def month_menu():
    print("\n----Browse by months----\n")
    print(" 1. January")
    print(" 2. February")
    print(" 3. March")
    print(" 4. April")
    print(" 5. May")
    print(" 6. June")
    print(" 7. July")
    print(" 8. August")
    print(" 9. September")
    print("10. October")
    print("11. November")
    print("12. December")
    print(" 0. Back\n")


def sort_months(work_days: list[WorkDay]):
    while True:
        month_menu()
        select = select_func(0, 12)

        if select == 0:
            return
        else:
            filter_month(select, work_days)

def filter_month(month: int, work_days: list[WorkDay]):
    temp_list = []
    temp_classes = 0
    total_workday = 0

    for work_day in work_days:
        compare_month = work_day.date.split("-")

        if int(compare_month[1]) == month:
            temp_list.append(work_day)
        else:
            continue

    if not temp_list:
        print("No work days found for this month")
        return
    
    for work_day in temp_list:
        print(f"{work_day.date} ({work_day.day}): {work_day.classes} classes")
        print(f"    {work_day.description}")    
        temp_classes += work_day.classes
        total_workday += 1
    
    print("\n---Monthly Summary---\n")
    print(f"Total work days: {total_workday}")
    print(f"Total classes: {temp_classes}")
    print(f"Total earning: RM{calculate_pay(temp_classes, 25)}")
    print(f"Average per work day: RM{calculate_pay(temp_classes, 25) / total_workday:.2f}")


    


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
        select = select_func(1, 5)

        match select:
            case 1:
                add_work_day(work_days)
            case 2:
                view_earnings(work_days)
            case 3:
                work_day_management(work_days)
            case 4:
                search_n_analytics(work_days)
            case 5:
                save_file(work_days)
                sys.exit("Thanks for using! ")
                

if __name__ == "__main__":
    main()