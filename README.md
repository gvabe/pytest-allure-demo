# Python + Pytest + Allure + Jenkins (Windows)

This project runs four passing tests without a browser or external website.
Git stores the files, GitHub hosts the repository, Jenkins retrieves and runs it,
and Allure turns the test results into a report.

## 1. Open the project and run locally

Open THIS folder in VS Code (File > Open Folder). You should see requirements.txt,
Jenkinsfile, and tests directly inside it. Choose Terminal > New Terminal and use
PowerShell. All local and Git commands below go in that terminal.

First check Python (Java does not replace Python):

```powershell
py -3 --version
git --version
java -version
allure --version
```

If Python is missing, install Python 3.12 or newer from python.org with pip and the
Python launcher enabled, then reopen VS Code. If `py` fails but `python --version`
works, replace `py -3` with `python` here and in Jenkinsfile. A Windows Store alias
is not a working Python installation. Use the real interpreter path if needed.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest tests -v --alluredir=allure-results --clean-alluredir
allure serve allure-results
```

Expect `4 passed`. Allure opens a local report. Press Ctrl+C to stop its server.
No environment activation is needed, so PowerShell execution-policy changes are
unnecessary. In VS Code, use Python: Select Interpreter to select .venv if desired.
The Python Allure adapter creates result files; the Allure command-line tool or
Jenkins plugin generates the HTML report. This walkthrough targets Allure 2's
Java-based command-line tool, as used by the Jenkins Allure plugin.

## 2. Initialize Git and push to GitHub

On GitHub create a repository named `pytest-allure-demo`. Leave README, license,
and .gitignore unchecked so the remote repository starts empty. Choose public for
a simple demo, or private with Jenkins credentials configured in step 3.

Run from this project folder, replacing YOUR-USERNAME:

```powershell
git init
git branch -M main
git add .
git commit -m "Add Pytest Allure Jenkins demo"
git remote add origin https://github.com/YOUR-USERNAME/pytest-allure-demo.git
git push -u origin main
```

If commit asks for an identity, set your own details locally, then retry commit:

```powershell
git config user.name "Your Name"
git config user.email "YOUR-EMAIL"
```

Complete the browser sign-in if Git asks. GitHub account passwords are not used
for Git HTTPS authentication. For an existing `origin`, inspect `git remote -v`
and use `git remote set-url origin YOUR-REPOSITORY-URL` if necessary.

Refresh GitHub: tests/test_demo.py, requirements.txt, .gitignore, Jenkinsfile,
and this README should be visible. .venv and generated reports should be absent.

## 3. Prepare the Windows Jenkins executor

Jenkins runs under its own account, often a Windows service account. Software
available to your VS Code terminal may not be available to that account.
On the Windows machine executing the job, ensure Python, Git and Java are usable
by Jenkins. Restart the Jenkins service/agent after changing its PATH. If Python
is installed only for your user, install it for the executor account/all users,
or change `py -3` in Jenkinsfile to a quoted absolute Python executable path.
For example: `bat '"C:\\Python312\\python.exe" -m venv .venv'`.
The executor also needs access to GitHub and the Python package index.

Manage Jenkins > Nodes > select your Windows node > Configure > Labels: add
`windows`, then save. It must be online with an available executor. If Jenkins
runs on Linux or in Docker, attach a Windows agent for this Windows Jenkinsfile.

Manage Jenkins > Plugins: verify Git, Pipeline and Allure are installed.
Manage Jenkins > Tools (older versions: Global Tool Configuration): configure
an Allure Commandline installation. For this example use the Jenkins plugin's
supported Allure 2 command line. You can use its automatic installer or point to
a preinstalled Allure home on the executor. Verify Java is available there too.
Installing the plugin alone does not configure the report-generation tool.

## 4. Recommended: Pipeline job

If your previous job had no Source Code Management or Build Steps sections, it
may have been a Pipeline job. This is normal: Pipeline uses a Jenkinsfile for its
commands. Freestyle exposes checkout and build steps as separate form sections.
You can check your existing job's Configure page for a Pipeline section, or simply
create this new job:

1. Dashboard > New Item > name `pytest-allure-demo` > Pipeline > OK.
2. Configure > Pipeline > Definition: **Pipeline script from SCM**.
3. SCM: **Git**. Repository URL: your GitHub HTTPS repository URL.
4. Public repository: credentials may remain None. Private repository: Add a
   Jenkins username/password credential with your GitHub username and an access
   token as the password; grant the token read access to this repository, then
   select that credential. Never put tokens in repository files or URLs.
5. Branch Specifier: `*/main`. Script Path: `Jenkinsfile` (case matters).
6. Save > Build Now > select build number > Console Output.

Expected stages: Checkout, Install dependencies, Run tests. The console should
show `4 passed`. Open **Allure Report** on the build/job page. You should see four
successful tests, calculator steps, and Actual result attachments.

The Jenkinsfile starts with a clean job workspace, checks out GitHub, creates its
own virtual environment and runs tests. Its test-stage `post { always { ... } }`
publishes Allure even when a test fails. Test failure still fails the build.
The result folder configured for Allure is `allure-results`, not `allure-report`.
You do not run `allure serve` inside Jenkins.

If the Allure step needs a specific configured tool, open your job's Pipeline
Syntax > Snippet Generator > allure, select the tool, generate the snippet and
replace only the `allure ...` line in Jenkinsfile. Commit and push the change.

## 5. Alternative: Freestyle job

Use this instead of step 4 if you prefer form fields. Jenkinsfile is ignored.

1. New Item > a different name > Freestyle project > OK.
2. Restrict where this project can be run: label expression `windows`.
3. Source Code Management > Git: same URL, credentials and `*/main` branch.
4. Build Steps > Add build step > Execute Windows batch command. Paste:

```bat
py -3 -m venv .venv
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m pytest tests -v --alluredir=allure-results --clean-alluredir
exit /b %ERRORLEVEL%
```

5. Post-build Actions > Add post-build action > Allure Report. Results Path:
   `allure-results`. Select the configured command-line tool if requested. In
   Advanced, choose the report policy **Always**, including failed builds.
6. Save > Build Now > Console Output, then open Allure Report.

If a Freestyle job has no Git option, check the Git plugin installation. If you
are configuring a folder or Multibranch Pipeline container, create the ordinary
Pipeline or Freestyle job described above for this demo.

## 6. Make a change and run again

Edit a test, save it, then run:

```powershell
git add tests/test_demo.py
git commit -m "Update demo tests"
git push
```

Click Build Now in Jenkins again. A push alone does not trigger this job until
you separately configure a webhook or SCM polling.

To see a deliberate failure locally:

```powershell
$env:DEMO_FAIL = "1"
.\.venv\Scripts\python.exe -m pytest tests -v --alluredir=allure-results --clean-alluredir
Remove-Item Env:DEMO_FAIL
allure serve allure-results
```

Expect 3 passed and 1 failed. For Jenkins, temporarily add
`environment { DEMO_FAIL = '1' }` immediately below the agent line in Jenkinsfile,
commit, push, and Build Now. The build fails but Allure still publishes. Remove
that environment line, commit and push to restore four passing tests.

## Troubleshooting

* Waiting for an executor: check the `windows` label, node status and executors.
* `py` not recognized: fix Python availability for the Jenkins account, or use an
  absolute interpreter path. Your personal terminal's PATH is separate.
* Cannot find Jenkinsfile: check repository URL, main branch, spelling, and push.
* Checkout/authentication error: verify Jenkins credentials and repository access.
* `No module named allure`: install requirements with the same .venv Python used
  to run pytest; the package is `allure-pytest` and the import is `allure`.
* Empty report: inspect Console Output first. Tests must actually execute and
  create allure-results in the workspace before a report can be generated.
* Allure/Java tool error: check Manage Jenkins > Tools and the executor's Java.

Official references:
* https://www.jenkins.io/doc/book/pipeline/getting-started/
* https://www.jenkins.io/doc/pipeline/tour/running-multiple-steps/
* https://allurereport.org/docs/pytest/
* https://allurereport.org/docs/integrations-jenkins/
