import requests

class CatalogManager:
    def __init__(self):
        self.url = "https://automationexercise.com/api/productsList"

    def get_products(self):
        """Petición real a la API."""
        response = requests.get(self.url)
        if response.status_code != 200:
            return []
        return response.json().get("products", [])

    def filter_by_brand(self, brand_name):
        """Lógica de negocio: Filtra productos por marca."""
        products = self.get_products()
        return [p for p in products if p.get("brand").lower() == brand_name.lower()]

    def get_total_products_count(self):
        """Lógica de negocio: Cuenta el total de productos."""
        products = self.get_products()
        return len(products)