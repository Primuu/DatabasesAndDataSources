import json
import oracledb
from variables import *
import re


def load_data_from_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def validate_agent_client(record):
    if not record["first_name"] or not record["last_name"] or not record["phone_number"] or not record["email"]:
        return False, "Required field is missing."
    if len(record["phone_number"]) > 15:
        return False, "Phone number exceeds max length of 15."
    if not re.match(r"^\S+@\S+\.\S+$", record["email"]):
        return False, "Invalid email format."
    return True, ""


def validate_address(record):
    if not record["address_id"] or not record["locality"] or not record["zip_code"] or not record["property_number"]:
        return False, "Required field is missing."
    if len(record["zip_code"]) > 10:
        return False, "ZIP code exceeds max length of 10."
    return True, ""


def validate_estate(record):
    if not record["estate_id"] or not record["area"] or not record["price"] or not record["status_id"]:
        return False, "Required field is missing."
    if record["area"] <= 0:
        return False, "Area must be greater than 0."
    if record["price"] <= 0:
        return False, "Price must be greater than 0."
    return True, ""


def validate_transaction(record):
    if not record["transaction_id"] or not record["estate_id"] or not record["client_id"] or not record["agent_id"] or not record["transaction_date"]:
        return False, "Required field is missing."
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", record["transaction_date"]):
        return False, "Transaction date must be in format YYYY-MM-DD."
    return True, ""


def validate_data(table_name, data):
    validation_results = []
    for record in data:
        if table_name == "agents" or table_name == "clients":
            valid, error = validate_agent_client(record)
        elif table_name == "addresses":
            valid, error = validate_address(record)
        elif table_name == "estates":
            valid, error = validate_estate(record)
        elif table_name == "transactions":
            valid, error = validate_transaction(record)
        else:
            valid, error = True, ""
        if not valid:
            validation_results.append((record, error))
    return validation_results


def insert_data(cursor, table_name, data, columns):
    placeholders = ", ".join([f":{i + 1}" for i in range(len(columns))])
    sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

    try:
        rows = [[record[col] for col in columns] for record in data]
        cursor.executemany(sql, rows)
        print(f"Successfully inserted {len(rows)} records into '{table_name}'.")
    except Exception as e:
        print(f"Error inserting into {table_name}: {e}")


def main():
    json_file = "fake_estate_data.json"
    data = load_data_from_json(json_file)

    print("Validating data...")

    invalid_agents = validate_data("agents", data["agents"])
    invalid_clients = validate_data("clients", data["clients"])
    invalid_addresses = validate_data("addresses", data["addresses"])
    invalid_estates = validate_data("estates", data["estates"])
    invalid_transactions = validate_data("transactions", data["transactions"])

    if invalid_agents or invalid_clients or invalid_addresses or invalid_estates or invalid_transactions:
        print("Data validation failed:")
        for invalid_set, name in [
            (invalid_agents, "Agents"),
            (invalid_clients, "Clients"),
            (invalid_addresses, "Addresses"),
            (invalid_estates, "Estates"),
            (invalid_transactions, "Transactions")
        ]:
            if invalid_set:
                print(f"\nInvalid records in {name}:")
                for record, error in invalid_set:
                    print(f"Record: {record}, Error: {error}")
        return

    print("Data validation passed. Proceeding to load data into the database.")

    try:
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as connection:
            with connection.cursor() as cursor:
                print("Connected to Oracle database.")
                print("Loading data...")

                insert_data(cursor, "agents", data["agents"],
                            [
                                # "agent_id",
                                "first_name",
                                "last_name",
                                "phone_number",
                                "email",
                                "commission_rate"
                            ])

                insert_data(cursor, "clients", data["clients"],
                            [
                                # "client_id",
                                "first_name",
                                "last_name",
                                "phone_number",
                                "email",
                                "budget"
                            ])

                insert_data(cursor, "estate_statuses", data["estate_statuses"],
                            [
                                # "status_id",
                                "status_name"
                            ])

                insert_data(cursor, "estate_types", data["estate_types"],
                            [
                                # "type_id",
                                "type_name"
                            ])

                insert_data(cursor, "estate_features", data["estate_features"],
                            [
                                # "feature_id",
                                "estate_description",
                                "num_of_rooms",
                                "num_of_bedrooms",
                                "num_of_bathrooms",
                                "floor_number",
                                "num_of_parking_spaces"
                            ])

                insert_data(cursor, "addresses", data["addresses"],
                            [
                                # "address_id",
                                "locality",
                                "street",
                                "zip_code",
                                "property_number",
                                "apartment_number"
                            ])

                insert_data(cursor, "estates", data["estates"],
                            [
                                # "estate_id",
                                "feature_id",
                                "address_id",
                                "agent_id",
                                "status_id",
                                "type_id",
                                "estate_name",
                                "area",
                                "price"
                            ])

                insert_data(cursor, "transactions", data["transactions"],
                            [
                                # "transaction_id",
                                "estate_id",
                                "client_id",
                                "agent_id",
                                "transaction_date",
                                "sale_price"
                            ])

                connection.commit()
                print("Data loaded successfully.")
    except oracledb.DatabaseError as e:
        print(f"Database error: {e}")
    except Exception as ex:
        print(f"Unexpected error: {ex}")
    finally:
        print("The connection to the database has been closed.")


if __name__ == "__main__":
    main()
