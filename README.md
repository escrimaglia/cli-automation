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
* `--install-completion`: Install completion for the current shell (highly recommended).
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `netmiko`: SSH library for network automation
* `scrapli`: Telnet, SSH or NETCONF library for network...

## `cla netmiko`

SSH library for network automation

**Usage**:

```console
$ cla netmiko [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `pull-single`: Pull data from a Single Host
* `pull-multiple`: Pull data from Multiple Hosts
* `push-single`: Push configuration to a Single Host
* `push-multiple`: Push configuration file to Multiple Hosts
* `templates`: Download templates to create hosts and...

### `cla netmiko pull-single`

Pull data from a Single Host

**Usage**:

```console
$ cla netmiko pull-single [OPTIONS]
```

**Options**:

* `-h, --host TEXT`: host ip address  [required]
* `-u, --user TEXT`: username  [required]
* `-c, --cmd TEXT`: commands to execute on device  [required]
* `-t, --type [cisco_ios|cisco_xr|juniper_junos|arista_eos|huawei|alcatel_sros|autodetect]`: device type  [required]
* `-s, --cfg TEXT`: ssh config file
* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [info|debug|error|warning|critical]`: Log level
* `--help`: Show this message and exit.

### `cla netmiko pull-multiple`

Pull data from Multiple Hosts

**Usage**:

```console
$ cla netmiko pull-multiple [OPTIONS]
```

**Options**:

* `-h, --hosts FILENAME Json file`: group of hosts  [required]
* `-c, --cmd TEXT`: commands to execute on device  [required]
* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [info|debug|error|warning|critical]`: Log level
* `--help`: Show this message and exit.

### `cla netmiko push-single`

Push configuration to a Single Host

**Usage**:

```console
$ cla netmiko push-single [OPTIONS]
```

**Options**:

* `-h, --host TEXT`: host ip address  [required]
* `-u, --user TEXT`: username  [required]
* `-t, --type [cisco_ios|cisco_xr|juniper_junos|arista_eos|huawei|alcatel_sros|autodetect]`: device type  [required]
* `-c, --cmd TEXT`: commands to configure on device
* `-f, --cmdf FILENAME Json file`: commands to configure on device
* `-s, --cfg TEXT`: ssh config file
* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [info|debug|error|warning|critical]`: Log level
* `--help`: Show this message and exit.

### `cla netmiko push-multiple`

Push configuration file to Multiple Hosts

**Usage**:

```console
$ cla netmiko push-multiple [OPTIONS]
```

**Options**:

* `-h, --hosts FILENAME Json file`: group of hosts  [required]
* `-f, --cmdf FILENAME Json file`: commands to configure on device  [required]
* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [info|debug|error|warning|critical]`: Log level
* `--help`: Show this message and exit.

### `cla netmiko templates`

Download templates to create hosts and config commands files with the necessary information

**Usage**:

```console
$ cla netmiko templates [OPTIONS]
```

**Options**:

* `-v, --verbose`: Verbose level  [default: 0]
* `-l, --log [info|debug|error|warning|critical]`: Log level
* `--help`: Show this message and exit.

## `cla scrapli`

Telnet, SSH or NETCONF library for network automation. Yet under development

**Usage**:

```console
$ cla scrapli [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `pull-data`: Pull data from devices
* `push-data`: Push data to devices

### `cla scrapli pull-data`

Pull data from devices

**Usage**:

```console
$ cla scrapli pull-data [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `cla scrapli push-data`

Push data to devices

**Usage**:

```console
$ cla scrapli push-data [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

`Author: Ed Scrimaglia`
