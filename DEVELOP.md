## Clean Test Scenario

```
docker run -v `pwd`/furiosa-cli:/furiosa-cli \
-v $HOME/.furiosa:/root/.furiosa \
-v `pwd`/furiosa-cli/test_data:/test_data -it ubuntu:focal /bin/bash

apt-get update && apt-get install -y python3-pip git

pip3 install --upgrade git+https://github.com/furiosa-ai/furiosa-cli.git

cd furiosa-cli && python3 -m unittest discover -v -s ./test
```