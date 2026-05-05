#!/usr/bin/env python3
"""
Commandes de gestion du projet devZair.

Usage :
  python src/manage.py create-user
  python src/manage.py create-user --username admin --password monmotdepasse
"""
import argparse
import asyncio
import getpass
import sys


async def cmd_create_user(username: str, password: str) -> None:
    from app.core.security import hash_password
    from app.database.session import async_session_factory
    from app.repositories.user_repository import UserRepository

    async with async_session_factory() as session:
        repo = UserRepository(session=session)
        existing = await repo.get_by_username(username)
        hashed = hash_password(password)

        if existing:
            await repo.update_password(existing, hashed)
            print(f"\n✅  Mot de passe mis à jour pour « {username} ».")
        else:
            await repo.create(username, hashed)
            print(f"\n✅  Utilisateur « {username} » créé avec succès.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Outil de gestion devZair",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    user_parser = subparsers.add_parser(
        "create-user",
        help="Créer ou mettre à jour un utilisateur admin",
    )
    user_parser.add_argument("--username", "-u", default="", help="Nom d'utilisateur (défaut : admin)")
    user_parser.add_argument("--password", "-p", default="", help="Mot de passe (saisie masquée si omis)")

    args = parser.parse_args()

    if args.command == "create-user":
        username = args.username.strip() or input("Nom d'utilisateur [admin] : ").strip() or "admin"

        if args.password:
            password = args.password
        else:
            password = getpass.getpass("Mot de passe : ")
            confirm = getpass.getpass("Confirmer le mot de passe : ")
            if password != confirm:
                print("❌  Les mots de passe ne correspondent pas.", file=sys.stderr)
                sys.exit(1)

        if len(password) < 8:
            print("❌  Le mot de passe doit faire au moins 8 caractères.", file=sys.stderr)
            sys.exit(1)

        asyncio.run(cmd_create_user(username, password))


if __name__ == "__main__":
    main()
