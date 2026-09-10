quest 1:
pyproject.toml : information or configuration about the Python project and dependencies
.python-version :  Python version the project uses
README.md : documentation about the project
.gitignore : files Git should ignore

quest 2: 
.dvc/ : contains DVC configuration/internal project information.
.dvcignore : tells DVC which files it should ignore.
The configuration files needed to reproduce the project are committed to Git, while DVC cache/temp data isn't.

quest 3: 
onfiguration is stored outside the repository, local configuration can be used for machine-specific/secrets, and credentials/passwords/tokens should never be committed to GitHub
For this lab, I used Solution 1 from the updated lab instructions:
a local DVC remote outside the Git repository.