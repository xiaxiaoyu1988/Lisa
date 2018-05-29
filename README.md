# lisa
A cross platform ui kit base on [cefpython](https://github.com/cztomczak/cefpython)

- [lisa](#lisa)
    - [Install](#install)
    - [Package](#package)
    - [ToDo](#todo)

## Install
```
    pip install cefpython3==57.0
```

Windows Platform
```
    pip install pywin32
```

## Package
Base on pyinstaller
```
    pip install pyinstaller
```

## ToDo
 * [x] Basic framework
 * [ ] config file support
 * [x] Windows Support
    * [x] Base on pywin32 
    * [x] Hide title bar
    * [x] Custom window height and width
 * [x] Mac OS Support
     * [ ] Base on PyObjC
     * [ ] Custom window height and width
     * [ ] Hide title bar
 * [ ] Linux Support
 * [x] Front and back communication
     * [x] Javascript callback
     * [x] http protocol support @refer to [bottle.py](http://www.bottlepy.org/docs/dev/)
         * [ ] http error handle
         * [ ] @route support function args 
 * [ ] Database Support
     * [ ] Internal sqlite3 support   
 * [X] Example
     * [X] helloworld
     * [X] calljs
     * [X] callpython
     * [X] bootstrap
     * [X] http
     * [ ] login
     * [ ] crossplatrom window custom