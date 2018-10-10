import invoke


@invoke.task
def deploy(context):
    context.run("git push heroku develop:master")
