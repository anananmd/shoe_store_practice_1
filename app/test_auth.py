from app.services.auth_service import authenticate, get_guest_user


def main() -> None:
    print(authenticate("admin", "123"))
    print(authenticate("manager", "123"))
    print(authenticate("client", "123"))
    print(authenticate("admin", "wrong"))
    print(get_guest_user())


if __name__ == "__main__":
    main()
