class TableRow:
    def __init__(self, id: int, ogrn: str, inn: str):
        self.id = id
        self._ogrn = None
        self._inn = None
        self._on_inn_change = []
        self._on_ogrn_change = []

        self.ogrn = ogrn
        self.inn = inn

    # Свойство name
    @property
    def ogrn(self):
        return self._ogrn

    @ogrn.setter
    def ogrn(self, new_ogrn: str):
        if not new_ogrn.strip():
            raise ValueError("OGRN can not be empty!")
        old_ogrn = self._ogrn
        self._ogrn = new_ogrn
        self._trigger_ogrn_change(old_ogrn, new_ogrn)

    # Свойство balance
    @property
    def inn(self):
        return self._inn

    @inn.setter
    def inn(self, new_inn: float):
        if new_inn == "":
            raise ValueError("INN can not be ")
        old_inn = self.inn
        self._inn = new_inn
        self._trigger_inn_change(old_inn, new_inn)

    # Методы для регистрации триггеров
    def on_inn_change(self, callback):
        """Registers a handler for changing the INN."""
        self._on_inn_change.append(callback)

    def on_ogrn_change(self, callback):
        """Registers a handler for changing the OGRN."""
        self._on_ogrn_change.append(callback)

    # Вызов триггеров
    def _trigger_inn_change(self, old_balance, new_balance):
        """Calls all registreted triggers."""
        for callback in self._on_inn_change:
            callback(self, old_balance, new_balance)

    def _trigger_ogrn_change(self, old_ogrn, new_ogrn):
        """Calls all registered triggers for the OGRN."""
        for callback in self._on_ogrn_change:
            callback(self, old_ogrn, new_ogrn)

def notify_balance_change(row, old_INN, new_INN):
    print(f"INN of {row.ogrn} was changed from  {old_INN} to {new_INN}.")

def notify_name_change(row, old_ogrn, new_ogrn):
    print(f"OGRN was changed from '{old_ogrn}' to '{new_ogrn}'.")


row = TableRow(id=1, ogrn="Alice", inn=100.0)

row.on_ogrn_change(notify_balance_change)
row.on_inn_change(notify_name_change)


row.inn = 150.0
row.ogrn = "Bob"

row.ogrn = "1312r12r1"

try:
    row.inn = -50
except ValueError as e:
    print(f"Ошибка: {e}")

try:
    row.ogrn = " "
except ValueError as e:
    print(f"Ошибка: {e}")
