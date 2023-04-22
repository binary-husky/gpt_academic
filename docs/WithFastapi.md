# Running with fastapi

We currently support fastapi in order to solve sub-path deploy issue.

1. checkout to `subpath` branch

``` sh
git checkout subpath
```


2. merge lastest features (optional)

``` sh
git merge master
```

3. change CUSTOM_PATH setting in `config.py`

``` sh
nano config.py
```

4. Go!

``` sh
python main.py
```
