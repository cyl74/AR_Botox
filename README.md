# Augmented Reality Botox Injection Reference - ARBIR

Our project allows for real-time patient face scanning with region and injection point overlay to aid in Botox surgery. It gives the users options on which injection points to show, a reference image which creates landmarks on a 2D image, and a database full of medical information.


## Video/demo/GIF
[Demo video can be found here](https://drive.google.com/file/d/1AEQx9qpp4w2zriho360IgaxnaJ402W2C/view?t=4)


## Table of Contents
1. [Demo](#demo)

2. [Installation](#installation)

3. [Reproducing this project](#repro)

4. [Guidance](#guide)


<a name="demo"></a>
## 1. Example demo

To use the live AR feed of our app, the user can select from a list of injection points on the right-hand side, organized by face area and region (example: Eye --> Orbital Oculi). This will update the video to include a draw region, along with a small dot where the injeciton should take place, allowing for needle guidance. Multiple points, from different areas can be selected at the same time. There are five tabs in the patient information column, the first of which allows the user to upload someone's image for reference, in which all of the regions are divided for insight. The details tab shows information (name, contact, date of birth, medical history) of the selected patient, which can be found in the search tab. The add patient tab is self-explanatory as it just provides an interface to add to the database, while the appointments tab shows upcoming and priors appointments for a specified patient, along with the option to schedule a new one.


### What to find where

Brief explanations of important files:

```bash
repository
├── ARbotox                                     ## Source code of the package itself
    ├── data                                    ## Directory containing our data
        ├── inputs                              ## Botox-specific data (injections, regions, etc.)
        ├── mp_pointData                        ## Names/outcomes/side effects of specific injection points
        ├── patientData                         ## Patient-specific data (patients, clinicians, etc.)
        ├── mapped_landmarks_to_regions.csv     ## Face landmark data mapping to injection points
    ├── db_api                                  ## Database-specific scripts
        ├── Id_fix.py                           ## Script to fix auto-increment issues
        ├── createDatabase.sql                  ## Script to create and load the database
        ├── db.py                               ## Database schema
        ├── exampleUse.py                       ## Example queries for the DB API
    ├── notebook                                ## Tests for the 2D and 3D reference scans
    ├── resources                               ## Example images used for reference
    ├── src                                     ## Scripts for face mapping and landmark calculations
    ├── Makefile                                ## Sets up the virtual environment 
    ├── gui.py                                  ## Front-end GUI script
    ├── main.py                                 ## AR face scanning showcase script
    ├── requirements.txt                        ## Required packages to run
├── README.md                                   ## You are here
```

<a name="installation"></a>

## 2. Installation

Clone this repo. In the directory, the project file can be installed by running ```make run```.
A virtual environment ```.venv``` (which is ignored by git) using python3 will be created with necessary dependencies to run the project.

```bash
git clone $THISREPO
cd $THISREPO/ARBotox
make run
```
**Note**: For MacOS, Mediapipe may not work as intended at times and might need to be downgraded to an older version. If there are persistent runtime issues related to Mediapipe on MacOS, try downgrading to ``mediapipe==0.10.9``

Next, import the SQL data, which can be done by running the contents of ARBotox/db_api/createDatabase.sql either using mysql on the terminal, or an application such as MySQL Workbench. After this is done, you will need to update the credentials at the beginning of the files Id_fix.py and db.py under the db_api directory. Make sure the database username, password, host and name are consistent.


<a name="repro"></a>
## 3. Reproduction

To run the application, first make sure you are in the ARBotox directory. In the gui.py use the find tool to look for 'reload_data_to_database=' which should appear twice. Set it to True the first time you are running the app, and False any subsequent times to avoid redundant loading. Start the GUI using the following command. Please note that the face scanning won't start until injection points have been selected.

```bash
streamlit run .\gui.py
```

<a name="guide"></a>
## 4. Guidance

- Use [git](https://git-scm.com/book/en/v2)
    - Do NOT use history re-editing (rebase)
    - Commit messages should be informative:
        - No: 'this should fix it', 'bump' commit messages
        - Yes: 'Resolve invalid API call in updating X'
    - Do NOT include IDE folders (.idea), or hidden files. Update your .gitignore where needed.
    - Do NOT use the repository to upload data
- Use [VSCode](https://code.visualstudio.com/) or a similarly powerful IDE
- Use [Copilot for free](https://dev.to/twizelissa/how-to-enable-github-copilot-for-free-as-student-4kal)
- Sign up for [GitHub Education](https://education.github.com/) 
