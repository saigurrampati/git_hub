""" Our business logic  in this views """
from django.shortcuts import render
from github import Github
from django.http import HttpResponseRedirect


# Create your views here

def login_page(request):
    """ This is for our home page """
    return render(request, 'gitapp/login.html')


open_git = ""


def credits(request):
    """For all required credentials"""
    if request.method == 'POST':
        global open_git
        open_git = Github(request.POST["token"])
        user_name = request.POST['username']
        user = open_git.get_user(user_name)
        request.session["username"] = user_name
        repo_list = user.get_repos()
        total = []
        for i in repo_list:
            total.append(i)
        return user_name, user, total


def repository_list(request):
    """ This view for the repositories in github"""
    # import pdb
    # pdb.set_trace()
    user_name, user, total = credits(request)
    return render(request, 'gitapp/repository.html', {'total': total, 'name': user_name})


def logout_page(request):
    """This is for logout function to clear the session"""
    del request.session['username']
    return HttpResponseRedirect("/gitapp/login/")


def reposit_details(request, name):
    """This is for contents in repository"""
    username = open_git.get_user().login
    my_repo = open_git.get_repo("{}/{}".format(username, name))
    my_branches = list(my_repo.get_branches())
    if request.method == "POST":
        # import pdb
        # pdb.set_trace()
        contents = my_repo.get_contents("", ref=request.POST["source"])
        pulls = my_repo.get_pulls(state='open', sort='created', base=request.POST["source"])
    else:
        contents = my_repo.get_contents("", ref="master")
        pulls = my_repo.get_pulls(state='open', sort='created', base="master")
    files = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            files.extend(my_repo.get_contents(file_content.path))
        else:
            files.append(file_content)
    return render(request, "gitapp/reposit_details.html",
                  {"branches": my_branches, "files": files, "repo": my_repo, "pulls": pulls})


def my_branch(request, name):
    """ for get the list of all branches"""
    username = open_git.get_user().login
    my_repo = open_git.get_repo("{}/{}".format(username, name))
    my_branches = list(my_repo.get_branches())
    return my_branches


def data(request, name):
    """View for uploading the data """
    my_branches = my_branch(request, name)
    return render(request, "gitapp/create_branch.html", {"name": name, "branches": my_branches})


def create_branch(request, name):
    """ Creating a new  branch  """
    if request.method == "POST":
        # import pdb
        # pdb.set_trace()
        repo_name = name
        source_branch = request.POST["source"]
        target_branch = request.POST["new_branch"]
        repo = open_git.get_user().get_repo(repo_name)
        new_commit = repo.get_branch(source_branch)
        repo.create_git_ref(ref='refs/heads/{}'.format(target_branch), sha=new_commit.commit.sha)
        return reposit_details(request, name)

        # return render(request, "gitapp/reposit_details.html",
        #               {"name": name, "repo": repo, "branches": repo.get_branches(), "files": files})
    else:
        return render(request, "gitapp/create_branch.html", {"name": name})


def file_details(request, name):
    """From html giving file name"""
    repo_name = name
    my_branches = my_branch(request, name)
    repo = open_git.get_user().get_repo(repo_name)
    return render(request, "gitapp/file.html", {"name": name, "branches": my_branches})


def file(request, name):
    """For creating a file """
    # import pdb
    # pdb.set_trace()
    username = open_git.get_user().login
    my_repo = open_git.get_repo("{}/{}".format(username, name))
    my_branches = list(my_repo.get_branches())
    if request.method == "POST":
        repo = open_git.get_user().get_repo(name)
        file_name = request.FILES["file"]
        content = file_name.read()
        repo.create_file(file_name.name, request.POST["msg"], content, branch=request.POST["source"])
        return reposit_details(request, name)


    else:
        return render(request, "gitapp/file.html", {"name": name, "branches": my_branches})


def pull_req(request, name):
    """To create a pull request"""
    username = open_git.get_user().login
    my_branches = my_branch(request, name)
    return render(request, "gitapp/pull_request.html", {"name": name, "branches": my_branches})


def pull_details(request, name):
    """Getting PR details from html"""
    repo = open_git.get_user().get_repo(name)
    if request.method == "POST":
        title = request.POST["title"]
        body = request.POST["body"]
        source_branch = request.POST["source"]
        target_branch = request.POST["target"]
        new_pr = repo.create_pull(title=title, body=body, head=source_branch, base=target_branch)
        return reposit_details(request, name)
    else:
        return pull_req(request, name)


def merging(request, name):
    """Merging two branches"""
    my_branches = my_branch(request, name)
    return render(request, "gitapp/merging.html", {"branches": my_branches, "name": name})


def merge(request, name):
    """Getting data from html to merge"""
    username = open_git.get_user().login
    my_repo = open_git.get_repo("{}/{}".format(username, name))
    if request.method == "POST":
        try:
            source_branch = my_repo.get_branch(request.POST["source"])
            target_branch = my_repo.get_branch(request.POST["target"])
            merge_to_master = my_repo.merge(source_branch.name, target_branch.name,
                                            "merge to {}".format(target_branch.name))
        except Exception as ex:
            print(ex)
        return reposit_details(request, name)
    else:
        return merging(request, name)


def del_branch(request, name):
    """for delete particular branch"""
    my_branches = my_branch(request, name)
    return render(request, "gitapp/del_branch.html", {"branches": my_branches, "name": name})


def delete(request, name):
    """for deleting that particular branch """
    repo = open_git.get_user().get_repo(name)
    my_branches = my_branch(request, name)
    contents = repo.get_contents("", ref="master")
    pulls = repo.get_pulls(state='open', sort="created", base="master")
    files = []
    if request.method == "POST":
        delete_branch = request.POST["source"]
        ref = repo.get_git_ref("heads/{}".format(delete_branch))
        ref.delete()
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                files.extend(repo.get_contents(file_content.path))
            else:
                files.append(file_content)
        return render(request, "gitapp/reposit_details.html",
                      {"branches": my_branches, "files": files, "repo": repo, "pulls": pulls})
    else:
        return del_branch(request, name)
