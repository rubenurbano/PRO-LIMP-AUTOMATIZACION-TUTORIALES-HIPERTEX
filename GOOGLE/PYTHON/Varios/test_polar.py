from polar_sdk import Polar

client = Polar(access_token="polar_oat_CBQytsxQouCim3NmL1GloNsmEiy7dA2nCg8Y60OjTr5")

resp = client.products.list()

for p in resp.result.items:
    print("ID:", p.id)
    print("Nombre:", p.name)
    print("Descripción:", p.description)
    print("¿Recurrente?:", p.is_recurring)
    print("Moneda/pricio tipo custom?:", [price.price_currency for price in p.prices])
    print("-" * 40)


