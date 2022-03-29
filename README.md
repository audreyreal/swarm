![Swarm](https://user-images.githubusercontent.com/19257341/159143323-93546138-ef97-47ff-89d1-70707f5aea2c.png)
# swarm (puppet manager)

trynna make prepping a bit less burnout prone by making it braindead simple
maybe some other things too idk
## how to use (on windows)
1. download latest binary release from https://github.com/sw33ze/swarm/releases
1. double click, nationlist json should be downloaded
1. fill nationlist json with nations and passwords respectively
1. open swarm.exe, navigate to tab you want to use
1. fill in main nation (for user agent) and jump point/poll fields
1. mash the button until the program tells you you're all done/out of nations
## how to run from source (on windows)
1. install python 3.10
1. run install_dependencies.bat
1. run main.pyw with python 3.10
## how to create binaries (on windows)
1. install python 3.10
1. run install_dependencies.bat
1. run "python -m pip install pyinstaller"
1. run compile_exe.bat
## submitting pull requests
pls format your code with black beforehand, basically my only requirement ._.
## todo
- [x] change theme
- [x] switch to a tabbed interface or checkboxes for multiple options
- [x] migrate from storing data in .py to .json
- [x] switch to dictionary for nation list
- [x] add tab for poll raiding
- [x] add icon
- [ ] add tab for putting up tags (this is gonna suck so much i hate nationstates)
- [ ] add tab for changing nation fields and flag
- [ ] add puppet creator because NS++ is practically abandoned at this point
- [x] generalize currently used functions
- [x] create binaries
- [x] publish instructions on creating binaries in accordance w/ GPL
- [x] functionality to find your wa
- [x] login script
