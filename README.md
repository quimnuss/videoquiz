# videoquiz
Automatic video generator of a Quiz for streams

## build

generate the spec and let the github action build it or build it yourself with pyinstaller

```
$ pyi-makespec --onefile quizgen.py
$ pyinstaller quizgen.spec
```

or

```
$ pyinstaller --onefile quizgen.py
```

