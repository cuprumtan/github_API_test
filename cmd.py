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
# repo level
# get_all_user_repositories
@click.option('-L', '--repolist', required=False, is_flag=True, help='Show current user repositories')
@click.option('--privacy', required=False, is_flag=True, help='Show repositories privacy')
@click.option('--languages', required=False, is_flag=True, help='Show repositories languages')
# create_new_github_repository
@click.option('-C', '--createrepo', required=False, help='Create new repository')
# delete_github_repository
@click.option('-D', '--deleterepo', required=False, help='Delete new repository')
# get_repository_contents
@click.option('-T', '--repocontents', required=False, help='Show repository contents')
@click.option('--recursively', required=False, is_flag=True, help='Show repository contents recursively')
# edit_repository_name
@click.option('-R', '--renamerepo', required=False, help='Rename repository. Usage: -R REPO,NEW_NAME')
# edit_repository_privacy
@click.option('-P', '--repoprivacy', required=False, help='Edit repository privacy. '
                                                          + 'Usage: -P REPO,PRIVACY where PRIVACY = [T|F]. '
                                                          + 'T for private, F for public.')
def main(username,
         password,
         repolist,
         privacy,
         languages,
         createrepo,
         deleterepo,
         repocontents,
         recursively,
         renamerepo,
         repoprivacy):
    params_dict = {
        'username': username,
        'password': password,
        'repolist': repolist,
        'privacy': privacy,
        'languages': languages,
        'createrepo': createrepo,
        'deleterepo': deleterepo,
        'repocontents': repocontents,
        'recursively': recursively,
        'renamerepo': renamerepo,
        'repoprivacy': repoprivacy
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
        githubapi.count_all_user_repositories(instance)
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
        if params_dict['repolist']:
            print()
            githubapi.get_all_user_repositories(instance, params_dict['privacy'], params_dict['languages'])
        if params_dict['createrepo']:
            print()
            githubapi.create_new_github_repository(instance, params_dict['createrepo'])
            print('Successfully created new repo '
                  + params_dict['createrepo']
                  + '\n')
        if params_dict['deleterepo']:
            print()
            githubapi.delete_github_repository(instance, params_dict['deleterepo'])
            print('Successfully deleted repo '
                  + params_dict['deleterepo']
                  + '\n')
        if params_dict['repocontents']:
            print()
            githubapi.get_repository_contents(instance, params_dict['repocontents'], params_dict['recursively'])
        if params_dict['renamerepo']:
            print()
            githubapi.edit_repository_name(instance,
                                           params_dict['renamerepo'].split(',')[0],
                                           params_dict['renamerepo'].split(',')[1])
            print('Successfully renamed repo '
                  + params_dict['renamerepo'].split(',')[0]
                  + ' to '
                  + params_dict['renamerepo'].split(',')[1]
                  + '\n')
        if params_dict['repoprivacy']:
            print()
            githubapi.edit_repository_privacy(instance,
                                              params_dict['repoprivacy'].split(',')[0],
                                              True if params_dict['repoprivacy'].split(',')[1] == 'T' else False)
            print('Successfully made repo '
                  + params_dict['repoprivacy'].split(',')[0]
                  + ' '
                  + 'private' if params_dict['repoprivacy'].split(',')[1] == 'T' else 'public'
                  + '\n')

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
