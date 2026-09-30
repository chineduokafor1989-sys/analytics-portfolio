import os, io, time, urllib.parse
from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv, find_dotenv
from azure.storage.blob import BlobServiceClient
from sqlalchemy import create_engine, text

load_dotenv(find_dotenv(usecwd=True))

required = [
    "AZURE_STORAGE_ACCOUNT", "AZURE_STORAGE_KEY", "AZURE_STORAGE_CONTAINER",
    "SQL_SERVER", "SQL_DATABASE", "SQL_USER", "SQL_PASSWORD", "SQL_DRIVER",
]
missing = [k for k in required if not os.getenv(k)]
assert not missing, f"Missing values in .env: {missing}"
print("1. All settings found.")

df = pd.DataFrame({
    "order_id": [1, 2, 3],
    "product": ["Laptop", "Mouse", "Monitor"],
    "quantity": [1, 3, 2],
    "unit_price": [999.00, 19.90, 249.50],
    "order_date": ["2026-09-01", "2026-09-02", "2026-09-03"],
})

# Upload to Blob Storage
today = datetime.now(timezone.utc)
blob_path = f"retail/smoke_test/{today:%Y/%m/%d}/smoke_test.csv"
account = os.environ["AZURE_STORAGE_ACCOUNT"]
blob_service = BlobServiceClient(
    account_url=f"https://{account}.blob.core.windows.net",
    credential=os.environ["AZURE_STORAGE_KEY"],
)
blob = blob_service.get_blob_client(
    container=os.environ["AZURE_STORAGE_CONTAINER"], blob=blob_path
)
blob.upload_blob(df.to_csv(index=False).encode("utf-8"), overwrite=True)
print("2. Uploaded to Blob:", blob_path)

csv_text = blob.download_blob().readall().decode("utf-8")
print("3. Read back from Blob:")
print(pd.read_csv(io.StringIO(csv_text)))

# Connect to Azure SQL
pwd = os.environ["SQL_PASSWORD"].replace("}", "}}")
conn_str = (
    f"DRIVER={{{os.environ['SQL_DRIVER']}}};"
    f"SERVER={os.environ['SQL_SERVER']};"
    f"DATABASE={os.environ['SQL_DATABASE']};"
    f"UID={os.environ['SQL_USER']};"
    f"PWD={{{pwd}}};"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60"
)
engine = create_engine(
    "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(conn_str),
    fast_executemany=True,
)

# Serverless databases pause when idle, so retry a few times
for attempt in range(1, 6):
    try:
        with engine.connect() as conn:
            print("4. Connected to SQL:", conn.execute(text("SELECT @@VERSION")).scalar()[:60])
        break
    except Exception as e:
        print(f"Attempt {attempt} failed (database may be resuming): {str(e)[:150]}")
        time.sleep(20)
else:
    raise RuntimeError("Could not connect. Check firewall IP, login, and database status.")

# Load into the raw schema and read back
df.to_sql("smoke_test", engine, schema="retail_raw", if_exists="replace", index=False)
with engine.connect() as conn:
    result = pd.read_sql(text("SELECT * FROM retail_raw.smoke_test"), conn)
print("5. Read back from Azure SQL:")
print(result)

print("\nSmoke test passed: file -> Blob -> Azure SQL all working.")