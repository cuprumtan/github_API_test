import click
import githubapi


@click.command()
@click.option('-U', '--username', required=False, help='GitHub username')
@click.option('-P', '--password', required=False, help='GitHub password')
def main(username, password):
    params_dict = {
        'username': username,
        'password': password
    }
    instance = githubapi.create_github_instance(params_dict['username'], params_dict['password'])
    githubapi.get_all_user_repositories(instance)


if __name__ == "__main__":
    main()
