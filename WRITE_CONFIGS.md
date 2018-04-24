# How to write necessary config files

## Updater config

`Updater` config (located at `~/.pyhodl/data/config.json`) store values like the data folder or how often to update your transactions
```json
{
    "interval": "1h",
    "folder": ""
}
```

Supported options are:

| Option | Description | Default | Possible options |
| --- | --- | --- | --- |
| `interval` | How often update data | `6h` | 1h, 2h ... 1d, 2d ... 1w, 2w .. 1m, 2m |
| `folder` | Local data folder where to store transacrions | `~/.pyhodl/data/` | any folder in your machine |



## API configs

`API` config is generally stored at `~/.pyhodl/api/config.json`. A simple config file looks like
```json
{
  "binance": {
    "key": "ghrohowfowjp748329jfcoenrc3u2m329",
    "secret": "oyvnmruk,2c9023c.230c923c0k'23l'"
  },
  "bitfinex": {
    "key": "çFWLGògèp385'c0l439k",
    "secret": "3902'1.x'-àeì3xcm32ix,02ir020c9v4p"
  },
  "coinbase": {
    "key": "09,1'.0c1'493èvk0932lèv",
    "secret": "im,3q-v.4o30483nvm3,04913'v,.èeoce-r_V"
  },
  "gdax": {
    "key": "04v8mà,3èo4'03q9vòm-,o.3'à 0àq6",
    "secret": "VM)r,£CQ=4i3pv08mò3,cp03q49 vnqm,4o.3qcàp",
    "passphrase": "0v4 m)°;?:$_3qà'49mc-,<x.ed-qxepà"
  }
}
```

To get your personal `key`s and `secret`s please refer to [the guide](IMPORT_DATA.md).
