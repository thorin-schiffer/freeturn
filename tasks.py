import invoke


@invoke.task
def deploy(context, repo=True):
    if repo:
        context.run("git push origin && git push heroku develop:master")
    else:
        context.run("git push heroku develop:master")
