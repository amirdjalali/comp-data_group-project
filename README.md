# comp-data_group-project

Hi all, I set up the github repo to collaborate on the comp-data group project.

To set up the repository locally, clone the repo

```bash
git clone https://github.com/amirdjalali/comp-data_group-project.git
cd your-repo
```
Set your identity (first-time Git users)

```bash
git config --global user.name "Your Name"
git config --global user.email "you@email.com"
```

Establish a Branching Workflow

A common pattern is feature branches.  Always pull latest changes first

```bash
git pull origin main

Create a new branch for your work

```bash
git checkout -b feature/your-feature-name
```

Make changes, then stage and commit

```bash
git add .
git commit -m "Add: description of what you did"
```

Push your branch

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request (PR) on GitHub so teammates can review before merging into main.
