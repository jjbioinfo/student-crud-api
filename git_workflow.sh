#!/usr/bin/env bash
# Copy ONE command at a time. Stop if a command fails.
# Git is already initialized on main in this folder. No git init is needed.

# 1. Enter the project.
cd /Users/JJOHN41/Documents/my_learning/euron_super30/assignment/october/2_student_CRUD_API

# 2. Set the author identity for this repository.
git config user.name "jjbioinfo"

git config user.email "jibinbioinfo@gmail.com"

# 3. Check and select the files. .env is excluded by .gitignore.
git status

git add .

# Check that .env is NOT staged before committing.
git status

git commit -m "Build Student CRUD API with FastAPI and Supabase"

# 4. BROWSER STEP: create an empty public repository at https://github.com/new
# Owner: jjbioinfo | Name: student-crud-api
# Do not add a README, .gitignore, or license in the browser.
# If the repository already exists, inspect it before continuing; do not overwrite history.

# 5. Connect the remote once, then upload.
git remote add origin https://github.com/jjbioinfo/student-crud-api.git

git push -u origin main

# Later updates only need: git add . / git commit -m "Your message" / git push
# Repository: https://github.com/jjbioinfo/student-crud-api
