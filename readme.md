# Linux + CodeQL Experiments

## Generate CodeQL Database

```sh
./setup-codeql-db.sh
```

## Additional Resources

```sh
codeql pack download trailofbits/cpp-queries trailofbits/go-queries
```

## Run CodeQL Analysis

```sh
codeql database analyze linux-codeql.db --format=sarif-latest --output=results.sarif -- codeql/cpp-queries
codeql database analyze linux-codeql.db --format=sarif-latest --output=./tob.sarif -- trailofbits/cpp-queries
```
