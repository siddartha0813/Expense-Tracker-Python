import os
from operator import index
import csv
import sqlite3

RED="\033[91m"
GREEN="\033[92m"
YELLOW="\033[93m"
BLUE="\033[94m"
CYAN="\033[96m"
RESET="\033[0m"
class Expense:
    def __init__(self,description,amount,category,date):
        self.description = description
        self.amount = amount
        self.category = category
        self.date = date
class ExpenseTracker:
    def __init__(self):
        self.conn = sqlite3.connect("expenses.db")
        self.cursor = self.conn.cursor()
        self.created_table()
        self.expenses = []
    def add_expense(self,expense):
            self.cursor.execute("INSERT INTO expenses(description, amount, category, date) VALUES (?, ?, ?, ?)",(expense.description, expense.amount, expense.category, expense.date))
            self.conn.commit()
    def total_expenses(self):
        total=sum(exp.amount for exp in self.expenses)
        print(CYAN+f"Total expenses:$ {total}"+RESET)
    def filter_by_category(self,category):
        print(f"Filtering expenses by category: {category}")
        for exp in self.expenses:
                    print(f"{exp.date} | {exp.description} | $ {exp.amount}")

    def view_expenses(self):
        self.cursor.execute("SELECT description,amount,category,date FROM expenses")
        rows = self.cursor.fetchall()
        if not rows:
            print(YELLOW+"No expense found!"+RESET)
            return
        print(BLUE+"\n==== Your expenses===="+RESET)
        print("+-------+----------------+-----------------------------+--------------------+----------------+")
        print("| No | Date        | category     | amount     | description     |")
        print("+-------+----------------+-----------------------------+--------------------+----------------+")
        for i,(desc,amount,category,date) in enumerate(rows, start=1):
            print(f"{i:<2} {date:<10} {category:<11} {amount:<9} {desc:<17}")
            print("+-------+----------------+-----------------------------+--------------------+----------------+")

    def filter_by_category(self, category):
        self.cursor.execute("SELECT * FROM expenses WHERE category = ?",(category,))
        results = self.cursor.fetchall()
        if not results:
            print(RED+"No expense found for this category!"+RESET)
            return
        print(BLUE+f"\n==== Expenses in category : {category} ===="+RESET)

        print("+-------+----------------+-----------------------------+--------------------+----------------+")
        print("| No | Date        | category     | amount     | description     |")
        print("+-------+----------------+-----------------------------+--------------------+----------------+")
        for i,(id,desc, amount,cat,date)  in enumerate(results, start=1):
            print(f"{i:<2} {date:<10} {category:<11} {amount:<9} {desc:<17}")
            print("+-------+----------------+-----------------------------+--------------------+----------------+")
            print(GREEN+f"Total found:{len(results)}"+RESET)

    def save_to_file(self, filename="expenses.txt"):
        self.cursor.execute("SELECT description, amount, category, date FROM expenses")
        rows = self.cursor.fetchall()

        if not rows:
            print(YELLOW + "No expenses to save!" + RESET)
            return

        with open(filename, "w") as f:
            for desc, amount, cat, date in rows:
                f.write(f"{date},{cat},{amount},{desc}\n")

        print(GREEN + "Expenses saved successfully!" + RESET)
    def load_from_file(self,filename='expenses.txt'):
        if not os.path.isfile(filename):
            return
        with open(filename,"r") as f:
            for line in f:
                date,category,amount,description = line.strip().split(",")
                expense = Expense(date,category,amount,description)
                self.expenses.append(expense)
    def sort_menu(self):
        print(CYAN+"\n=== Sort Expenses ==="+RESET)
        print("1.sorted by Date ")
        print("2.sorted by amount ")
        print("3.sorted by category ")
        option = input("choice sorting option: ")
        if option == "1":
            self.sort_by_date()
        elif option == "2":
            self.sort_by_amount()
        elif option == "3":
            self.sort_by_category()
        else:
            print(RED+"Invalid choice,try again"+RESET)
    def sort_by_date(self):
        self.expenses.sort(key=lambda x: x.date)
        print(GREEN+"sorted by Date Successfully !"+RESET)
        self.view_expenses()
    def sort_by_amount(self):
        self.expenses.sort(key=lambda x: x.amount)
        print(GREEN+"sorted by Amount Successfully !"+RESET)
        self.view_expenses()
    def sort_by_category(self):
        self.expenses.sort(key=lambda x:x.category.lower())
        print(GREEN+"sorted by Category Successfully !"+RESET)
        self.view_expenses()

    def delete_expense(self, index):
        self.cursor.execute("SELECT id FROM expenses")
        rows = self.cursor.fetchall()

        if index < 0 or index >= len(rows):
            print(RED + "Invalid choice, try again!" + RESET)
            return

        exp_id = rows[index][0]

        self.cursor.execute("DELETE FROM expenses WHERE id = ?", (exp_id,))
        self.conn.commit()

        print(GREEN + "Expense deleted successfully!" + RESET)
    def edit_expense(self,index):
        if 0 <= index <len(self.expenses):
            exp=self.expenses[index]
            print("\n=== Editing Expense ===")
            print(f"current description: {exp.description}")
            new_desc = input(f"New description:({exp.description}): ") or exp.description
            print(f"current amount: {exp.amount}")
            new_amount = input(f"New amount:({exp.amount}): ")
            new_amount = float(new_amount) if new_amount else exp.amount
            print(f"current date: {exp.date}")
            new_date = input(f"New date:({exp.date}): ") or exp.date
            print(f"current category: {exp.category}")
            new_cat = input(f"New category:({exp.category}): ") or exp.category
            exp.description = new_desc
            exp.amount = new_amount
            exp.date = new_date
            exp.category = new_cat
            print(GREEN+"Expense updated successfully !"+RESET)
        else:
            print(RED+"Invalid index! "+RESET)
    def search_expense(self,keyword):
        self.cursor.execute("SELECT * FROM expenses WHERE description LIKE ?",('%'+keyword+'%',))
        results = self.cursor.fetchall()
        if not results:
            print(RED+"No matching expenses found! "+RESET)
            return
        print("\nsearch results:")
        for row in results:
            print(row)

    def monthly_summary(self, month, year):
        self.cursor.execute("SELECT description, amount, category, date FROM expenses")
        rows = self.cursor.fetchall()

        total = 0
        print(f"\nMonthly summary for {month}/{year}:")
        print("-" * 40)

        for desc, amount, category, date in rows:
            exp_year, exp_month, exp_day = date.split("/")
            if int(exp_month) == month and int(exp_year) == year:
                print(f"{desc} | {amount} | {category} | {date}")
                total += float(amount)

        print(f"\nTotal spent in {month}/{year} : $ {total}")
    def export_csv(self):
        with open("expenses.csv",'w',newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Date","Description","Amount","Category"])
            for exp in self.expenses:
                writer.writerow([exp.date,exp.description,exp.amount,exp.category])
            print(GREEN+"Expense exported to expenses.csv successfully!"+RESET)

    def created_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS expenses (id integer PRIMARY KEY Autoincrement,description TEXT,amount REAL,category TEXT,date TEXT)""")
        self.conn.commit()

def main():
    manager = ExpenseTracker()
    while True:
        print(CYAN+"\n===Expense Tracker==="+RESET)
        print("1. View Expenses ")
        print("2. Add Expense")
        print("3. Total Expenses")
        print("4. Filter by Category")
        print("5. save expenses")
        print("6. sort expenses")
        print("7. delate expense")
        print("8. edit expense")
        print("9. search expenses")
        print("10. montly summary")
        print("11. export csv")
        print("12. Exit")
        choice = int(input("Enter your choice: "))
        if choice == 1:
           manager.view_expenses()
        elif choice == 2:
            desc = input("Enter expense description: ")
            amount = float(input("Enter expense amount: "))
            category = input("Enter expense category: ")
            date = input("Enter expense date(yyyy/mm/dd): ")
            expense = Expense(desc, amount, category, date)
            manager.add_expense(expense)
            print(GREEN+"Expense Added Successfully !"+RESET)
        elif choice == 3:
            manager.total_expenses()
        elif choice == 4:
            cat=input("Enter expense category: ")
            expense = manager.filter_by_category(cat)
        elif choice == 5:
            manager.save_to_file()
        elif choice == 6:
            manager.sort_menu()
        elif choice == 7:
            manager.view_expenses()
            idx = int(input("Enter expense number to delate: "))-1
            manager.delete_expense(idx)
        elif choice == 8:
            manager.view_expenses()
            index = int(input("Enter expense number to edit: "))-1
            manager.edit_expense(index)
        elif choice == 9:
            manager.search_expense(keyword=input("Enter search keyword: "))
        elif choice == 10:
           month = int(input("Enter month (1-12): "))
           year = int(input("Enter year (yyyy): "))
           manager.monthly_summary(month,year)
        elif choice == 11:
            manager.export_csv()

        elif choice == 12:
            print("exiting expense tracker....")
            break
        else:
            print("Invalid choice,try again")
    def load_from_db(self):
        self.cursor.execute("SELECT decription,amount,category,date FROM expenses")
        rows = self.cursor.fetchall()
        for row in rows:
            desc,amount,category,date = row
            self.expenses.append(Expense(desc,amount,category,date))



if __name__ == "__main__":
    main()
