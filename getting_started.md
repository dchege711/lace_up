# Getting Started on LaceUp

1. [Preparing Your Python Environment](#preparing-your-python-environment)

2. [Using Git](#using-git)

I'll update more steps if need be. I'm always here for debugging help! - Chege

## Preparing Your Python Environment

* First get your Python in order. Make sure you have Python 3.6.x installed. There are instructions on how to check and install right [here](http://docs.python-guide.org/en/latest/starting/install3/osx/). The code base for LaceUp was done in Python 3.6.4, so it's more convenient for you to also have it.

* LaceUp uses some non-standard Python libraries. The most elegant way of dealing with this is by creating a virtual environment that is specific to LaceUp.

* We'll start by creating an empty virtual env (without any packages). I recommend [Conda's package manager](https://conda.io/docs/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands). The rest of the instructions assume that you have [Conda installed](https://conda.io/docs/user-guide/install/index.html). 

* Run `$ conda create --no-default-packages -n lace_up python=3.6`. The virtual environment should contain just the packages needed to run LaceUp, and nothing else. If we have more packages than necessary, the application's package will be unecessarily bloated. That's why we include the *no-default-packages* flag.

* To move into the newly created env, run `$ source activate lace_up`. Your command prompt should now look like `(lace_up) $` instead of just `$`.

* To confirm that the virtual environment is relatively clean, run `(lace_up) $ pip freeze`. The list of packages should be quite small (at most ~20).


## Using Git

* This part assumes that you have Git [installed](https://git-scm.com/book/en/v1/Getting-Started-Installing-Git). Git is a version control system that will save you from [clutter and endless pain](https://www.reddit.com/r/ProgrammerHumor/comments/72rki5/the_real_version_control/).

* To get working knowledge, I recommend [Git Basics](https://git-scm.com/book/en/v1/Getting-Started-Git-Basics), [Git First-Time Setup](https://git-scm.com/book/en/v1/Getting-Started-First-Time-Git-Setup), and [Getting Help](https://git-scm.com/book/en/v1/Getting-Started-Getting-Help). As for the rest, God bless StackOverflow!

* So far, you don't have LaceUp files on your computer yet. In your home directory, run `(lace_up) $ git clone https://github.com/dchege711/lace_up.git`. This copies the LaceUp repository into a folder named 'lace_up'. Go ahead and enter the directory using `(lace_up) $ cd lace_up`. Awesome! Sorry the setup took so long. But I promise you that it was worth it.

* We now need to install the packages that we need for LaceUp. Run `(lace_up) $ pip install -r requirements.txt`. If you run `(lace_up) $ pip freeze`, the resulting list should contain all of the packages listed in requirements.txt. 

* Side note: the file 'requirements.txt' is created using `(lace_up) $ pip freeze > requirements.txt`. If you have unnecessary packages installed, requirements.txt will include all of them. When we run the application in some server provider (e.g. Heroku), the resulting package will be larger, and maybe cost us more $$$. We don't want that. In general, it's a good practice to just install what you need. <sup>[*Cough* NodeJS *Cough*](https://twitter.com/iamdevloper/status/908335750797766656)</sup>

* Now that you've read the 3 articles above, let's get down to what it means for LaceUp. We want to have a special branch that only has code that runs on the actual website. We will not be experimenting stuff on this branch. Let that branch be `master`. 

* Say you want to add discussion threads to each upcoming game:

    * You can't do this on the `master` branch, so you create your own branch using `(lace_up) $ git checkout -b add_discussion_threads`. You should receive a confirmation message saying that you have a new branch, which is even with master.
    * Now that you have your own branch, go ahead and hack away. Although you can use `(lace_up) $ git add .` generously, be judicious about using `(lace_up) $ git commit -m "<MEANINGFUL_COMMIT_MESSAGE>"`. Relevant [blog](https://www.git-tower.com/learn/git/ebook/en/command-line/appendix/best-practices) [posts](http://alistapart.com/article/the-art-of-the-commit).
    * Occassionally, back up your code on Github, by running `(lace_up) $ git push origin add_discussion_threads`.
    * Once you're done and you've confirmed that your changes work as expected, it's time to push that to the `master` branch. Yay! Go ahead and run `(lace_up) $ git push origin master`. 
    * Since the `master` branch is protected, your changes won't be immediate. I'll use my admin status to confirm that the new changes don't break anything and then merge your changes with the master branch.

* Say someone recently pushed something to the `master` branch. If you want to get those changes in the branch that you're currently working on, run `(lace_up) $ git pull origin master`. Sometimes you'll get merge conflicts, but fear not. Resolving merge conflicts builds character!<sup>[I really need to get a life...](https://www.reddit.com/r/ProgrammerHumor/comments/7nuvie/got_myself_a_tool_for_resolving_git_merge/)</sup>