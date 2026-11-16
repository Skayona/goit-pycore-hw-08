from address_book import Record, AddressBook
from bot_exceptions import BirthdayError, MissingContactError, ExtendedValueError

def input_error(func):
  def inner(*args, **kwargs):
    try:
      print(args)
      return func(*args, **kwargs)
    except ValueError:
      return "Not all data is provided."
    except IndexError:
      return "Enter user name."
    except KeyError:
      return "Contact not found."
    except (ExtendedValueError, MissingContactError, BirthdayError) as e:
      return e.message

  return inner

def get_record(book: AddressBook, name: str) -> Record:
  record = book.find(name)
  if record is None:
    raise MissingContactError(name)
  return record

@input_error
def parse_input(user_input: str) -> tuple[str, ...]:
  user_input = user_input.strip()
  cmd, *args = user_input.split()
  cmd = cmd.lower()

  return cmd, *args

@input_error
def add_contact(args: list[str], book: AddressBook) -> str:
  name, phone, *_ = args
  record = book.find(name)
  message = "Contact updated."

  if record is None:
    record = Record(name)
    book.add_record(record)
    message = "Contact added."

  if phone:
    record.add_phone(phone)

  return message

@input_error
def change_contact(args: list[str], book: AddressBook) -> str:
  name, old_phone, new_phone, *_ = args
  record = get_record(book, name)
  record.edit_phone(old_phone, new_phone)
  return "Contact updated."

@input_error
def show_phone(args: list[str], book: AddressBook) -> str:
  name = args[0]
  record = get_record(book, name)
  return record

@input_error
def add_birthday(args: list[str], book: AddressBook) -> str:
  name, date, *_ = args
  record = get_record(book, name)
  record.add_birthday(date)
  return "Birthday added."

@input_error
def show_birthday(args: list[str], book: AddressBook) -> str:
  name, *_ = args
  record = get_record(book, name)
  return "No birthday date" if record.birthday == None else record.birthday

def birthdays(book: AddressBook) -> str:
  if not book:
    return "The contacts list is empty."

  upcoming_list = "\n".join([f"{upcoming_bd.get('name')}: {upcoming_bd.get('congratulation_date')}" for upcoming_bd in book.get_upcoming_birthdays()])

  return upcoming_list or "No upcoming birthdays."

def show_all(book: AddressBook) -> str:
  if not book:
    return "The contacts list is empty."

  return "\n".join([f"{record}" for record in book.values()])

def main():
  book = AddressBook()
  print("Welcome to the assistant bot!")

  while True:
    user_input = input("Enter a command: ")
    command, *args = parse_input(user_input)

    match command:
      case "hello":
        print("How can I help you?")
      case "close" | "exit":
        print("Good bye!")
        break
      case "add":
        print(add_contact(args, book))
      case "change":
        print(change_contact(args, book))
      case "phone":
        print(show_phone(args, book))
      case "all":
        print(show_all(book))
      case "add-birthday":
        print(add_birthday(args, book))
      case "show-birthday":
        print(show_birthday(args, book))
      case "birthdays":
        print(birthdays(book))
        pass
      case _:
        print("Invalid command.")

if __name__ == "__main__":
  main()
