from app.services.product_service import get_all_products


def main() -> None:
    products = get_all_products()

    for product in products:
        print(product)


if __name__ == "__main__":
    main()
