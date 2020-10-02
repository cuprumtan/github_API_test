from github import Github


def create_github_instance(username, password):
    github_instance = Github(username, password)
    return github_instance


def count_all_user_repositories(github_instance, private=False, languages=False):
    github_repositories = github_instance.search_repositories(query='user:' + github_instance.get_user().login)
    print('===== USER '
          + github_instance.get_user().login
          + ', TOTAL '
          + str(github_repositories.totalCount)
          + ' repos')


def get_all_user_repositories(github_instance, private=False, languages=False):
    github_repositories = github_instance.search_repositories(query='user:' + github_instance.get_user().login)
    print('===== USER '
          + github_instance.get_user().login
          + ' REPOSITORIES:')
    github_repositories_dict = dict((repo.name, ('PRIVATE' if repo.private else 'PUBLIC', repo.language))
                                    for repo in github_repositories)
    if private and languages:
        for repo in sorted(github_repositories_dict.items()):
            print('--- '
                  + repo[0]
                  + ' ('
                  + str(repo[1][0])
                  + ') '
                  + '\n    main langueage: '
                  + str(repo[1][1]))
    if private and not languages:
        for repo in sorted(github_repositories_dict.items()):
            print('--- '
                  + repo[0]
                  + ' ('
                  + str(repo[1][0])
                  + ') ')
    if not private and languages:
        for repo in sorted(github_repositories_dict.items()):
            print('--- '
                  + repo[0]
                  + '\n    main langueage: '
                  + str(repo[1][1]))
    if not private and not languages:
        for repo in sorted(github_repositories_dict.items()):
            print('--- '
                  + repo[0])


def create_new_github_repository(github_instance, github_repository_name):
    github_user = github_instance.get_user()
    github_user.create_repo(github_repository_name)


def delete_github_repository(github_instance, github_repository_name):
    github_repository = github_instance.get_repo(
        full_name_or_id=github_instance.get_user().login + '/' + github_repository_name)
    github_repository.delete()


def get_repository_contents(github_instance, github_repository_name, recursively=True):
    github_repository = github_instance.get_repo(
        full_name_or_id=github_instance.get_user().login + '/' + github_repository_name)
    github_repository_contents = github_repository.get_contents("")
    print('===== REPO ' + github_repository_name + ' CONTENTS:')
    if recursively:
        while github_repository_contents:
            file_content = github_repository_contents.pop(0)
            if file_content.type == "dir":
                github_repository_contents.extend(github_repository.get_contents(file_content.path))
            else:
                print(file_content.path)
    else:
        for file_content in github_repository_contents:
            if file_content.type == "dir":
                print(file_content.path + '/')
            else:
                print(file_content.path)


def edit_repository_name(github_instance, github_repository_name, new_github_repository_name):
    github_repository = github_instance.get_repo(
        full_name_or_id=github_instance.get_user().login + '/' + github_repository_name)
    github_repository.edit(name=new_github_repository_name)


def edit_repository_privacy(github_instance, github_repository_name, privacy):
    github_repository = github_instance.get_repo(
        full_name_or_id=github_instance.get_user().login + '/' + github_repository_name)
    github_repository.edit(private=privacy)


def get_repository_files_by_type(github_instance, github_repository_name, type):
    github_repository = github_instance.get_repo(
        full_name_or_id=github_instance.get_user().login + '/' + github_repository_name)
    github_repository_contents = github_repository.get_contents("")
    print('===== REPO ' + github_repository_name + ' ' + type + ' FILES:')
    while github_repository_contents:
        file_content = github_repository_contents.pop(0)
        if file_content.type == "dir":
            github_repository_contents.extend(github_repository.get_contents(file_content.path))
        else:
            if ('.' + type.lower()) == file_content.path.lower()[-(len(type) + 1):]:
                print(file_content.path)


def create_new_repo_file_from_cmd(github_instance, github_repository_name, file_path, file_content):
    github_repository = github_instance.get_repo(
        full_name_or_id=github_instance.get_user().login + '/' + github_repository_name)
    github_repository.create_file(path=file_path,
                                  message='Create new file ' + file_path,
                                  content=file_content)


def create_new_repo_file_from_file(github_instance, github_repository_name, file_path, my_file_path):
    github_repository = github_instance.get_repo(
        full_name_or_id=github_instance.get_user().login + '/' + github_repository_name)
    file = open(my_file_path)
    file_content = file.read()
    file.close()
    github_repository.create_file(path=file_path,
                                  message='Create new file ' + file_path,
                                  content=file_content)


def delete_file_from_repo(github_instance, github_repository_name, file_path):
    github_repository = github_instance.get_repo(
        full_name_or_id=github_instance.get_user().login + '/' + github_repository_name)
    file_contents = github_repository.get_contents(file_path)
    github_repository.delete_file(path=file_path,
                                  message='Delete file ' + file_path,
                                  sha=file_contents.sha)
