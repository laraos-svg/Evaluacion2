
import requests
import urllib.parse

geocode_url = "http://localhost:8082/api/1/geocode?"
route_url = "http://localhost:8082/api/1/route?"
key = "ab025f53-2e99-449c-90d4-0d255f731583"  # Reemplaza esto por tu clave válida en el editor


def geocoding(location, key):
    while location.strip() == "":
        location = input("Ingresa una ubicación: ")

    params = {
        "q": location,
        "limit": "1",
        "key": key
    }
    url = geocode_url + urllib.parse.urlencode(params)

    try:
        response = requests.get(url, timeout=30)
        json_data = response.json()
        status = response.status_code
    except requests.RequestException as error:
        print("Error de conexión al buscar la ubicación:", error)
        return 500, None, None, location

    if status == 200 and len(json_data.get("hits", [])) > 0:
        hit = json_data["hits"][0]
        lat = hit["point"]["lat"]
        lng = hit["point"]["lng"]
        name = hit["name"]
        state = hit.get("state", "")
        country = hit.get("country", "")

        parts = [name]
        if state and state != name:
            parts.append(state)
        if country:
            parts.append(country)

        new_loc = ", ".join(parts)
        print("Ubicación encontrada:", new_loc)
        return status, lat, lng, new_loc

    if status == 200:
        print("No se encontró la ubicación:", location)
        return 404, None, None, location

    print("Error al buscar la ubicación. Código:", status)
    print("Mensaje:", json_data.get("message", "Error desconocido"))
    return status, None, None, location


while True:
    loc1 = input(
        "\nIngresa el origen (o escribe 's' o 'salir' para terminar): "
    ).strip()

    if loc1.lower() in ("s", "salir"):
        print("Programa finalizado.")
        break

    orig = geocoding(loc1, key)
    if orig[0] != 200:
        continue

    loc2 = input(
        "Ingresa el destino (o escribe 's' o 'salir' para terminar): "
    ).strip()

    if loc2.lower() in ("s", "salir"):
        print("Programa finalizado.")
        break

    dest = geocoding(loc2, key)
    if dest[0] != 200:
        continue

    print("=" * 55)
    print("Ruta desde", orig[3], "hasta", dest[3])
    print("=" * 55)

    params = [
        ("key", key),
        ("point", f"{orig[1]},{orig[2]}"),
        ("point", f"{dest[1]},{dest[2]}"),
        ("locale", "es")
    ]
    paths_url = route_url + urllib.parse.urlencode(params)

    try:
        response = requests.get(paths_url, timeout=60)
        paths_data = response.json()
        paths_status = response.status_code
    except requests.RequestException as error:
        print("Error de conexión al calcular la ruta:", error)
        continue

    if paths_status == 200:
        path_data = paths_data["paths"][0]

        distance_m = path_data["distance"]
        distance_km = distance_m / 1000
        total_seconds = int(path_data["time"] / 1000)

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        print(f"Distancia total: {distance_km:.2f} km / {distance_m:.2f} m")
        print(
            f"Duración estimada: "
            f"{hours:02d}:{minutes:02d}:{seconds:02d} (hh:mm:ss)"
        )

        print("\nInstrucciones del viaje:")
        for instruction in path_data["instructions"]:
            text = instruction["text"]
            distance = instruction["distance"]

            print(
                f"- {text} "
                f"({distance / 1000:.2f} km / {distance:.2f} m)"
            )

        print("=" * 55)
    else:
        print("No se pudo calcular la ruta.")
        print("Código de respuesta:", paths_status)
        print("Mensaje:", paths_data.get("message", "Error desconocido"))
