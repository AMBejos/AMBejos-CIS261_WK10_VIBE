#Anthony Bejos
#CIS261
#WK10 VIBE Coding

import os
import sys

try:
    import tty
    import termios
except ImportError:
    tty = None
    termios = None

FILE_NAME = "student_grades.txt"


def get_data_file_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), FILE_NAME)


def load_records():
    records = []
    file_path = get_data_file_path()

    if not os.path.exists(file_path):
        return records

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue

                parts = line.split("|")
                if len(parts) != 7:
                    print(f"Warning: Skipping invalid file line {line_number}.")
                    continue

                name, student_id, test1, test2, test3, average, grade = parts

                try:
                    record = {
                        "name": name,
                        "id": student_id,
                        "test1": float(test1),
                        "test2": float(test2),
                        "test3": float(test3),
                        "average": float(average),
                        "grade": grade,
                    }
                except ValueError:
                    print(f"Warning: Skipping invalid numeric data on line {line_number}.")
                    continue

                record["average"] = calculate_average(record)
                record["grade"] = determine_letter_grade(record["average"])
                records.append(record)
    except IOError as error:
        print(f"Error loading records from file: {error}")

    return records


def save_records(records):
    file_path = get_data_file_path()

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            for record in records:
                line = (
                    f"{record['name']}|{record['id']}|"
                    f"{record['test1']:.2f}|{record['test2']:.2f}|{record['test3']:.2f}|"
                    f"{record['average']:.2f}|{record['grade']}\n"
                )
                file.write(line)
    except IOError as error:
        print(f"Error saving records to file: {error}")
    else:
        print(f"Saved {len(records)} record(s) to '{FILE_NAME}'.")


def calculate_average(record):
    return (record["test1"] + record["test2"] + record["test3"]) / 3.0


def determine_letter_grade(average):
    if average >= 90:
        return "A"
    if average >= 80:
        return "B"
    if average >= 70:
        return "C"
    if average >= 60:
        return "D"
    return "F"


def prompt_input(prompt_text):
    value = input(prompt_text).strip()
    if value.upper() == "ESC":
        return None
    return value


def read_menu_choice(prompt_text="Choose an option: "):
    if tty is None or termios is None or not sys.stdin.isatty():
        return input(prompt_text).strip()

    sys.stdout.write(prompt_text)
    sys.stdout.flush()
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    if not ch:
        return ""

    if ch == "\x1b":
        sys.stdout.write("\n")
        sys.stdout.flush()
        return "ESC"

    if ch in "12345":
        rest = ""
        while True:
            peek = sys.stdin.read(1)
            if not peek or peek in ("\n", "\r"):
                break
            rest += peek
        sys.stdout.write(ch + "\n")
        sys.stdout.flush()
        return ch

    if ch in ("\r", "\n"):
        return ""

    while True:
        peek = sys.stdin.read(1)
        if not peek or peek in ("\n", "\r"):
            break
    sys.stdout.write(ch + "\n")
    sys.stdout.flush()
    return ch


def prompt_float(prompt_text, min_value=0.0, max_value=100.0):
    while True:
        raw = prompt_input(prompt_text)
        if raw is None:
            return None

        try:
            value = float(raw)
        except ValueError:
            print("Please enter a valid numeric score.")
            continue

        if not (min_value <= value <= max_value):
            print(f"Score must be between {min_value:.0f} and {max_value:.0f}.")
            continue

        return value


def add_student(records):
    print("\nEnter student information or type ESC at any prompt to cancel.")

    while True:
        name = prompt_input("Student name: ")
        if name is None:
            print("Student entry canceled.")
            return

        student_id = prompt_input("Student ID: ")
        if student_id is None:
            print("Student entry canceled.")
            return

        test1 = prompt_float("Test 1 score: ")
        if test1 is None:
            print("Student entry canceled.")
            return

        test2 = prompt_float("Test 2 score: ")
        if test2 is None:
            print("Student entry canceled.")
            return

        test3 = prompt_float("Test 3 score: ")
        if test3 is None:
            print("Student entry canceled.")
            return

        record = {
            "name": name,
            "id": student_id,
            "test1": test1,
            "test2": test2,
            "test3": test3,
        }
        record["average"] = calculate_average(record)
        record["grade"] = determine_letter_grade(record["average"])
        records.append(record)

        print(f"Added {name} with average {record['average']:.2f} and grade {record['grade']}.")

        next_action = prompt_input("Add another student? (Y/N): ")
        if next_action is None or next_action.strip().lower() != "y":
            break


def format_record_row(record):
    return (
        f"{record['name']:<20} | {record['id']:<10} | "
        f"{record['test1']:.2f} | {record['test2']:.2f} | {record['test3']:.2f} | "
        f"{record['average']:.2f} | {record['grade']}"
    )


def display_students(records):
    if not records:
        print("\nNo student records found.")
        return

    header = (
        "Name                 | ID         | Test1 | Test2 | Test3 | Average | Grade"
    )
    separator = "-" * len(header)
    print(f"\n{header}")
    print(separator)
    for record in records:
        print(format_record_row(record))


def calculate_class_statistics(records):
    if not records:
        return None

    highest_record = max(records, key=lambda r: r["average"])
    lowest_record = min(records, key=lambda r: r["average"])
    average = sum(record["average"] for record in records) / len(records)

    return {
        "highest": highest_record["average"],
        "highest_name": highest_record["name"],
        "lowest": lowest_record["average"],
        "lowest_name": lowest_record["name"],
        "average": average,
    }


def display_statistics(records):
    stats = calculate_class_statistics(records)
    if stats is None:
        print("\nNo records available to calculate statistics.")
        return

    print("\nClass Statistics")
    print("----------------")
    print(f"Highest average: {stats['highest']:.2f} ({stats['highest_name']})")
    print(f"Lowest average : {stats['lowest']:.2f} ({stats['lowest_name']})")
    print(f"Class average  : {stats['average']:.2f}")


def search_students(records):
    if not records:
        print("\nNo records to search.")
        return

    search_term = prompt_input("Enter student name to search: ")
    if search_term is None:
        return

    search_term = search_term.lower()
    matches = [rec for rec in records if search_term in rec["name"].lower()]

    if not matches:
        print(f"No students found matching '{search_term}'.")
        return

    print(f"\nFound {len(matches)} matching student(s):")
    display_students(matches)


def print_menu():
    print("\nStudent Grade Calculator")
    print("------------------------")
    print("1. Add new student")
    print("2. Display all students")
    print("3. Display class statistics")
    print("4. Search student by name")
    print("5. Save and Exit (or press ESC)")


def main():
    records = load_records()
    if records:
        print(f"Loaded {len(records)} student record(s) from '{FILE_NAME}'.")
    else:
        print("No existing records found. Starting with an empty list.")

    while True:
        print_menu()
        choice = read_menu_choice()

        if not choice:
            continue

        if choice.upper() == "ESC" or choice == "5":
            print("Saving records and exiting program...")
            save_records(records)
            print("Goodbye.")
            break

        if choice == "1":
            add_student(records)
            continue

        if choice == "2":
            display_students(records)
            continue

        if choice == "3":
            display_statistics(records)
            continue

        if choice == "4":
            search_students(records)
            continue

        print("Invalid option. Please enter 1-5 or ESC.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Saving records before exit...")
        save_records(load_records())
        sys.exit(0)


