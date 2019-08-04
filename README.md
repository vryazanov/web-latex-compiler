## Introduction
A web service that compiles LaTeX files online via UI or API call.

## Examples
Compile single LaTeX file:
```
curl -O -F 'file=@hello.latex' -X POST http://127.0.0.1:5000/upload
```
You can send a zip file in case if you have multiple files or assets.
Pass `entry` param with the path to root LaTex file like this:
```
curl -O -F 'file=@large.zip' -d 'entry=./large/main.latex' -X POST http://127.0.0.1:5000/upload-zip
```
## How to start local environment
TBU

## How to run quality checks and tests
```
docker-compose run web ./codestyle.sh
docker-compose run web python -m pytest
```