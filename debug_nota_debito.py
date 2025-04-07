from sqlalchemy import inspect
from src.models import session
from src.models.nota_debito import NotaDebito  # adjust import as needed

def debug_nota_debito_columns():
    """
    Debug method to inspect columns of the nota_debito table
    """
    # Get the table
    inspector = inspect(session.bind)
    
    # Get columns for nota_debito table
    columns = inspector.get_columns('nota_debito')
    
    print("Columns in nota_debito table:")
    for column in columns:
        print(f"Name: {column['name']}, Type: {column['type']}")
    
    # Check if 'enviada' column exists
    enviada_column = [col for col in columns if col['name'] == 'enviada']
    if enviada_column:
        print("\n'enviada' column found:")
        print(enviada_column[0])
    else:
        print("\n'enviada' column NOT found!")

    # Additional SQLAlchemy model inspection
    print("\nSQLAlchemy Model Columns:")
    mapper = inspect(NotaDebito)
    for column in mapper.columns:
        print(f"Column: {column.key}, Type: {column.type}")

# Run the debug function
debug_nota_debito_columns()