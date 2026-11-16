from collections import UserDict
from dataclasses import dataclass
import re
from datetime import datetime, timedelta
from bot_exceptions import ExtendedValueError, BirthdayError

@dataclass
class Field:
  value: str

  def __str__(self):
      return str(self.value)

@dataclass
class Name(Field):
  def __post_init__(self):
    if not self.value or not self.value.strip():
      raise ExtendedValueError("Name cannot be empty. Please provide a valid name")

class Phone(Field):
  def __init__(self, value):
    super().__init__(value)

    if not self.__is_phone_valid():
      raise ExtendedValueError(f"Phone number {self.value} is incorrect. It should contain 10 numbers")

  def __is_phone_valid(self) -> bool:
    pattern = r"^\d{10}$"
    match = re.match(pattern, self.value)

    return match is not None

class Birthday(Field):
  def __init__(self, value):
    self.value = None
    self.__date_str_format = '%d.%m.%Y'
    self.__validate_date(value)

  def __validate_date(self, value: str):
    try:
      datetime.strptime(value, self.__date_str_format)
      self.value = value
    except ValueError:
      raise BirthdayError
    except TypeError:
      raise BirthdayError(f'Provided value is not a date. Please provide a date in DD.MM.YYYY format.')

class Record:
  def __init__(self, name: str):
    self.name = Name(name)
    self.phones = []
    self.birthday: Birthday | None = None

  def add_phone(self, phone: str):
     self.phones.append(Phone(phone))

  def remove_phone(self, phone: str):
    phone_to_remove = self.find_phone(phone)
    if phone_to_remove:
      self.phones.remove(phone_to_remove)

  def edit_phone(self, old_phone: str, new_phone: str):
    phone_to_edit = self.find_phone(old_phone)
    if phone_to_edit:
      index = self.phones.index(phone_to_edit)
      self.phones[index] = Phone(new_phone)
    else:
     raise ExtendedValueError(f"Phone number {old_phone} doesn't exist.")

  def find_phone(self, number: str) -> Phone | None:
    return next((phone for phone in self.phones if phone.value == number), None)

  def add_birthday(self, date: str):
    self.birthday = Birthday(date)

  def __str__(self):
    res = f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    if self.birthday:
      res += f", birthday: {self.birthday.value}"
    return res

class AddressBook(UserDict):
  def add_record(self, record: Record):
    name = record.name.value
    if name in self.data:
      raise ExtendedValueError("Contact already exists.")

    self.data[name] = record

  def find(self, name: str) -> Record | None:
    try:
      return self.data[name]
    except KeyError:
      return None

  def delete(self, name: str):
    if name in self.data:
      del self.data[name]

  def get_upcoming_birthdays(self) -> list[dict]:
    today = datetime.today().date()
    date_str_format = '%d.%m.%Y'
    congratulation_list = []

    for name in self.data:
      user = self.find(name)
      if user.birthday == None:
        continue

      users_bd = datetime.strptime(user.birthday.value, date_str_format).date()
      birthday_this_year = self.__handle_leap_year(users_bd, today.year)

      should_notify_next_year = today.weekday() == 0 and (today - birthday_this_year).days > 2 or today.weekday() > 0 and  birthday_this_year < today

      if should_notify_next_year:
        birthday_this_year = self.__handle_leap_year(users_bd, today.year + 1)

      diff = (birthday_this_year - today).days

      if diff < 7:
        birthday_weekday = birthday_this_year.weekday()

        if (birthday_weekday >= 5):
          first_weekday = 7 - birthday_weekday
          birthday_this_year += timedelta(days=first_weekday)

        congratulation_list.append({
          "name": name,
          "congratulation_date": birthday_this_year.strftime(date_str_format)
        })

    return congratulation_list

  def __handle_leap_year(self, date: datetime.date, year: int) -> datetime.date:
    try:
      return date.replace(year=year)
    except ValueError:
      return date.replace(year=year, month=3, day=1)

