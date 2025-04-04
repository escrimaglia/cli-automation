# `cla`

The CLA `Command Line interface Automation` is an Async Typer Python-based application designed to automate infrastructure directly from the command line. With CLA,
there is no need to write a single line of code, users simply follow the options presented in the help menu. When I thought about building CLA, I considered those
network engineers who have not yet acquired the necessary software knowledge, so `CLA was specifically designed to enable engineers who have not yet acquired software 
knowledge to progress in the practice of automation`. CLA lets you both extract configurations and set up networking devices. You can enter 
connection and configuration parameters either via the command line or using JSON files. Another reason I decided to develop CLA is to enable its commands to be invoked 
from any programming language, once again, without requiring a single line of code for automation. CLA version 1.X.X focuses exclusively on Network Automation, while version 
2.X.X will introduce Cloud Automation capabilities.

**Supported devices**:

- Cisco IOS
- Cisco XR
- Cisco XE
- Cisco NXOS
- Juniper
- Arista
- Huawei
- Extreme
- Alcatel
- Vyos
- Generic Telnet

**Instalation**:

Since CLA generates working files, it is recommended to create a virtual environment (to avoid potential conflicts between Python libraries) and install it there. Alternatively, if you prefer a global installation, you only need to create a working directory. Once installed, it is advisable to run the `cla --install-completion` command so that the TAB key helps navigate the options menu.
Additionally, while typing a command, the --help parameter can be used anywhere to obtain context-based assistance.

```
From PyPY:

$ pip install cli-automation
```

