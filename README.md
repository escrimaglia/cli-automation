# `cla`

CLA (Command Line interface Automation) is a Python-based application designed to automate infrastructure directly from the command line. 
With CLA, there is no need to write a single line of code, users simply follow the options presented in the help menu. It was specifically 
developed for networking engineers who have not yet advanced in programming knowledge.  
LA version 1 focuses exclusively on Network Automation, while version 2 will introduce Cloud Automation capabilities.

**Usage**:

```console
$ cla [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-V, --version`: Get the app version
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `templates`: Download templates to create the working...
* `ssh`: Access devices using SSH protocol
* `telnet`: Access devices using Telnet protocol
* `tunnel`: Manage SOCKS5 tunnel with Bastion Host

## `cla templates`

Download templates to create the working files

**Usage**:

```console
$ cla templates [OPTIONS]
```

**Options**:

* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `--help`: Show this message and exit.

Download templates to create the working files

## `cla ssh`

Access devices using SSH protocol

**Usage**:

```console
$ cla ssh [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `pullsingle`: Pull data from a Single Host
* `pullmultiple`: Pull data from Multiple Hosts
* `pushsingle`: Push configuration to a Single Host
* `pushmultiple`: Push configuration file to Multiple Hosts

### `cla ssh pullsingle`

Pull data from a Single Host

**Usage**:

```console
$ cla ssh pullsingle [OPTIONS]
```

**Options**:

* `-h, --host TEXT`: host ip address  [required]
* `-u, --user TEXT`: username  [required]
* `-c, --cmd TEXT`: commands to execute on device  [required]
* `-t, --type [cisco_ios|cisco_xr|juniper_junos|arista_eos|huawei|alcatel_sros|autodetect]`: device type  [default: generic_telnet]
* `-p, --port INTEGER`: port  [default: 22]
* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `-d, --delay FLOAT`: port  [default: 0.1]
* `-s, --cfg TEXT`: ssh config file
* `--help`: Show this message and exit.

### `cla ssh pullmultiple`

Pull data from Multiple Hosts

**Usage**:

```console
$ cla ssh pullmultiple [OPTIONS]
```

**Options**:

* `-h, --hosts FILENAME Json file`: group of hosts  [required]
* `-c, --cmd TEXT`: commands to execute on device  [required]
* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `--help`: Show this message and exit.

### `cla ssh pushsingle`

Push configuration to a Single Host

**Usage**:

```console
$ cla ssh pushsingle [OPTIONS]
```

**Options**:

* `-h, --host TEXT`: host ip address  [required]
* `-u, --user TEXT`: username  [required]
* `-t, --type [cisco_ios|cisco_xr|juniper_junos|arista_eos|huawei|alcatel_sros|autodetect]`: device type  [required]
* `-c, --cmd TEXT`: commands to configure on device
* `-f, --cmdf FILENAME Json file`: commands to configure on device
* `-s, --cfg TEXT`: ssh config file
* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `--help`: Show this message and exit.

### `cla ssh pushmultiple`

Push configuration file to Multiple Hosts

**Usage**:

```console
$ cla ssh pushmultiple [OPTIONS]
```

**Options**:

* `-h, --hosts FILENAME Json file`: group of hosts  [required]
* `-f, --cmdf FILENAME Json file`: commands to configure on device  [required]
* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `--help`: Show this message and exit.

## `cla telnet`

Access devices using Telnet protocol

**Usage**:

```console
$ cla telnet [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `pullsingle`: Pull data from a Single Host
* `pullmultiple`: Pull data from Multiple Hosts
* `push-single`: Push configuration to a Single Host
* `push-multiple`: Push configuration file to Multiple Hosts

### `cla telnet pullsingle`

Pull data from a Single Host

**Usage**:

```console
$ cla telnet pullsingle [OPTIONS]
```

**Options**:

* `-h, --host TEXT`: host ip address  [required]
* `-u, --user TEXT`: username  [required]
* `-c, --cmd TEXT`: commands to execute on device  [required]
* `-t, --type TEXT`: device type  [default: generic_telnet]
* `-p, --port INTEGER`: port  [default: 23]
* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `-d, --delay FLOAT`: port  [default: 0.1]
* `--help`: Show this message and exit.

### `cla telnet pullmultiple`

Pull data from Multiple Hosts

**Usage**:

```console
$ cla telnet pullmultiple [OPTIONS]
```

**Options**:

* `-h, --hosts FILENAME Json file`: group of hosts  [required]
* `-c, --cmd TEXT`: commands to execute on device  [required]
* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `--help`: Show this message and exit.

### `cla telnet push-single`

Push configuration to a Single Host

**Usage**:

```console
$ cla telnet push-single [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `cla telnet push-multiple`

Push configuration file to Multiple Hosts

**Usage**:

```console
$ cla telnet push-multiple [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `cla tunnel`

Manage SOCKS5 tunnel with Bastion Host

**Usage**:

```console
$ cla tunnel [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `setup`: Setup SOCKS5 tunnel to the Bastion Host
* `kill`: Kill SOCKS5 tunnel to the bastion Host

### `cla tunnel setup`

Setup SOCKS5 tunnel to the Bastion Host

**Usage**:

```console
$ cla tunnel setup [OPTIONS]
```

**Options**:

* `-u, --user TEXT`: bastion host username  [required]
* `-b, --bastion TEXT`: bastion host ip address  [required]
* `-p, --port INTEGER`: local port  [default: 1080]
* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `--help`: Show this message and exit.

### `cla tunnel kill`

Kill SOCKS5 tunnel to the bastion Host

**Usage**:

```console
$ cla tunnel kill [OPTIONS]
```

**Options**:

* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `--help`: Show this message and exit.
