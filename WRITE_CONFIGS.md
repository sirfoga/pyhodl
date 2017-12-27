# How to write necessary config files

## Updater config

`Updater` config (located at `~home/.pyhodl/data/config.json`) store values like the data folder or how often to update your transactions
```json
{
    "interval": "1h",
    "folder": ""
}
```

Supported options are:

| Option | Description | Default | Possible options |
| --- | --- | --- | --- |
| `interval` | How often update data | `6h` | [1h, 6h, 1d, 3d, 7d, 1w, 1m] |
| `folder` | Local data folder where to store transacrions | `~/.pyhodl/data/` | any folder in your machine |



## API configs

`API` config is generally stored at `~home/.pyhodl/api/config.json`. A simple config file looks like
```json
[
    {
        "name": "binance",
        "key": "<my personal api key>",
        "secret": "<my personal api secret>"
    },
    {
        "name": "gdax",
        "key": "<my personal api key>",
        "secret": "<my personal api secret>",
        "passphrase": "<my personal api passhrase>"
    }
]
```

To get your personal `key`s and `secret`s please refer to [the guide](IMPORT_DATA.md).
