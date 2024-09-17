# cel-takehome
Community Energy Labs takehome assignment

Usage:
```commandline
docker build . -t cel-takehome:local

# Run the server
docker run --rm -it -p 8080:8080 cel-takehome:local

# Local development
docker run --rm -it -v $(pwd):/app cel-takehome:local bash
```