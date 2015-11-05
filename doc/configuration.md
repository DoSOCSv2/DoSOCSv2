## Configuration 

DoSOCS is configured through plain text configuration files.

An explanation of the configuration options is found in the default
`dosocs2.conf` file. To generate a copy of this file, run
`dosocs2 newconfig`. It will write the default config to
`$XDG_CONFIG_HOME/dosocs2/dosocs2.conf`. Unless you have explicitly
defined `$XDG_CONFIG_HOME` in your environment, the new config file will
probably be at `~/.config/dosocs2/dosocs2.conf`.

### Discovery

DoSOCS will read configuration files in the following order:

- The in-memory default config (defined in `config.py`)
- `$XDG_CONFIG_HOME/dosocs2/dosocs2.conf` (if not defined,
  `$XDG_CONFIG_HOME` is equal to `$HOME/.config`)
- If an alternate config file is specified on the command line with `-f`,
  that one is used *instead of* the one in `$XDG_CONFIG_HOME`.

One can see the effective configuration using `dosocs2 configtest`. One may
also pass the `-f` option to this command to see the effects of specifying an
alternate config file location.
