import click
from cryptography.fernet import Fernet
import datetime
import githubapi
from github import GithubException
import yaml


with open('githubapi_config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

permanent_key = b'M4A2fxPIIRxj6f7dGeDVBnnlILbUNWPMtYlS1lmvxcM='
fernet = Fernet(permanent_key)


@click.command()
@click.option('-U', '--username', required=False, help='GitHub username')
@click.option('-P', '--password', required=False, help='GitHub password')
def main(username, password):
    params_dict = {
        'username': username,
        'password': password
    }

    # check credentials file. Use creds from it if exists, else exit
    if not params_dict['username'] or not params_dict['password']:
        try:
            cred_file = open(config.get('cred_file'), 'r')
            lines = cred_file.readlines()
            params_dict['username'] = fernet.decrypt(lines[0][2:-2].encode()).decode()
            params_dict['password'] = fernet.decrypt(lines[1][2:-1].encode()).decode()
            print('\nNo username/password added, using last successfully authorization credentials...\n')
        except OSError:
            print('\nERROR: No username/password added and no saved credentials\n')
            exit(2)

    # first action before authorization - read all user repos
    try:
        instance = githubapi.create_github_instance(params_dict['username'], params_dict['password'])
        githubapi.get_all_user_repositories(instance)
        log_file = open(config.get('log_file'), 'a')
        log_file.write(str(datetime.datetime.now())
                       + ' | Successfully authorized as '
                       + params_dict['username']
                       + '\n')
        log_file.close()

        cred_file = open(config.get('cred_file'), 'w')
        cred_file.write(str(fernet.encrypt(params_dict['username'].encode()))
                        + '\n'
                        + str(fernet.encrypt(params_dict['password'].encode())))
        cred_file.close()

        # optional operations


    except GithubException:
        log_file = open(config.get('log_file'), 'a')
        log_file.write(str(datetime.datetime.now())
                       + ' | Authorisation error for user '
                       + params_dict['username']
                       + '\n')
        log_file.close()
        print('Authorisation error! Check username/password.')


if __name__ == "__main__":
    main()
