from catalog_manager import CatalogManager

def run_app():
    print("=== BIENVENIDO AL CATALOG MANAGER ===")
    manager = CatalogManager()
    
    # 1. Obtener todos los productos (Integración)
    print("\nConsultando productos en la API...")
    products = manager.get_products()
    print(f"Se encontraron {len(products)} productos.")

    # 2. Usar lógica de filtrado
    brand = "Polo"
    print(f"\nFiltrando por la marca: '{brand}'...")
    filtered = manager.filter_by_brand(brand)
    
    for p in filtered:
        print(f" - [{p['id']}] {p['name']} | Precio: {p['price']}")

    # 3. Mostrar estadísticas
    total = manager.get_total_products_count()
    print(f"\nResumen: Hay un total de {total} productos disponibles.")

if __name__ == "__main__":
    run_app()