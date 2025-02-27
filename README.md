# `cla`

CLA `Command Line interface Automation` is a Python-based application designed to automate infrastructure directly from the command line.
With CLA, there is no need to write a single line of code, users simply follow the options presented in the help menu. `CLA was specifically
designed for networking engineers who have not yet advanced in programming knowledge`.
CLA lets you both extract configurations and set up networking devices, doing it all asynchronously. You can enter connection and configuration
parameters either via the command line or using JSON files.
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

* `templates`: Create working files
* `ssh`: Accesses devices via the SSH protocol
* `telnet`: Accesses devices via the Telnet protocol
* `tunnel`: Manage SOCKS5 tunnel with Bastion Host

## `cla templates`

The `cla templates` command generates example files, which can be used to create working files, both for connection parameters and for device configuration commands

**Usage**:

```console
$ cla templates [OPTIONS]
```

**Options**:

* `-v, --verbose`: Verbose level  [default: 0; x&lt;=2]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `--help`: Show this message and exit.

## `cla ssh`

The `cla ssh` command allows access to devices via the SSH protocol. The command can be used to pull or push configurations to devices.

**Usage**:

```console
$ cla ssh [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `onepull`: Pull config from a single Host
* `pullconfig`: Pull config from hosts in host file
* `onepush`: Push config to a single host
* `pushconfig`: Push config file to hosts in hosts file

### `cla ssh onepull`

Pull config from a single Host

**Usage**:

```console
$ cla ssh onepull [OPTIONS]
```

**Options**:

* `-h, --host TEXT`: host ip address  [required]
* `-u, --user TEXT`: username  [required]
* `-c, --cmd TEXT`: commands to execute on device  [required]
* `-t, --type [cisco_ios|cisco_xr|juniper_junos|arista_eos|huawei|alcatel_sros]`: device type  [required]
* `-p, --port INTEGER`: port  [default: 22]
* `-v, --verbose`: Verbose level  [default: 0; x&lt;=2]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `-o, --output FILENAME`: output file  [default: output.json]
* `-d, --delay FLOAT`: port  [default: 0.1]
* `-s, --cfg TEXT`: ssh config file
* `--help`: Show this message and exit.

### `cla ssh pullconfig`

Pull config from hosts in host file

**Usage**:

```console
$ cla ssh pullconfig [OPTIONS]
```

**Options**:

* `-h, --hosts FILENAME Json file`: group of hosts  [required]
* `-c, --cmd TEXT`: commands to execute on device  [required]
* `-v, --verbose`: Verbose level  [default: 0; x&lt;=2]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `-o, --output FILENAME Json file`: output file  [default: output.json]
* `--help`: Show this message and exit.

### `cla ssh onepush`

Push config to a single host

**Usage**:

```console
$ cla ssh onepush [OPTIONS]
```

**Options**:

* `-h, --host TEXT`: host ip address  [required]
* `-u, --user TEXT`: username  [required]
* `-t, --type [cisco_ios|cisco_xr|juniper_junos|arista_eos|huawei|alcatel_sros]`: device type  [required]
* `-c, --cmd TEXT`: commands to configure on device
* `-f, --cmdf FILENAME Json file`: commands to configure on device
* `-p, --port INTEGER`: port  [default: 22]
* `-v, --verbose`: Verbose level  [default: 0; x&lt;=2]
* `-l, --llog [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `-o, --output FILENAME`: output file  [default: output.json]
* `-d, --delay FLOAT`: global delay factor  [default: 0.1]
* `-s, --cfg TEXT`: ssh config file
* `--help`: Show this message and exit.

### `cla ssh pushconfig`

Push config file to hosts in hosts file

**Usage**:

```console
$ cla ssh pushconfig [OPTIONS]
```

**Options**:

* `-h, --hosts FILENAME Json file`: group of hosts  [required]
* `-c, --cmd FILENAME Json file`: commands to configure on device  [required]
* `-v, --verbose`: Verbose level  [default: 0; x&lt;=2]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `-o, --output FILENAME Json file`: output file  [default: output.json]
* `--help`: Show this message and exit.

## `cla telnet`

Telnet was added to CLA to access older devices that, for some reason, do not support SSH. Telnet operates in a generic way,
 and configuration commands must follow the structure explained in the `example_telnet_commands_structure.json file`, file generated by the `cla templates` command. However, whenever possible, SSH remains the preferred protocol.

**Usage**:

```console
$ cla telnet [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `pullconfig`: Pull configuration from Hosts
* `pushconfig`: Push configuration file to Hosts

### `cla telnet pullconfig`

Pull configuration from Hosts

**Usage**:

```console
$ cla telnet pullconfig [OPTIONS]
```

**Options**:

* `-h, --hosts FILENAME Json file`: group of hosts  [required]
* `-c, --cmd TEXT`: commands to execute on device  [required]
* `-v, --verbose`: Verbose level  [default: 0; x&lt;=2]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `-o, --output FILENAME text file`: output file  [default: output.txt]
* `--help`: Show this message and exit.

### `cla telnet pushconfig`

Push configuration file to Hosts

**Usage**:

```console
$ cla telnet pushconfig [OPTIONS]
```

**Options**:

* `-h, --hosts FILENAME Json file`: group of hosts  [required]
* `-c, --cmd FILENAME Json file`: commands to configure on device  [required]
* `-v, --verbose`: Verbose level  [default: 0; x&lt;=2]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `-o, --output FILENAME text file`: output file  [default: output.json]
* `--help`: Show this message and exit.

## `cla tunnel`

Sometimes, the machine running CLA doesn’t have direct access to the devices and must go through a Bastion Host or Jump Host. To connect via a Bastion Host, you can either configure SSH specifically or set up a tunnel. Personally, I think creating a tunnel is more efficient since it avoids SSH configuration. Using `cla tunnel`, you can create or remove a SOCKS5 tunnel. CLA constantly monitors the tunnel’s status, but you can also manually check it using the Linux command `lsof -i:{local_port}`.

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

**Usage**:

```console
$ cla tunnel setup [OPTIONS]
```

**Options**:

* `-u, --user TEXT`: bastion host username  [required]
* `-b, --bastion TEXT`: bastion name or ip address  [required]
* `-p, --port INTEGER`: local port  [default: 1080]
* `-v, --verbose`: Verbose level  [default: 0; x&lt;=2]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `--help`: Show this message and exit.

### `cla tunnel kill`

**Usage**:

```console
$ cla tunnel kill [OPTIONS]
```

**Options**:

* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [INFO|DEBUG|ERROR|WARNING|CRITICAL]`: Log level  [default: INFO]
* `--help`: Show this message and exit.

### `cla Logging`

CLA includes an efficient Log System that allows you to view INFO, DEBUG, CRITICAL, and ERROR details for each operation performed by CLA.

#### By Ed Scrimaglia - <edgardo.scrimaglia@gmail.com>