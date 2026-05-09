import click
import auth
from profiles import profile


@click.group()
def insighta():
    pass


insighta.add_command(auth.login)
insighta.add_command(auth.logout)
insighta.add_command(auth.whoami)
insighta.add_command(profile)


if __name__ == "__main__":
    insighta()
