# comp-data_group-project

Hi all, I set up the github repo to collaborate on the comp-data group project.

We can work on separate files on separate machines, then push the changes on this repository.

## Set up the repository locally by cloning the repo

```bash
git clone https://github.com/amirdjalali/comp-data_group-project.git
cd your-repo
```

## Set your identity (first-time Git users)

```bash
git config --global user.name "Your Name"
git config --global user.email "you@email.com"
```

## How to make changes

Always pull latest changes first. ```pull``` synchronizes all the changes locally.

```bash
git pull origin main

Make changes, then stage and commit. Commit saves changes on your local machine.

```bash
# tell git which files have changed. To include all files, use
git add .

# commit saves the changes on your local git repo, with a description of the changes
git commit -m "Add: description of what you did"
```

Push your changes. Uploads changes to github so everyone can see them.

```bash
git push origin main
```

Then open a Pull Request (PR) on GitHub so teammates can review before merging into main.

# Good Collaboration Habits

- Pull before you push — always sync with main before starting work.
- Write clear commit messages — explain what and why
- Use Issues — track bugs and features via GitHub Issues
- Communicate in PRs — leave comments and request specific reviewers

# Quick Reference: Daily Workflow

```bash
# Start of every work session — always pull first!
git pull origin main

# Do your work on your files...

# Save and push
git add .
git commit -m "Brief description of what you changed"
git push origin main
```
