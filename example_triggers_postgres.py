import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os

load_dotenv()
host = os.getenv('host')
user = os.getenv('user')
password = os.getenv('password')
db = os.getenv('db')
print(host, user, password, db)
class TableRow:
    def __init__(self, _id: int, name: str, balance: float):
        self._id = _id
        self.name = name
        self.balance = balance
        self._on_large_balance_drop = []

    def on_large_balance_drop(self, callback):
        """Регистрирует триггер для значительного снижения баланса."""
        self._on_large_balance_drop.append(callback)

    def check_balance_change(self, previous_balance):
        """Проверяет изменение баланса относительно предыдущего состояния."""
        if previous_balance is not None:
            delta = previous_balance - self.balance
            if delta > 1000:  # Условие триггера
                for callback in self._on_large_balance_drop:
                    callback(self, previous_balance, self.balance)


class TableMonitor:
    def __init__(self, connection_string: str, table_name: str, schema_name: str):
        self.engine = create_engine(connection_string)
        self.table_name = table_name
        self.schema_name = schema_name
        self.previous_data = pd.DataFrame()
        self._on_row_change = []

    def on_row_change(self, callback):
        """Trigger for all rows"""
        self._on_row_change.append(callback)

    def load_data(self, start_date: str, end_date: str, ogrn: str):
        """load data from Postgres on specific period"""
        query = f"""
        SELECT * 
        FROM {self.schema_name}.{self.table_name}
        WHERE date_ BETWEEN '{start_date}' AND '{end_date}' AND name_ = '{ogrn}'
        """
        return pd.read_sql(query, self.engine)

    def process_changes(self, current_data: pd.DataFrame):
        """Compare both states last + present"""
        previous_row = current_data.iloc[[0]]
        for _, row in current_data.iterrows():
            # previous_row = self.previous_data[self.previous_data['_id'] == row['_id']]
            previous_balance = previous_row['balance'].iloc[0] if not previous_row.empty else None

            table_row = TableRow(row['_id'], row['name_'], row['balance'])

            table_row.on_large_balance_drop(self.handle_large_balance_drop)

            table_row.check_balance_change(previous_balance)

            previous_row = pd.DataFrame(row).T

            for callback in self._on_row_change:
                callback(row, previous_row)

       #update prev data with current data
        self.previous_data = current_data

    def handle_large_balance_drop(self, row, previous_balance, current_balance):
        """if balance decrease """
        print(f"[Trigger]: User {row.name} (ID={row._id}) "
              f"balance decrease from  {previous_balance} to {current_balance}.")

    def monitor(self, start_date: str, end_date: str, ogrn: str):
        """Load data"""
        current_data = self.load_data(start_date, end_date, ogrn)
        print(current_data)
        self.process_changes(current_data)

connection_string = f"postgresql://{user}:{password}@{host}:5432/{db}"
monitor = TableMonitor(connection_string, table_name="test_1", schema_name="test_triggers")

def notify_row_change(current_row, previous_row):
    if previous_row.values.tolist()[0] != current_row.values.tolist():
        print(f"[Full trigger]: Row ID={current_row['_id']} was changed.")
    # else:
    #     print(f"[Общий триггер]: Новая строка добавлена ID={current_row['_id']}.")

monitor.on_row_change(notify_row_change)

monitor.monitor("2014-01-01", "2014-01-02", "Alice")
