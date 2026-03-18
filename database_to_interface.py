from database.database import Base
from database.models import *
import re

if __name__ == "__main__":
    all_types = {
        'VARCHAR(255)': 'string',
        'FLOAT': 'number',
        'DATETIME': 'number | null',
        'DATE': 'string | null',
        'BOOLEAN': 'boolean',
        'TEXT': 'string',
        'INTEGER': 'number'
    }
    for i in Base.__subclasses__():
        line = f"export interface {i.__name__}Model " + "{"
        content = line
        print(line)
        for item in i.__table__.columns:
            item_type = str(item.type)
            line = f"  {item.key}: {all_types[item_type]};"
            print(line)
            content += f"\n{line}"
        line = "}"
        print(line)
        content += f"\n{line}"

        translated = re.sub(r'(?<!^)(?=[A-Z])|_', '-', i.__name__).lower()
        with open(f'./db_models/{translated}.model.ts', "w") as f:
            f.write(content)
