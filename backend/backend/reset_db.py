# clean_database.py
import psycopg2
from app.database import engine


def clean_database():
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host="localhost",
        database="agrisetu",
        user="postgres",
        password="password"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Drop ALL tables to start fresh
    tables_to_drop = [
        'weather', 'users', 'farmers', 'vendors', 'crops', 'price_predictions',
        'farmer', 'marketlisting', 'crop', 'transaction', 'vendor', 'pricehistory',
        'crop_diseases', 'price_histories', 'market_listings', 'crop_suggestions',
        'transactions', 'notifications', 'analytics_dashboards', 'system_logs',
        'weather_alerts'
    ]
    
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            print(f"✅ Dropped table: {table}")
        except Exception as e:
            print(f"❌ Could not drop {table}: {e}")
    
    cursor.close()
    conn.close()
    print("🎉 Database cleaned! All tables dropped.")

if __name__ == "__main__":
    clean_database()