import sys
import csv
import json

def print_menu():
    print("\n================")
    print(" Salary Tracker")
    print("================\n")
    print("1. Add Work Day")
    print("2. View earnings")
    print("3. Exit\n")

def add_work_day(days):
    day = input("Day: ")

    while True:
        try:
            classes = int(input("Classes: "))
            if classes < 1:
                print("Invalid classes. \n")
                continue
        except ValueError:
            continue

        break

    if day.lower() in days:
        days[day.lower()].append(classes)
    else:
        days[day.lower()] = []
        days[day.lower()].append(classes)

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

    while True:
        print_menu()
        select = int(input("Select: "))

        match select:
            case 1:
                add_work_day(days)
            case 2:
                view_earnings(days)
            case 3:
                save_file(days)
                sys.exit("Thanks for using! ")
                

if __name__ == "__main__":
    main()