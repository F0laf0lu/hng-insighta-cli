import json
from pathlib import Path
import tabulate
from yaspin import yaspin
from datetime import datetime


import click
import requests


@click.group()
def profile():
    pass


@click.command()
@click.option("--gender", type=click.STRING)
@click.option("--country", type=click.STRING)
@click.option("--age-group", type=click.STRING)
@click.option("--min-age", type=click.INT)
@click.option("--max-age", type=click.INT)
@click.option("--sort-by", type=click.STRING)
@click.option("--order", type=click.STRING)
@click.option("--page", type=click.INT)
@click.option("--limit", type=click.INT)
def list(gender, country, age_group, min_age, max_age, sort_by, order, page, limit):
    path = Path(Path.home(), ".insighta/credentials.json")
    if not path.exists():
        click.echo("Invalid token path")
        return
    with open(path, "r") as file:
        content = json.loads(file.read())
        access_token = content["data"]["access_token"]
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            "X-API-Version": 1,
        }
        url = "http://127.0.0.1:8000/api/profiles"
        with yaspin(text="Loading", color="yellow") as spinner:
            response = requests.get(
                url,
                params={
                    "sort_by": sort_by,
                    "gender": gender,
                    "age_group": age_group,
                    "country_id": country,
                    "page": page,
                    "limit": limit,
                    "order": order,
                    "min_age": min_age,
                    "max_age": max_age,
                },
                headers=headers,
            )
            response.raise_for_status()
            if response.ok:
                spinner.ok("✅")
                data = response.json()["data"]
                table = tabulate(data, headers="keys", tablefmt="pipe")
                click.echo(table)
            else:
                spinner.fail("💥")


@click.command()
@click.argument("query", type=click.STRING)
def search(query):
    path = Path(Path.home(), ".insighta/credentials.json")
    if not path.exists():
        click.echo("Invalid token path")
        return
    with open(path, "r") as file:
        content = json.loads(file.read())
        access_token = content["data"]["access_token"]
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            "X-API-Version": 1,
        }
        url = "http://127.0.0.1:8000/api/profiles/search"
        with yaspin(text="Loading", color="yellow") as spinner:
            response = requests.get(url, params={"q": query}, headers=headers)
            response.raise_for_status()
            if response.ok:
                spinner.ok("✅")
                data = response.json()["data"]
                table = tabulate(data, headers="keys", tablefmt="pipe")
                click.echo(table)
            else:
                spinner.fail("💥")


@click.command()
@click.option("--name", type=click.STRING)
def create(name):
    path = Path(Path.home(), ".insighta/credentials.json")
    if not path.exists():
        click.echo("Invalid token path")
        return
    with open(path, "r") as file:
        content = json.loads(file.read())
        access_token = content["data"]["access_token"]
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            "X-API-Version": 1,
        }
        url = "http://127.0.0.1:8000/api/profiles"

        with yaspin(text="Loading", color="yellow") as spinner:
            response = requests.post(url, json={"name": name}, headers=headers)
            response.raise_for_status()
            if response.ok:
                spinner.ok("✅")
                data = response.json()["data"]
                table = tabulate(data, headers="keys", tablefmt="pipe")
                click.echo(table)
            else:
                spinner.fail("💥")


@click.command()
@click.option("--format", type=click.Choice(["csv"]))
@click.option("--gender", type=click.STRING)
@click.option("--country", type=click.STRING)
def export(format, gender, country):
    path = Path(Path.home(), ".insighta/credentials.json")
    if not path.exists():
        click.echo("Invalid token path")
        return
    with open(path, "r") as file:
        content = json.loads(file.read())
        access_token = content["data"]["access_token"]
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            "X-API-Version": 1,
        }
        url = "http://127.0.0.1:8000/api/profiles/export"

        with yaspin(text="Loading", color="yellow") as spinner:
            response = requests.get(
                url,
                params={"format": format, "gender": gender, "country_id": country},
                headers=headers,
            )
            response.raise_for_status()
            if response.ok:
                spinner.ok("✅")
                data = response.text
                export_path = Path(
                    Path.cwd(),
                    f"profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                )
                with open(export_path, "w") as file:
                    file.write(data)
                    click.echo(f"Data exported to {export_path}")
            else:
                spinner.fail("💥")


@click.command()
@click.argument("id")
def get(id):
    path = Path(Path.home(), ".insighta/credentials.json")
    if not path.exists():
        click.echo("Invalid token path")
        return
    with open(path, "r") as file:
        content = json.loads(file.read())
        access_token = content["data"]["access_token"]
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            "X-API-Version": 1,
        }
        url = f"http://127.0.0.1:8000/api/profiles/{id}"
        with yaspin(text="Loading", color="yellow") as spinner:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            if response.ok:
                spinner.ok("✅")
                data = response.json()["data"]
                table = tabulate([data], headers="keys", tablefmt="pipe")
                click.echo(table)
            else:
                spinner.fail("💥")


profile.add_command(list)
profile.add_command(search)
profile.add_command(create)
profile.add_command(export)
