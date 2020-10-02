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
@click.option('-u', '--username', required=False, help='GitHub username')
@click.option('-p', '--password', required=False, help='GitHub password')
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
                                                          + 'T for private, F for public')
#get_repository_files_by_type
@click.option('-F', '--findinrepo', required=False, help='Find files in repo by type. Usage: -F REPO,TYPE')
# files level
@click.option('--repo', required=False, help='Repository name')
# create_new_repo_file_from_cmd
@click.option('-c', '--createfile', required=False, help='Create new file in repository')
@click.option('--content', required=False, help='File content. Usage: --content "WRITE CONTENT HERE"')
# create_new_repo_file_from_file
@click.option('-l', '--loadfile', required=False, help='Load new file in repository')
@click.option('--path', required=False, help='File path')
# delete_file_from_repo
@click.option('-d', '--deletefile', required=False, help='Delete file from repository')
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
         repoprivacy,
         findinrepo,
         repo,
         createfile,
         content,
         loadfile,
         path,
         deletefile):
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
        'repoprivacy': repoprivacy,
        'findinrepo': findinrepo,
        'repo': repo,
        'createfile': createfile,
        'content': content,
        'loadfile': loadfile,
        'path': path,
        'deletefile': deletefile
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
            try:
                print()
                githubapi.get_all_user_repositories(instance, params_dict['privacy'], params_dict['languages'])
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Loaded all repositories for user '
                               + params_dict['username']
                               + (' recursively' if params_dict['privacy'] else ' ')
                               + (' with languages' if params_dict['languages'] else ' ')
                               + '\n')
                log_file.close()
            except GithubException:
                print('ERROR')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Error while loading all repositories for user '
                               + params_dict['username']
                               + (' recursively' if params_dict['privacy'] else ' ')
                               + (' with languages' if params_dict['languages'] else ' ')
                               + '\n')
                log_file.close()
                exit(11)
        if params_dict['createrepo']:
            try:
                print()
                githubapi.create_new_github_repository(instance, params_dict['createrepo'])
                print('Successfully created new repo '
                      + params_dict['createrepo']
                      + '\n')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Created new repository '
                               + params_dict['createrepo']
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
            except GithubException:
                print('ERROR')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Error while creating new repository '
                               + params_dict['createrepo']
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
                exit(11)
        if params_dict['deleterepo']:
            try:
                print()
                githubapi.delete_github_repository(instance, params_dict['deleterepo'])
                print('Successfully deleted repo '
                      + params_dict['deleterepo']
                      + '\n')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Deleted repository '
                               + params_dict['deleterepo']
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
            except GithubException:
                print('ERROR')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Error while deleting repository '
                               + params_dict['deleterepo']
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
                exit(11)
        if params_dict['repocontents']:
            try:
                print()
                githubapi.get_repository_contents(instance, params_dict['repocontents'], params_dict['recursively'])
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Loaded repository '
                               + params_dict['repocontents']
                               + ' contents '
                               + ('recursively ' if params_dict['recursively'] else ' ')
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
            except GithubException:
                print('ERROR')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Error while loading repository '
                               + params_dict['repocontents']
                               + ' contents '
                               + ('recursively ' if params_dict['recursively'] else ' ')
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
                exit(11)
        if params_dict['renamerepo']:
            try:
                print()
                githubapi.edit_repository_name(instance,
                                               params_dict['renamerepo'].split(',')[0],
                                               params_dict['renamerepo'].split(',')[1])
                print('Successfully renamed repo '
                      + params_dict['renamerepo'].split(',')[0]
                      + ' to '
                      + params_dict['renamerepo'].split(',')[1]
                      + '\n')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Renamed repository '
                               + params_dict['renamerepo'].split(',')[0]
                               + ' to '
                               + params_dict['renamerepo'].split(',')[1]
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
            except GithubException:
                print('ERROR')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Error while renaming repository '
                               + params_dict['renamerepo'].split(',')[0]
                               + ' to '
                               + params_dict['renamerepo'].split(',')[1]
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
                exit(11)
        if params_dict['repoprivacy']:
            try:
                print()
                githubapi.edit_repository_privacy(instance,
                                                  params_dict['repoprivacy'].split(',')[0],
                                                  True if params_dict['repoprivacy'].split(',')[1] == 'T' else False)
                print('Successfully made repo '
                      + params_dict['repoprivacy'].split(',')[0]
                      + ' '
                      + ('private' if params_dict['repoprivacy'].split(',')[1] == 'T' else 'public')
                      + '\n')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Setted repository '
                               + params_dict['repoprivacy'].split(',')[0]
                               + ' to '
                               + ('private' if params_dict['repoprivacy'].split(',')[1] == 'T' else 'public')
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
            except GithubException:
                print('ERROR')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Error while setting repository '
                               + params_dict['repoprivacy'].split(',')[0]
                               + ' to '
                               + ('private' if params_dict['repoprivacy'].split(',')[1] == 'T' else 'public')
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
                exit(11)
        if params_dict['findinrepo']:
            try:
                print()
                githubapi.get_repository_files_by_type(instance,
                                                       params_dict['findinrepo'].split(',')[0],
                                                       params_dict['findinrepo'].split(',')[1])
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Found '
                               + params_dict['findinrepo'].split(',')[1]
                               + ' files in repository '
                               + params_dict['findinrepo'].split(',')[0]
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
            except GithubException:
                print('ERROR')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Error while searching '
                               + params_dict['findinrepo'].split(',')[1]
                               + ' files in repository '
                               + params_dict['findinrepo'].split(',')[0]
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
                exit(11)
        if params_dict['repo'] and params_dict['createfile'] and params_dict['content']:
            try:
                print()
                githubapi.create_new_repo_file_from_cmd(instance,
                                                        params_dict['repo'],
                                                        params_dict['createfile'],
                                                        params_dict['content'])
                print('Successfully create file '
                      + params_dict['createfile']
                      + ' in repo '
                      + params_dict['repo']
                      + '\n')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Created file '
                               + params_dict['createfile']
                               + ' in repository '
                               + params_dict['repo']
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
            except GithubException:
                print('ERROR')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Error while creating file '
                               + params_dict['createfile']
                               + ' in repository '
                               + params_dict['repo']
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
                exit(11)
        if params_dict['repo'] and params_dict['loadfile'] and params_dict['path']:
            try:
                print()
                githubapi.create_new_repo_file_from_file(instance,
                                                         params_dict['repo'],
                                                         params_dict['loadfile'],
                                                         params_dict['path'])
                print('Successfully loaded file '
                      + params_dict['loadfile']
                      + ' in repo '
                      + params_dict['repo']
                      + '\n')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Loaded file '
                               + params_dict['loadfile']
                               + ' into repository '
                               + params_dict['repo']
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
            except GithubException:
                print('ERROR')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Error while loading file '
                               + params_dict['loadfile']
                               + ' into repository '
                               + params_dict['repo']
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
                exit(11)
        if params_dict['repo'] and params_dict['deletefile']:
            try:
                print()
                githubapi.delete_file_from_repo(instance,
                                                params_dict['repo'],
                                                params_dict['deletefile'])
                print('Successfully deleted file '
                      + params_dict['deletefile']
                      + ' from repo '
                      + params_dict['repo']
                      + '\n')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Deleted file '
                               + params_dict['deletefile']
                               + ' from repository '
                               + params_dict['repo']
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
            except GithubException:
                print('ERROR')
                log_file = open(config.get('log_file'), 'a')
                log_file.write(str(datetime.datetime.now())
                               + ' | Error while deleting file '
                               + params_dict['deletefile']
                               + ' from repository '
                               + params_dict['repo']
                               + ' for user '
                               + params_dict['username']
                               + '\n')
                log_file.close()
                exit(11)

    except GithubException:
        log_file = open(config.get('log_file'), 'a')
        log_file.write(str(datetime.datetime.now())
                       + ' | Authorisation error for user '
                       + params_dict['username']
                       + '\n')
        log_file.close()
        print('Authorisation error! Check username/password.')
        exit(11)


if __name__ == "__main__":
    main()
