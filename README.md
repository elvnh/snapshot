# snapshot
`snapshot` is an integration testing utility used for testing programs which produce some
sort of text output, for example compilers. It works by providing it a series of input files
and a command to run on those files, as well as an expected output for those input files.

It then runs the command and compares the received output with the expected output. If they differ,
the test has failed.

## Configuring

Tests are configured using `.toml` files. This file is then provided to `snapshot`, along with
input files to run the tests on.

```toml
output_dir = "foo" # Where to put the received outputs
max_failures = 10 # How many tests are allowed to failed before aborting

# Define a test called 'basic'
[tests.basic]
command = "cat {file}" # The command to run. 'file' will be replaced with the input filename.
return_code = 0 # The expected return code. Anything else will be counted as a failure.

# Define a test called 'lexer'
[tests.lexer]
command = "cat {file}"
return_code = 0
```

## Quick start
```bash
python3 snapshot.py config.toml run input/*
```

This will use `config.toml` as config file and run the tests defined in it on all files in the `input`
directory.

## Usage
```bash
python3 snapshot.py <config> [mode] [filenames]...
```

### Subcommands
`snapshot` must be run with one of the available subcommands. The commands are as follows:

#### `run`
Run the tests defined in `<config>` on all provided filenames.
```bash
python3 snapshot.py <config> run filename [filenames]...
```


#### `accept`
Accept the provided files as the expected output for the test which produced them.
The next time running the test, the output will be compared to these new expected output files.

```bash
python3 snapshot.py <config> accept filename [filenames]...
```

#### `unaccept`
Remove the provided output files so that they are no longer counted as the expected output.

```bash
python3 snapshot.py <config> unaccept filename [filenames]...
```

#### `diff`
Display the difference between expected and received output files for the provided test files.

```bash
python3 snapshot.py <config> diff filename [filenames]...
```
#### `rm`
Remove expected and received output files for the given input files.

```bash
python3 snapshot.py <config> rm filename [filenames]...
```

#### `clean`
Remove all expected and received files.

```bash
python3 snapshot.py <config> clean
```

### Flags
Several flags are available, some of which work for multiple subcommands. The flags are as follows:

- `-i`/`--interactive` - Prompts the user for each action taken. In `run` and `diff` mode,
  prompts to ask if user wants to accept the received output if a test fails. In `accept` and `unaccept` mode
  it will ask for confirmation before accepting or unaccepting received output.
- `-j n`/`--jobs n` - Works for the `run` subcommand. Run tests on `n` threads.
- `-s`/`--save` - Works for the `run` subcommand. Automatically save each new output file as the expected output file for that test. Use with caution.
- `-T`/`--no-truncate-diffs` - Works for the `run` subcommand. By default, diffs are truncated if too
  long. If this flag is present, the will always be printed in their entirety.
