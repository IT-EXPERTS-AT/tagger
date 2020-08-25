# Tagger 


## About
This project contains two repositories `taggercore` and `taggercli`.

The taggercli helps with two main use cases:
 - finding resources in your AWS account and compare it to a certain tagging scheme
 - applying a tagging scheme to resources   
 
Taggercore provides utility classes for scanning an AWS account and tagging resources.

Please take a look at the individual README files for further information.


## Contribution

Please feel free to contribute to this project. Any help would be gladly appreciated. 


## Development
### Taggercore 
#### Dependency
Taggercore is based on a skew fork currently hosted on [github](https://github.com/tobHai/skew).  
To make changes to skew, clone this repo and commit to develop. Once committed, the new skew version can be installed by running
 `pipenv uninstall skew`  
 `pipenv install git+file:///YOUR_PATH_TO_REPO/skew@develop#egg=skew` 
from the pipenv shell of taggercore.

### Taggercli 