[Project Repository](https://github.com/escrimaglia/cli-automation)

**Usage**:

```console
$ cla [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-V, --version`
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `templates`: Create examples of configuration files
* `ssh`: Accesses devices via the SSH protocol
* `telnet`: Accesses devices via the Telnet protocol
* `tunnel`: Manage tunnel with Bastion Host

## `cla templates`

The cla templates command generates example files, which can be used to create working files, both 
for connection parameters and for device configuration commands

**Usage**:

```console
$ cla templates [OPTIONS]
```

**Options**:

* `-v, --verbose`: Verbose level  [default: 1; 0&lt;=x&lt;=2]
* `--help`: Show this message and exit.

## `cla ssh`

The cla ssh command allows access to devices via the SSH protocol. The command can be used to pull or push configurations to devices.
To structure the output data when retrieving configurations, the `cla ssh pullconfig` command uses TextFSM templates. If the query
command is included in the templates, the output will be in JSON format; otherwise, the output will be in TXT format.

**Usage**:

```console
$ cla ssh [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `onepull`: Pull config from a single host
* `pullconfig`: Pull config from multiple hosts
* `onepush`: Push config to a single host
* `pushconfig`: Push config to multiple hosts

### `cla ssh onepull`

Pull config from a single host

**Usage**:

```console
$ cla ssh onepull [OPTIONS]
```

**Options**:

* `-h, --host TEXT`: host name or ip address  [required]
* `-u, --user TEXT`: username  [required]
* `-c, --cmd Multiple -c parameter`: commands to execute on the device  [required]
* `-t, --type [cisco_ios|cisco_xr|cisco_xe|cisco_nxos|juniper|juniper_junos|arista_eos|huawei|huawei_vrp|alcatel_sros|vyos|vyatta_vyos|extreme_exos|extreme]`: device type  [required]
* `-p, --port INTEGER`: port  [default: 22]
* `-v, --verbose`: verbose level  [default: 0; 0&lt;=x&lt;=2]
* `-o, --output FILENAME Json file`: output file  [default: output.json]
* `-d, --delay FLOAT RANGE`: global delay  [default: 0.1; 0.1&lt;=x&lt;=4]
* `-s, --cfg TEXT`: ssh config file
* `--help`: Show this message and exit.

### `cla ssh pullconfig`

the commands can be entered via the command line or through a JSON file

**Usage**:

```console
$ cla ssh pullconfig [OPTIONS]
```

**Options**:

* `-h, --hosts FILENAME Json file`: group of hosts  [required]
* `-c, --cmd Multiple -c parameter`: commands to execute on the device
* `-f, --cmdf FILENAME Json file`: commands to configure on the device
* `-v, --verbose`: verbose level  [default: 0; 0&lt;=x&lt;=2]
* `-o, --output FILENAME Json file`: output file  [default: output.json]
* `--help`: Show this message and exit.

### `cla ssh onepush`

the commands can be entered via the command line or through a JSON file

**Usage**:

```console
$ cla ssh onepush [OPTIONS]
```

**Options**:

* `-h, --host TEXT`: host name or ip address  [required]
* `-u, --user TEXT`: username  [required]
* `-t, --type [cisco_ios|cisco_xr|cisco_xe|cisco_nxos|juniper|juniper_junos|arista_eos|huawei|huawei_vrp|alcatel_sros|vyos|vyatta_vyos|extreme_exos|extreme]`: device type  [required]
* `-c, --cmd Multiple -c parameter`: commands to configure the device
* `-f, --cmdf FILENAME Json file`: commands to configure the device
* `-p, --port INTEGER`: port  [default: 22]
* `-v, --verbose`: verbose level  [default: 0; 0&lt;=x&lt;=2]
* `-o, --output FILENAME Json file`: output file  [default: output.json]
* `-d, --delay FLOAT RANGE`: global delay factor  [default: 0.1; 0.1&lt;=x&lt;=4]
* `-s, --cfg TEXT`: ssh config file
* `--help`: Show this message and exit.

### `cla ssh pushconfig`

the commands must be provided through a JSON file

**Usage**:

```console
$ cla ssh pushconfig [OPTIONS]
```

**Options**:

* `-h, --hosts FILENAME Json file`: group of hosts  [required]
* `-f, --cmd FILENAME Json file`: commands to configure the device  [required]
* `-v, --verbose`: verbose level  [default: 0; 0&lt;=x&lt;=2]
* `-o, --output FILENAME Json file`: output file  [default: output.json]
* `--help`: Show this message and exit.

## `cla telnet`

Telnet was added to CLA to access older devices that, for some reason, do not support SSH. Telnet operates in a generic way,
 and configuration commands must follow the structure explained in the `telnet_commands_structure.json file`, file generated by the `cla templates` command. 
However, whenever possible, SSH remains the preferred protocol.

**Usage**:

```console
$ cla telnet [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `pullconfig`: Pull config from multiple hosts
* `pushconfig`: Push config file to multiple hosts

### `cla telnet pullconfig`

Pull config from multiple hosts

**Usage**:

```console
$ cla telnet pullconfig [OPTIONS]
```

**Options**:

* `-h, --hosts FILENAME Json file`: group of hosts  [required]
* `-c, --cmd Single -c parameter`: command to execute on the device  [required]
* `-v, --verbose`: verbose level  [default: 0; 0&lt;=x&lt;=2]
* `-o, --output FILENAME text file`: output file  [default: output.txt]
* `--help`: Show this message and exit.

### `cla telnet pushconfig`

Push config file to multiple hosts

**Usage**:

```console
$ cla telnet pushconfig [OPTIONS]
```

**Options**:

* `-h, --hosts FILENAME Json file`: group of hosts  [required]
* `-f, --cmdf FILENAME Json file`: commands to configure on the device  [required]
* `-v, --verbose`: verbose level  [default: 0; 0&lt;=x&lt;=2]
* `-o, --output FILENAME text file`: output file  [default: output.txt]
* `--help`: Show this message and exit.

## `cla tunnel`

Sometimes, the machine running CLA doesn’t have direct access to the devices and must go through a Bastion Host or Jump Host. To connect via a Bastion Host, 
you can either configure SSH specifically or set up a tunnel. Personally, I think creating a tunnel is more efficient since it avoids SSH configuration, 
specially when using `Telnet` commands. 
Using `cla tunnel`, you can create or remove a SOCKS5 tunnel. For `cla tunnel` to function properly, the host running CLA must have easy access to the 
Bastion Host (it should be listed in the Bastion Host&#x27;s known_hosts file). CLA constantly monitors the tunnel’s status, but you can also manually check it using 
the Linux command `lsof -i:{local_port}`.

**Usage**:

```console
$ cla tunnel [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `setup`: Setup a tunnel to the Bastion Host
* `kill`: Kill the tunnel to the bastion Host
* `status`: Check the tunnel status

### `cla tunnel setup`

**Usage**:

```console
$ cla tunnel setup [OPTIONS]
```

**Options**:

* `-u, --user TEXT`: bastion host username  [required]
* `-b, --bastion TEXT`: bastion name or ip address  [required]
* `-p, --port INTEGER RANGE`: local port  [default: 1080; 1000&lt;=x&lt;=1100]
* `-t, --timeout INTEGER RANGE`: timeout in seconds for the tunnel startup  [default: 10; 3&lt;=x&lt;=25]
* `-v, --verbose`: verbose level  [default: 1; 0&lt;=x&lt;=2]
* `--help`: Show this message and exit.

### `cla tunnel kill`

**Usage**:

```console
$ cla tunnel kill [OPTIONS]
```

**Options**:

* `-v, --verbose`: verbose level  [default: 1; 0&lt;=x&lt;=2]
* `--help`: Show this message and exit.

### `cla tunnel status`

**Usage**:

```console
$ cla tunnel status [OPTIONS]
```

**Options**:

* `-p, --port INTEGER RANGE`: local port  [default: 1080; 1000&lt;=x&lt;=1100]
* `-t, --timeout INTEGER RANGE`: timeout in seconds for the tunnel return its status  [default: 10; 3&lt;=x&lt;=20]
* `-r, --test INTEGER`: remote port for testing the tunnel  [default: 22]
* `-v, --verbose`: verbose level  [default: 1; 0&lt;=x&lt;=2]
* `--help`: Show this message and exit.

**Logging**:

CLA includes an efficient Log System that allows you to view INFO, DEBUG, CRITICAL, and ERROR details for each operation performed by CLA. The Log System includes a log file rotation based on file size. Each time the log file exceeds 5 MB, a new log file will be created.
