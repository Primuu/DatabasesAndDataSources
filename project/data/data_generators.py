import json
import random
from faker import Faker

fake = Faker()

STATUSES = [
    {"status_id": 1000, "status_name": "Available"},
    {"status_id": 1001, "status_name": "Sold"},
    {"status_id": 1002, "status_name": "Reserved"}
]

TYPES = [
    {"type_id": 1000, "type_name": "Apartment"},
    {"type_id": 1001, "type_name": "House"},
    {"type_id": 1002, "type_name": "Commercial"},
    {"type_id": 1003, "type_name": "Land"}
]


def generate_ids(start, count):
    return list(range(start, start + count))


def generate_agents(count):
    agents = []
    ids = generate_ids(1000, count)
    for agent_id in ids:
        agent = {
            "agent_id": agent_id,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone_number": fake.numerify(text="+##-###-###-###"),
            "email": fake.email(),
            "commission_rate": round(random.uniform(5.0, 10.0), 2)
        }
        agents.append(agent)
    return agents


def generate_clients(count):
    clients = []
    ids = generate_ids(1000, count)
    for client_id in ids:
        client = {
            "client_id": client_id,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone_number": fake.numerify(text="+##-###-###-###"),
            "email": fake.email(),
            "budget": random.randint(400_000, 3_600_000)
        }
        clients.append(client)
    return clients


def generate_features(count):
    features = []
    ids = generate_ids(1000, count)
    for feature_id in ids:
        feature = {
            "feature_id": feature_id,
            "estate_description": fake.text(max_nb_chars=200),
            "num_of_rooms": random.randint(1, 10),
            "num_of_bedrooms": random.randint(1, 5),
            "num_of_bathrooms": random.randint(1, 3),
            "floor_number": random.randint(0, 20),
            "num_of_parking_spaces": random.randint(0, 5)
        }
        features.append(feature)
    return features


def generate_addresses(count):
    addresses = []
    ids = generate_ids(1000, count)
    for address_id in ids:
        address = {
            "address_id": address_id,
            "locality": fake.city(),
            "street": fake.street_name(),
            "zip_code": fake.numerify(text="##-###"),
            "property_number": str(random.randint(1, 100)),
            "apartment_number": str(random.randint(1, 50))
        }
        addresses.append(address)
    return addresses


def generate_estates(count, agents, statuses, types):
    estates = []
    ids = generate_ids(1000, count)
    for estate_id in ids:
        area = random.randint(35, 400)
        price_per_meter = random.randint(3_500, 30_000)

        estate = {
            "estate_id": estate_id,
            "feature_id": estate_id,
            "address_id": estate_id,
            "agent_id": random.choice(agents)["agent_id"],
            "status_id": random.choice(statuses)["status_id"],
            "type_id": random.choice(types)["type_id"],
            "estate_name": fake.street_name(),
            "area": area,
            "price": area * price_per_meter
        }
        estates.append(estate)
    return estates


def generate_transactions(count, estates, clients, agents):
    transactions = []
    sold_estates = [estate for estate in estates if estate["status_id"] == 1001]

    if len(sold_estates) < count:
        raise ValueError("The number of properties sold is lower than the number of transactions to be generated.")

    ids = generate_ids(1000, count)
    used_clients = set()

    for transaction_id in ids:
        estate = sold_estates.pop(random.randrange(len(sold_estates)))

        client = random.choice([c for c in clients if c["client_id"] not in used_clients])
        used_clients.add(client["client_id"])

        agent_id = estate["agent_id"]
        agent = next(agent for agent in agents if agent["agent_id"] == agent_id)

        commission = estate["price"] * (agent["commission_rate"] / 100)
        final_price = estate["price"] + round(commission)

        transaction_date = fake.date_between(start_date='-2y', end_date='today')
        transaction = {
            "transaction_id": transaction_id,
            "estate_id": estate["estate_id"],
            "client_id": client["client_id"],
            "agent_id": agent["agent_id"],
            "transaction_date": transaction_date.strftime('%Y-%m-%d'),
            "sale_price": final_price
        }
        transactions.append(transaction)
    return transactions


def main():
    agents = generate_agents(24)
    clients = generate_clients(300)
    features = generate_features(996)
    addresses = generate_addresses(996)
    estates = generate_estates(996, agents, STATUSES, TYPES)
    transactions = generate_transactions(200, estates, clients, agents)

    data = {
        "agents": agents,
        "clients": clients,
        "estate_statuses": STATUSES,
        "estate_types": TYPES,
        "estate_features": features,
        "addresses": addresses,
        "estates": estates,
        "transactions": transactions
    }

    with open("fake_estate_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("The data was generated and saved to a file.")


if __name__ == "__main__":
    main()
