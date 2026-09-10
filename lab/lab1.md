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

quest 4: 
after running : dvc add data, DVC updated the .gitignore file and added the data/ folder to it. This means Git will not track or upload the actual dataset to GitHub.
The reason is that the dataset is large, so DVC manages the data files instead of Git. Git only keeps the small DVC pointer file.

qeust 5: 
After running: dvc add data, a file called: data.dvc was created.
This file does not contain the actual dataset. It contains information about the data/ folder, such as its hash, size, number of files, and path.
The hash is used by DVC to identify the exact version of the dataset. So data.dvc acts like a pointer to the version of the data that should be used with the current Git version of the project.

quest 6: 
On GitHub, I can see the project files, source code, configuration files, the lab folder, and the 'data.dvc' file.
The actual Food-11 dataset is not stored on GitHub because the 'data/' folder is ignored by Git. Instead, Git stores the 'data.dvc' file, which points to the correct version of the dataset.
For this lab, I used the local DVC remote solution, so the actual dataset is stored in my local DVC storage folder instead of DagsHub.

quest 7 :
After cloning the GitHub repository into a new folder, I could see the project files and the 'data.dvc' file, but the actual Food-11 dataset was not present.
This is because Git stores the source code and the DVC pointer file, while DVC manages the actual dataset.
To retrieve the data, I ran:
```bash
dvc pull
After running this command, the Food-11 dataset was restored from my configured local DVC remote.